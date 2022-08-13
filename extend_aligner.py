import re
import os
import math
import shutil
import argparse
import subprocess

from utils.logger import getLogger
from utils.helpers import readInputFile, getTrimPeriods, readInstructions
from utils.youtube_mp3 import downloadYTmp3
from utils.regprocess import applyPreInstructions
from utils.aligners import aeneasAligner
from utils.post_process import readSRT, getValidAlignments, postProcess

def alignExtended(args):
    # assigning absolute path values
    input_path = os.path.abspath(args.input_path)
    instruction_path = os.path.abspath(args.instruction_path)
    output_path = os.path.abspath(args.output_path)
    download_path = os.path.abspath("downloads/")
    dump_path = os.path.abspath("dump/")
    log_path = os.path.abspath("aligner.log")

    logger = getLogger(log_path)

    # python script options logging
    logger.info(os.path.abspath(__file__) + " " + ' '.join(f'--{k} {v}' for k, v in vars(args).items()))

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
        # if instruction path is given and dump exists, it is assumed that the text has been pre-processed using instructions and saved to dump
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
                subcommand = ["ffmpeg", "-i", aud_paths[ind], "-ar", str(args.sampling_rate), new_aud_path]
                logger.info(f"<subprocess>: {' '.join(subcommand)}")
                subprocess.run(subcommand, capture_output=True)
            else:
                seek_time, to_time = getTrimPeriods(trim_paths[ind])
                logger.info(f"reformatting {aud_paths[ind]} to {new_aud_path} with sr {args.sampling_rate} and trim of (ss: {seek_time}) (t: {to_time})")
                subcommand = ["ffmpeg", "-ss", str(seek_time), "-i", aud_paths[ind], "-ar", str(args.sampling_rate), "-t", str(to_time),  new_aud_path]
                logger.info(f"<subprocess>: {' '.join(subcommand)}")
                subprocess.run(subcommand, capture_output=True)
            aud_paths[ind] = new_aud_path
        # cleaning and converting text to phrases
        if(args.instruction_path):
            logger.info(f"reading text pre-processing instructions from {instruction_path}")
            pre_instructions = readInstructions(instruction_path, "pre")
            logger.info(f"<regprocess>: {pre_instructions}")
            for ind in range(len(txt_paths)):
                aud_id = os.path.splitext(os.path.basename(aud_paths[ind]))[0]
                new_txt_path = os.path.join(dump_path, aud_id + ".txt")
                logger.info(f"pre-processing and phrasing {txt_paths[ind]} to {new_txt_path}")
                applyPreInstructions(pre_instructions, txt_paths[ind], new_txt_path)
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

    # post processing
    wav_path = os.path.join(output_path, "wav/")
    if(os.path.isdir(wav_path)):
        logger.warning(f"wav directory already found at {wav_path} ... skipping post processing")
    else:
        logger.info(f"creating wav directory at {wav_path}")
        os.mkdir(wav_path)
        logger.info(f"reading post-processing instructions from {instruction_path}")
        post_instructions = readInstructions(instruction_path, "post")
        # convert post processing instructions to parameter values
        post_params = {}
        for inst in post_instructions:
            if(inst[0] in ["max_length", "min_length"]):
                post_params[inst[0]] = float(inst[1])
            else:
                if(len(inst) == 1):
                    post_params[inst[0]] = ''
                else:
                    post_params[inst[0]] = inst[1]
        if(post_params["format"] not in ["kaldi"]):
            logger.error("invalid output format given - {form}".format(form=post_params["format"]))
            return
        logger.info(f"<postprocess>: {post_params}")
        # get valid alignments
        logger.info(f"getting valid alignments")
        total_alignments = []
        total_count = 0
        for ind in range(len(aud_paths)):
            srt_align = readSRT(srt_paths[ind])
            alignments = getValidAlignments(srt_align, post_params)
            total_count += len(alignments)
            total_alignments.append(alignments)
        # added parameters for post processing
        post_params["dataset_name"] = args.dataset_name
        post_params["count"] = total_count
        # start the post processing
        logger.info(f"found {total_count} total valid alignments")
        logger.info(f"starting post processing for dataset {args.dataset_name}")
        file_ctr = 1
        total_trans = ""
        for ind in range(len(aud_paths)):
            logger.info(f"post processing audio {aud_paths[ind]} and alignment {srt_paths[ind]} (files from {file_ctr} -> {file_ctr + len(total_alignments[ind]) - 1}")
            trans = postProcess(aud_paths[ind], wav_path, total_alignments[ind], post_params, file_ctr)
            file_ctr += len(total_alignments[ind])
            total_trans += trans
        transcript_path = os.path.join(output_path, "transcript.txt")
        logger.info(f"writing transcript at {transcript_path}")
        with open(transcript_path, 'w') as f:
            f.write(total_trans)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", "--input_path", help="path to the target file with format <audio_path> <text_path> [<trim_path>] (audio_path is youtube link if --from_youtube is flagged)", type=str, required=True)
    parser.add_argument("-out", "--output_path", help="path where the files will be saved", type=str, required=True)
    parser.add_argument("-instr", "--instruction_path", help="path to file with processing and phrasing instructions", type=str, required=True)
    parser.add_argument("-l", "--language", help="language of the alignment", type=str, choices=['eng', 'hin'], required=True)
    parser.add_argument("-dbn", "--dataset_name", help="name of the dataset", type=str, required=True)
    parser.add_argument("-sr", "--sampling_rate", help="sampling_rate of the resultant wav files", type=int, default=16000)
    parser.add_argument("--from_youtube", help="downloads the audio from Youtube", action="store_true")
    args = parser.parse_args()

    alignExtended(args)
