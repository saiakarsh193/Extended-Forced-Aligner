import re
import os
import math
import shutil

from aeneas.audiofile import AudioFile
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import youtube_dl

import argparse

from cleaners import cleanTextForPath
from utils import time2Frame, getPeriodsFromPath, getTimeFromText, getAlignmentsFromSRT, findEndFrame

def downloadYTmp3(link, target):
    # download 
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': target,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def getAF(path):
    # get the audio file object from the path
    adf = AudioFile(path)
    adf.read_samples_from_file()
    return adf

def subAF(oadf, sttime, entime):
    # create a new audio file which is a sub part of the original audio file
    # given the start time and end time (,)
    # get new samples from the start and end frame calculated from the input time
    stframe = time2Frame(oadf.audio_sample_rate,  sttime)
    if(entime == None):
        new_samples = oadf.audio_samples[stframe: ]
    else:
        enframe = time2Frame(oadf.audio_sample_rate, entime)
        new_samples = oadf.audio_samples[stframe: enframe]
    # create new audio file object from the new samples
    nadf = AudioFile()
    nadf.add_samples(new_samples)
    # assign sample rate to make the object functional
    nadf.audio_sample_rate = oadf.audio_sample_rate
    return nadf

def alignAeneas(audioPath, textPath, outPath, language):
    # alignment using aeneas
    # config string to Task object
    task = Task(config_string = "task_language={lang}|is_text_type=subtitles|os_task_file_format=srt".format(lang = language))
    # assigning proper paths (should be absolute)
    task.audio_file_path_absolute = os.path.abspath(audioPath)
    task.text_file_path_absolute = os.path.abspath(textPath)
    task.sync_map_file_path_absolute = os.path.abspath(outPath)
    # executing the alignment
    ExecuteTask(task).execute()
    # saving the output file
    task.output_sync_map_file()

def chunkAudioFromSRT(audiopath, srtpath, outpath, ctr=1):
    # get text and alignments
    data = getAlignmentsFromSRT(srtpath)
    oadf = getAF(audiopath)
    for frag in data:
        # extract the sub audio part
        nadf = subAF(oadf, frag[1], frag[2])
        # save the audio file
        nadf.write(outpath + "/{counter}.mp3".format(counter=ctr))
        # save the text file
        with open(outpath + "/{counter}.txt".format(counter=ctr), 'w') as f:
            f.write(frag[0])
        ctr += 1
    return ctr

def alignExtended(args):
    # temporary directory
    if(os.path.isdir(args.temp_path)):
        print(f"error... temporary directory ({args.temp_path}) already exists. Please remove the directory and run again")
        return
    print(f"creating temporary directory ({args.temp_path})")
    os.mkdir(args.temp_path)

     # create output directory if not already present
    if(not os.path.isdir(args.output_path)):
        print(f"creating output directory ({args.output_path})")
        os.mkdir(args.output_path)

    if(args.from_youtube):
        # reading the youtube link from the audio path
        with open(args.audio_path, 'r') as f:
            ytlink = f.read().strip()
        # downloading source audio from youtube
        print("downloading raw_audio from youtube link ({lnk})".format(lnk=ytlink))
        ralink = args.temp_path + "/raw_audio.mp3"
        downloadYTmp3(ytlink, ralink)
    else:
        ralink = args.audio_path

    # get raw audio
    print("reading raw_audio")
    raw_audio = getAF(ralink)

    # main start time, main end time: interval for the main audio from the total raw file
    if(args.period_path.lower in ['', 'none']):
        msttime, mentime = (0, 0), None
    else:
        msttime, mentime = getPeriodsFromPath(args.period_path)

    # trim raw audio
    print("trimming raw_audio into trim_audio using period {sttime} --> {entime}".format(sttime=msttime, entime=mentime))
    trim_audio = subAF(raw_audio, msttime, mentime)

    if(args.from_youtube):
        # removing raw audio
        print("removing raw_audio downloaded from youtube")
        os.remove(ralink)

    # save trimmed audio
    print("writing trim_audio")
    trim_audio.write(args.temp_path + "/trim_audio.mp3")

    # reading again to populate properties
    trim_audio = getAF(args.temp_path + "/trim_audio.mp3")
    print("trim_audio length:", trim_audio.audio_length)

    # each segment length <= 5 min (300 seconds)
    segment_count = math.ceil(trim_audio.audio_length / 300)
    print("segment count:", segment_count)

    # cleaning and writing raw text
    print("cleaning raw_text")
    print("writing clean_text")
    cleanTextForPath(args.text_path, args.temp_path + "/clean_text.txt", args.language, args.transcript_youtube)

    # path holders
    audio_path = args.temp_path + "/trim_audio.mp3"
    text_path = args.temp_path + "/clean_text.txt"
    align_path = args.temp_path + "/aligned_text.srt"
    audseg_path = args.temp_path + "/seg.mp3"
    srtseg_path = args.temp_path + "/seg.srt"

    # file counter name starting value
    fctr = args.start_count

    for seg in range(1, segment_count + 1):
        print(f"*****segment {seg}*****")

        # aligning the remaining text and remaining audio to get aligned segment
        print("aligning audio and text file")
        alignAeneas(audio_path, text_path, align_path, args.language)

        # extracting the srt data to find the end frame
        split_srt = getAlignmentsFromSRT(align_path)
        endframe = findEndFrame(split_srt, 5)
        endtime = split_srt[endframe - 1][2]

        # saving the audio
        print("writing segment audio")
        oadf = getAF(audio_path)
        nadf = subAF(oadf, (0, 0), endtime)
        nadf.write(audseg_path)

        # cleaning the temp_align and writing srt file
        print("writing segment srt")
        with open(align_path, 'r') as f:
            tmp_data = f.readlines()
        tmp_str = "".join(tmp_data[: endframe * 4])
        with open(srtseg_path, 'w') as f:
            f.write(tmp_str)

        # chunking the current segment into the individual aligned files
        print("chunking segment")
        fctr = chunkAudioFromSRT(audseg_path, srtseg_path, args.output_path, fctr)

        # updating the audio file and text file
        print("updating audio and text file")
        nadf = subAF(oadf, endtime, None)
        nadf.write(audio_path)

        with open(text_path, 'r') as f:
            tmp_data = f.readlines()
        tmp_str = "".join(tmp_data[endframe * 2: ])
        with open(text_path, 'w') as f:
            f.write(tmp_str)
        
        # if the file is empty (threshold of 5) due to incorrect prediction of segment count then we stop loop
        if(len(tmp_str) < 5):
            segment_count = seg
            break

    # remove temporary directory
    print("removing temporary directory")
    shutil.rmtree(args.temp_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_path", help="path to the audio file (or text file containing the link of video if --from_youtube is flagged)", type=str)
    parser.add_argument("text_path", help="path to the text file", type=str)
    parser.add_argument("period_path", help="path to the file containing the trim information of the audio", type=str)
    parser.add_argument("language", help="language of the alignment", type=str, choices=['eng', 'hin'])
    parser.add_argument("-sc", "--start_count", help="starting value for the file names to be saved", type=int, default=1)
    parser.add_argument("-out", "--output_path", help="path where the files will be saved", type=str, default="output")
    parser.add_argument("-temp", "--temp_path", help="path for the temporary directory", type=str, default="temp")
    parser.add_argument("--from_youtube", help="downloads the audio from Youtube", action="store_true")
    parser.add_argument("--transcript_youtube", help="extra parsing for direct youtube trascript", action="store_true")
    args = parser.parse_args()

    alignExtended(args)
