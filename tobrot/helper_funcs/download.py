#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) gautamajay52 | Shrimadhav U K

# the logging things
import logging

from tobrot.helper_funcs.utils import sanitize_text, getMediaAttributes, sanitize_file_name

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)
#

import asyncio
import math
import os
import time
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from pathlib import Path

from tobrot import (
    DOWNLOAD_LOCATION,
    UPLOAD_TO_CLOUD_WHEN_RENAME
)
from tobrot.helper_funcs.display_progress_g import progress_for_pyrogram_g
from tobrot.helper_funcs.upload_to_tg import upload_to_gdrive
from tobrot.helper_funcs.download_aria_p_n import call_apropriate_function_t
from tobrot.helper_funcs.create_compressed_archive import unzip_me, unrar_me, untar_me


async def down_load_media_f(client, message):
    user_id = message.from_user.id
    print(user_id)
    mess_age = await message.reply_text("...", quote=True)
    # raise ValueError("test")
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
    if message.reply_to_message is not None:
        start_t = datetime.now()
        file_name = None
        media_attr = await getMediaAttributes(message.reply_to_message)
        if media_attr is not None and media_attr.file_name is not None:
            file_name = await sanitize_file_name(media_attr.file_name)
        if len(message.command) > 1:
            txt = " ".join(message.command)
            if txt.find("rename") > -1 and len(txt[txt.find("rename") + 7:]) > 0:
                file_name = txt[txt.find("rename") + 7:]
                file_name = await sanitize_file_name(file_name)
                file_name = await sanitize_text(file_name)
            if media_attr is not None and media_attr.file_name is not None:
                file_name = file_name+Path(media_attr.file_name).suffix
        if file_name is None:
            file_name = ""

        download_location = DOWNLOAD_LOCATION + "/" + file_name
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram_g,
            progress_args=(
                "trying to download", mess_age, c_time
            )
        )
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        print(the_real_download_location)
        await asyncio.sleep(10)
        await mess_age.edit_text(f"Downloaded to <code>{the_real_download_location}</code> in <u>{ms}</u> seconds")
        gk = subprocess.Popen(['mv', f'{the_real_download_location}', '/app/'], stdout=subprocess.PIPE)
        out = gk.communicate()
        the_real_download_location_g = os.path.basename(the_real_download_location)
        if len(message.command) > 1:
            txt = " ".join(message.command)
            if message.command[1] == "unzip":
                file_upload = await unzip_me(the_real_download_location_g)
            elif message.command[1] == "unrar":
                file_upload = await unrar_me(the_real_download_location_g)
            elif message.command[1] == "untar":
                file_upload = await untar_me(the_real_download_location_g)
            else:
                file_upload = the_real_download_location_g

            if file_upload is not None and message.command[0] not in ['split', 'rename']:
                g_response = await upload_to_gdrive(file_upload, mess_age, message, user_id)
                LOGGER.info(g_response)
            elif message.command[0] == 'rename' and f"{UPLOAD_TO_CLOUD_WHEN_RENAME}".strip() == "Y":
                g_response = await upload_to_gdrive(file_upload, mess_age, message, user_id)
                LOGGER.info(g_response)
        else:
            gaut_response = await upload_to_gdrive(the_real_download_location_g, mess_age, message, user_id)
            LOGGER.info(gaut_response)
    else:
        # await asyncio.sleep(4)
        await mess_age.edit_text("Reply to a Telegram Media, to upload to the Cloud Drive.")

    return file_upload
