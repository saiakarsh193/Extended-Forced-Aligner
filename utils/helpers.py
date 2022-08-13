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

def readInstructions(path, part):
    if(part == "pre"):
        command_list = {
                'convert': 2,
                'remove': 1,
                'replace': 2,
                'final_format': 0,
                }
    elif(part == "post"):
        command_list = {
                'segment_wav': 0,
                'min_length': 1,
                'max_length': 1,
                'format': 1,
                }
    else:
        raise Exception("invalid type {pre, post}")
    with open(path, 'r') as f:
        rinst = f.readlines()
    in_post = False
    cinst = []
    ucomms = set()
    for ind, inst in enumerate(rinst, start=1):
        inst = inst.strip()
        if(not inst or inst[0] == '#'):
            continue
        elif(inst[0] == '!'):
            in_post = True
        else:
            if((part == "pre" and not in_post) or (part == "post" and in_post)):
                inst = inst.split()
                assert inst[0] in command_list, f"command not found at line {lno}"
                assert len(inst) - 1 == command_list[inst[0]], f"invalid number of arguments for command \"{inst[0]}\" at line {lno}"
                cinst.append(inst)
                ucomms.add(inst[0])
    if(part == "pre"):
        required = ["final_format"]
    else:
        required = ["segment_wav", "format"]
    for rcom in required:
        assert rcom in ucomms, f"command {rcom} is required for {part}-processing"
    return cinst

