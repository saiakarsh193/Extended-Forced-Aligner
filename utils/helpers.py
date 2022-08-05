import os

def readInputFile(path, from_youtube):
    with open(path, 'r') as f:
        rlines = f.readlines()
    splines = [line.split() for line in rlines]
    aud_paths, txt_paths, trim_paths = [], [], []
    parent_dir = os.path.dirname(path)
    for ind, line in enumerate(splines):
        if(len(line) not in [2, 3]):
            raise Exception(f"Invalid parameter count: given {len(line)} parameter(s) at line {ind + 1} in {path}")
        if(from_youtube):
            aud_paths.append(line[0])
        else:
            aud_paths.append(os.path.join(parent_dir, line[0]))
        txt_paths.append(os.path.join(parent_dir, line[1]))
        if(len(line) == 2):
            trim_paths.append("<no_trim>")
        else:
            trim_paths.append(os.path.join(parent_dir, line[2]))
    return aud_paths, txt_paths, trim_paths

def getTrimPeriods(path):
    # look at https://stackoverflow.com/questions/46508055/using-ffmpeg-to-cut-audio-from-to-position
    # for understanding the trim conversion for ffmpeg
    with open(path, 'r') as f:
        data = f.readlines()
    k1 = data[0].strip().split(" ")
    sm, ss = (int(k1[0]), int(k1[1]))
    k2 = data[1].strip().split(" ")
    em, es = (int(k2[0]), int(k2[1]))
    seek_time = sm * 60 + ss
    to_time = em * 60 + es
    return seek_time, to_time - seek_time

def getAlignmentsFromSRT(path):
    with open(path, 'r') as f:
        text = f.read()
    text = text.split("\n\n")
    data = []
    for frag in text:
        if(len(frag) == 0):
            continue
        frag = frag.split("\n")
        sent = frag[2]
        frag = frag[1].split(" --> ")
        data.append([sent, getTimeFromText(frag[0]), getTimeFromText(frag[1])])
    return data
