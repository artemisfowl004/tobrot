#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
import math

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

import asyncio
import os
import time
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from tobrot import (
    MAX_TG_SPLIT_FILE_SIZE
)


async def split_large_files(input_file):
    working_directory = os.path.dirname(os.path.abspath(input_file))
    new_working_directory = os.path.join(
        working_directory,
        str(time.time())
    )
    # create download directory, if not exist
    if not os.path.isdir(new_working_directory):
        os.makedirs(new_working_directory)
    # if input_file.upper().endswith(("MKV", "MP4", "WEBM", "MP3", "M4A", "FLAC", "WAV")):
    """The below logic is DERPed, so removing temporarily
    """
    if False:
        # handle video / audio files here
        metadata = extractMetadata(createParser(input_file))
        total_duration = 0
        if metadata.has("duration"):
            total_duration = metadata.get('duration').seconds
        # proprietary logic to get the seconds to trim (at)
        LOGGER.info(total_duration)
        total_file_size = os.path.getsize(input_file)
        LOGGER.info(total_file_size)
        minimum_duration = (total_duration / total_file_size) * (MAX_TG_SPLIT_FILE_SIZE)
        LOGGER.info(minimum_duration)
        # END: proprietary
        start_time = 0
        end_time = minimum_duration
        base_name = os.path.basename(input_file)
        input_extension = base_name.split(".")[-1]
        LOGGER.info(input_extension)
        i = 0
        while end_time < total_duration:
            LOGGER.info(i)
            parted_file_name = ""
            parted_file_name += str(i).zfill(5)
            parted_file_name += str(base_name)
            parted_file_name += "_PART_"
            parted_file_name += str(start_time)
            parted_file_name += "."
            parted_file_name += str(input_extension)
            output_file = os.path.join(new_working_directory, parted_file_name)
            LOGGER.info(output_file)
            LOGGER.info(await cult_small_video(
                input_file,
                output_file,
                str(start_time),
                str(end_time)
            ))
            start_time = end_time
            end_time = end_time + minimum_duration
            i = i + 1
    else:
        # handle normal files here
        o_d_t = os.path.join(
            new_working_directory,
            os.path.basename(input_file)
        )
        o_d_t = o_d_t + "."
        file_genertor_command = [
            "split",
            "--numeric-suffixes=1",
            "--suffix-length=5",
            f"--bytes={MAX_TG_SPLIT_FILE_SIZE}",
            input_file,
            o_d_t
        ]
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
    return new_working_directory


async def cult_small_video(video_file, out_put_file_name, start_time, end_time):
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        "-c",
        "copy",
        "-map",
        "0",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(t_response)
    return out_put_file_name


async def split_file_to_parts_or_by_start_end_seconds(message, input_file, no_of_parts, start_seconds, end_seconds):
    working_directory = os.path.dirname(os.path.abspath(input_file))
    new_working_directory = os.path.join(
        working_directory,
        str(time.time())
    )
    # create download directory, if not exist
    if not os.path.isdir(new_working_directory):
        os.makedirs(new_working_directory)
    if input_file.upper().endswith(("MKV", "MP4", "WEBM", "MP3", "M4A", "FLAC", "WAV")):
        # handle video / audio files here
        metadata = extractMetadata(createParser(input_file))
        total_duration = 0
        if metadata.has("duration"):
            total_duration = metadata.get('duration').seconds
        # proprietary logic to get the seconds to trim (at)
        LOGGER.info(total_duration)
        total_file_size = os.path.getsize(input_file)
        LOGGER.info(total_file_size)
        base_name = os.path.basename(input_file)
        input_extension = base_name.split(".")[-1]
        file_name_without_extension= base_name.replace(f".{input_extension}","")
        if no_of_parts is None:
            if total_duration >= end_seconds:
                output_file = os.path.join(new_working_directory, f'{file_name_without_extension}_SAMPLE.{input_extension}')
                LOGGER.info(await cult_small_video(
                    input_file,
                    output_file,
                    str(start_seconds),
                    str(end_seconds)
                ))
            else:
                await message.reply_text("given end timestamp is out of range of actual video runtime")
                return None
        else:
            duration_per_part = math.floor(total_duration / no_of_parts)
            LOGGER.info(duration_per_part)
            # END: proprietary
            start_time = 0
            end_time = duration_per_part

            LOGGER.info(input_extension)
            i = 0
            while end_time < total_duration+2:
                LOGGER.info(f'part - {i},starttime={start_time},endtime={end_time}')
                parted_file_name = ""
                parted_file_name += str(file_name_without_extension)
                parted_file_name += "_PART_"
                parted_file_name += str(i).zfill(3)
                parted_file_name += "."
                parted_file_name += str(input_extension)
                output_file = os.path.join(new_working_directory, parted_file_name)
                LOGGER.info(output_file)
                LOGGER.info(await cult_small_video(
                    input_file,
                    output_file,
                    str(start_time),
                    str(end_time)
                ))
                start_time = end_time
                end_time = end_time + duration_per_part
                i = i + 1
    return new_working_directory
