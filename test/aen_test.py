import os

from aeneas.audiofile import AudioFile
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from utils.post_process import readSRT, getValidAlignments, postProcess

def aeneasAligner(audioPath, textPath, outPath, conf_str):
    # alignment using aeneas
    # config string to Task object
    task = Task(config_string = conf_str)
    # assigning proper paths (should be absolute)
    task.audio_file_path_absolute = os.path.abspath(audioPath)
    task.text_file_path_absolute = os.path.abspath(textPath)
    task.sync_map_file_path_absolute = os.path.abspath(outPath)
    # executing the alignment
    ExecuteTask(task).execute()
    # saving the output file
    task.output_sync_map_file()

conf_str = "task_language=hin|is_text_type=subtitles|os_task_file_format=srt|dtw_margin=100" #|window_shift=0.060"
outdir = "/home/saiakarsh/Desktop/Extended-Forced-Aligner/tmp"

# fname = "3pz_2qrBLTk"
fname = "OW7UgtpF104"
audioPath = f"/home/saiakarsh/Desktop/Extended-Forced-Aligner/egs/nmhin/dump/{fname}.wav"
textPath = f"/home/saiakarsh/Desktop/Extended-Forced-Aligner/egs/nmhin/dump/{fname}.txt"

outPath = os.path.join(outdir, "out_val.srt")
wavPath = os.path.join(outdir, "wav/")
tranPath = os.path.join(outdir, "transcript.txt")
os.mkdir(outdir)
os.mkdir(wavPath)

print("aligning")
aeneasAligner(audioPath, textPath, outPath, conf_str)

post_params = {'segment_wav': '', 'min_length': 2.5, 'max_length': 15.0, 'format': 'kaldi'} 

alignments = readSRT(outPath)
total_count = len(alignments)
post_params["dataset_name"] = "aen_tst"
post_params["count"] = total_count
print(post_params)

trans = postProcess(audioPath, wavPath, alignments, post_params, 1)
with open(tranPath, 'w') as f:
    f.write(trans)
