import scipy
import numpy as np
import os

def readSRT(path):
    with open(path, 'r') as f:
        raw_lines = f.readlines()
    sdata = []
    for i in range(0, len(raw_lines), 4):
        sdata.append((extractTime(raw_lines[i + 1].strip()), raw_lines[i + 2].strip()))
    return sdata

def extractTime(tstr):
    sptstr = tstr.split(" --> ")
    convstime = lambda val: (int(val[0:2]) * 3600) + (int(val[3:5]) * 60) + (int(val[6:8]) * 1) + (int(val[9:]) / 1000)
    return convstime(sptstr[0]), convstime(sptstr[1])

def getValidAlignments(align, params):
    alignments = []
    for cur in align:
        (st_time, en_time), utt = cur
        wdur = en_time - st_time
        if(("min_length" in params and wdur < params["min_length"]) or ("max_length" in params and wdur > params["max_length"])):
            continue
        alignments.append(cur)
    return alignments 

def postProcess(inp_path, out_path, align, params, start_ind=1):
    fs, y = scipy.io.wavfile.read(inp_path)
    # 2D numpy stereo wav audio to 1D numpy mono wav audio
    y = y.mean(axis=1, dtype=np.int16)
    trans = ""
    scnt = len(str(params["count"]))
    for (st_time, en_time), utt in align:
        st_frame = int(fs * st_time)
        en_frame = int(fs * en_time)
        cur_name = getName(str(start_ind), scnt, params["dataset_name"])
        trans += getTrans(cur_name, utt, params["format"]) + "\n"
        cur_path = os.path.join(out_path, cur_name + ".wav")
        scipy.io.wavfile.write(cur_path, fs, y[st_frame: en_frame + 1])
        start_ind += 1
    return trans

def getTrans(cur_name, utt, form):
    if(form == "kaldi"):
        return "( " + cur_name + " \" " + utt + " \" )"

def getName(val, cnt, prefix):
    return prefix + "_" + val.rjust(cnt, '0')
