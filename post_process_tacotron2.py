import subprocess
from pydub import AudioSegment
from tqdm import tqdm

def getFileCount(path):
    cmd = "ls -lav " + path + " | tail -1"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    spout = output.split()
    flast = int(spout[-1][:spout[-1].find(b'.')])
    return flast

def trimSilence(path, outpath, silence_threshold=-50.0, chunk_size=10, sampling_rate=22050):
    assert chunk_size > 0
    subprocess.run(["ffmpeg", "-i", path, "-ar", str(sampling_rate), outpath], capture_output=True)
    sound = AudioSegment.from_file(outpath, format="wav")
    trimmed_sound = sound
    duration = len(sound)
    ltrim_ms = 0
    while sound[ltrim_ms: ltrim_ms + chunk_size].dBFS < silence_threshold and ltrim_ms < duration:
        ltrim_ms += chunk_size
    rsound = sound.reverse()
    rtrim_ms = 0
    while rsound[rtrim_ms: rtrim_ms + chunk_size].dBFS < silence_threshold and rtrim_ms < duration:
        rtrim_ms += chunk_size
    trimmed_sound = sound[ltrim_ms: duration - rtrim_ms]
    trimmed_sound.export(outpath, format="wav")

def formatText(path, apath):
    with open(path, 'r') as f:
        text = f.read().strip()
    text += "" if text[-1] == "." else "."
    ntext = apath + "|" + text
    return ntext

def processFiles(src, taraud, tartext):
    # count here refers to the number of files (index) to be processed from the src directory
    count = getFileCount(src)
    # src directory has both index.mp3 (audio) and index.txt (transcript)
    sent = ""
    for i in tqdm(range(1, 1 + count)):
        trimSilence(src + "/{filno}.mp3".format(filno=i), taraud + "/{filno}.wav".format(filno=i), -30)
        sent += formatText(src + "/{filno}.txt".format(filno=i), taraud + "/{filno}.wav".format(filno=i)) + "\n"
    with open(tartext, 'w') as f:
        f.write(sent[: -1])

# specific post processing unit for tacotron2 input

processFiles("output", "wavs", "filelists/all_filelist.txt")

