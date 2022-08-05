import scipy
import numpy as np

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

def subdivideWav(wav_path, convstr, start=1):
    fs, y = scipy.io.wavfile.read(wav_path)
    y = y.mean(axis=1, dtype=np.int16)
    return
