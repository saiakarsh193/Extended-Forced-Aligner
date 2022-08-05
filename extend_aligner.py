import re
import os
import math
import shutil
import argparse
import subprocess

from utils.logger import getLogger
from utils.helpers import readInputFile, getTrimPeriods
from utils.youtube_mp3 import downloadYTmp3
from utils.regprocess import readInstructions, applyInstructions
from utils.aligners import aeneasAligner
from utils.post_process import readSRT, subdivideWav

def alignExtended(args):
    # assigning absolute path values
    input_path = os.path.abspath(args.input_path)
    output_path = os.path.abspath(args.output_path)
    download_path = os.path.abspath("downloads/")
    dump_path = os.path.abspath("dump/")
    log_path = os.path.abspath("aligner.log")

    logger = getLogger(log_path)

    # check for file at path
    if(not os.path.isfile(input_path)):
        logger.error(f"{input_path} cannot be found")
        return

    # get the paths from input text
    logger.info(f"reading input file {input_path} and extracting paths")
    aud_paths, txt_paths, trim_paths = readInputFile(input_path, args.from_youtube)

    # download videos to youtube if --from_youtube is flagged
    if(args.from_youtube):
        logger.info(f"youtube download enabled")
        aud_ids = []
        for aud_link in aud_paths:
            aud_ids.append(aud_link[aud_link.rfind("/") + 1:])
        if(os.path.isdir(download_path)):
            logger.warning(f"downloads directory already found at {download_path} ... skipping youtube download")
            if(not os.path.isfile(os.path.join(download_path, "download.done"))):
                logger.error(f"downloads directory has incomplete downloads")
                logger.warning(f"deleting {download_path} for fresh start")
                shutil.rmtree(download_path)
        # not else condition because the else part of the previous block can delete the download directory
        if(not os.path.isdir(download_path)):
            logger.info(f"creating download directory at {download_path}")
            os.mkdir(download_path)
            for ind, aud_link in enumerate(aud_paths):
                new_aud_path = os.path.join(download_path, f"{aud_ids[ind]}.mp3")
                downloadYTmp3(aud_link, new_aud_path)
            logger.info(f"download completed")
            with open(os.path.join(download_path, "download.done"), 'w') as f:
                pass
        for ind in range(len(aud_paths)):
            aud_paths[ind] = os.path.join(download_path, f"{aud_ids[ind]}.mp3")

    # reformatting and phrase convertion
    if(os.path.isdir(dump_path)):
        logger.warning(f"dump directory already found at {dump_path} ... skipping reformatting")
        for ind in range(len(aud_paths)):
            aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
            new_aud_path = os.path.join(dump_path, f"{aud_id}.wav")
            aud_paths[ind] = new_aud_path
        if(args.instruction_path):
            for ind in range(len(txt_paths)):
                aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
                new_txt_path = os.path.join(dump_path, aud_id + ".txt")
                txt_paths[ind] = new_txt_path
    else:
        logger.info(f"creating dump directory at {dump_path}")
        os.mkdir(dump_path)
        # reformatting and trimming audio files
        for ind in range(len(aud_paths)):
            aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
            new_aud_path = os.path.join(dump_path, f"{aud_id}.wav")
            if(trim_paths[ind] == "<no_trim>"):
                logger.info(f"reformatting {aud_paths[ind]} to {new_aud_path} with sr {args.sampling_rate}")
                subprocess.run(["ffmpeg", "-i", aud_paths[ind], "-ar", str(args.sampling_rate), new_aud_path], capture_output=True)
            else:
                seek_time, to_time = getTrimPeriods(trim_paths[ind])
                logger.info(f"reformatting {aud_paths[ind]} to {new_aud_path} with sr {args.sampling_rate} and trim of (ss: {seek_time}) (t: {to_time})")
                subprocess.run(["ffmpeg", "-ss", str(seek_time), "-i", aud_paths[ind], "-ar", str(args.sampling_rate), "-t", str(to_time),  new_aud_path], capture_output=True)
            aud_paths[ind] = new_aud_path
        # cleaning and converting text to phrases
        if(args.instruction_path):
            instruction_path = os.path.abspath(args.instruction_path)
            logger.info(f"reading text pre-processing instructions at {instruction_path}")
            parse_instructions = readInstructions(instruction_path)
            for ind in range(len(txt_paths)):
                aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
                new_txt_path = os.path.join(dump_path, aud_id + ".txt")
                logger.info(f"pre-processing and phrasing {txt_paths[ind]} to {new_txt_path}")
                applyInstructions(parse_instructions, txt_paths[ind], new_txt_path)
                txt_paths[ind] = new_txt_path

    # alignment
    srt_paths = []
    if(os.path.isdir(output_path)):
        logger.warning(f"output directory already found at {output_path} ... skipping alignment")
        for ind in range(len(aud_paths)):
            aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
            srt_path = os.path.join(output_path, aud_id + ".srt")
            srt_paths.append(srt_path)
    else:
        logger.info(f"creating output directory at {output_path}")
        os.mkdir(output_path)
        conf_str = f"task_language={args.language}|is_text_type=subtitles|os_task_file_format=srt"
        logger.info(f"starting alignment using Aeneas with config \"{conf_str}\"")
        for ind in range(len(aud_paths)):
            aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
            srt_path = os.path.join(output_path, aud_id + ".srt")
            logger.info(f"aligning audio {aud_paths[ind]} with transcript {txt_paths[ind]} to {srt_path}")
            aeneasAligner(aud_paths[ind], txt_paths[ind], srt_path, conf_str)
            srt_paths.append(srt_path)
            break

    # post processing
    for ind in range(len(aud_paths)):
        convsrt = readSRT(srt_paths[ind])
        subdivideWav(aud_paths[ind], convsrt)
        break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", "--input_path", help="path to the target file with format <audio_path> <text_path> [<trim_path>] (audio_path is youtube link if --from_youtube is flagged)", type=str, required=True)
    parser.add_argument("-out", "--output_path", help="path where the files will be saved", type=str, required=True)
    parser.add_argument("-instr", "--instruction_path", help="path to file with processing and phrasing instructions", type=str, required=True)
    parser.add_argument("-l", "--language", help="language of the alignment", type=str, choices=['eng', 'hin'], required=True)
    parser.add_argument("-sr", "--sampling_rate", help="sampling_rate of the resultant wav files", type=int, default=16000)
    parser.add_argument("--from_youtube", help="downloads the audio from Youtube", action="store_true")
    args = parser.parse_args()

    alignExtended(args)
