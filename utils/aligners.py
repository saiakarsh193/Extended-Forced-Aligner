import os

from aeneas.audiofile import AudioFile
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

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

