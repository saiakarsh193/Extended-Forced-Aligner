def time2Frame(audio_rate, rtime):
    seconds = rtime[0] * 60 + rtime[1]
    return int(audio_rate * seconds)

def getPeriodsFromPath(path):
    with open(path, 'r') as f:
        data = f.readlines()
    k1 = data[0].strip().split(" ")
    k2 = data[1].strip().split(" ")
    return (int(k1[0]), int(k1[1])), (int(k2[0]), int(k2[1]))

def getTimeFromText(text):
    m = text[3:5]
    s = text[6:8] + "." + text[9:]
    return (int(m), float(s))

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

def findEndFrame(split_srt, minu):
    for ind, tp in enumerate(split_srt, start=1):
        if(tp[2][0] >= minu):
            return ind
    return ind

