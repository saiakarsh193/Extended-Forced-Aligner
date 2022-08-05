import re

def readInstructions(path):
    with open(path, 'r') as f:
        rinst = f.readlines()
    sinst = [inst.split() for inst in rinst]
    cinst = []
    for inst in sinst:
        if(not(not inst or inst[0][0] == '#')):
            cinst.append(inst)
    command_list = {
            'convert': 2,
            'remove': 1,
            'replace': 2,
            'final_format': 0,
            }
    for lno, inst in enumerate(cinst, start=1):
        assert inst[0] in command_list, f"command not found at line {lno}"
        assert len(inst) - 1 == command_list[inst[0]], f"invalid number of arguments for command \"{inst[0]}\" at line {lno}"
    return cinst

def applyInstructions(instructions, file_path, out_path):
    with open(file_path, 'r') as f:
        rtxt = f.read()
    for inst in instructions:
        if(inst[0] == 'convert'):
            pass
        elif(inst[0] == 'remove'):
            if(inst[1] == '{english}'):
                rtxt = re.sub(r"[0-9a-zA-Z]", "", rtxt, 0, re.MULTILINE)
            elif(inst[1] == '{symbols}'):
                rtxt = re.sub(r"[-_.,?!\"\'\“\”\’\‘]", "", rtxt, 0, re.MULTILINE)
            elif(inst[1] == '{fill_spaces}'):
                rtxt = re.sub(r" {2,}", " ", rtxt, 0, re.MULTILINE)
        elif(inst[0] == 'replace'):
            if(inst[2] == '<space>'):
                rtxt = re.sub(inst[1], " ", rtxt, 0, re.MULTILINE)
            elif(inst[2] == '<period>'):
                rtxt = re.sub(inst[1], "<period>", rtxt, 0, re.MULTILINE)
        elif(inst[0] == 'final_format'):
            rtxt = re.sub("<period>", "\n", rtxt, 0, re.MULTILINE)
            rtxt = rtxt.split("\n")
            ntxt = []
            for ltxt in rtxt:
                ltxt = ltxt.strip()
                if(len(ltxt) > 0):
                    ntxt.append(ltxt)
            rtxt = '\n\n'.join(ntxt)
    with open(out_path, 'w') as f:
        f.write(rtxt)
