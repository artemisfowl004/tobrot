#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | gautamajay52 | Akshay C

# the logging things
import datetime
import logging

from tobrot.helper_funcs import utils
from tobrot.helper_funcs.gplink_generator import generate_gp_link
from tobrot.helper_funcs.split_large_files import split_file_to_parts_or_by_start_end_seconds
from tobrot.helper_funcs.upload_to_tg import upload_to_tg
from tobrot.helper_funcs.utils import sanitize_file_name, sanitize_text

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

import os
import requests

from tobrot import (
    DOWNLOAD_LOCATION,
    SPLIT_COMMAND,
    RENAME_COMMAND,
    GP_LINKS_COMMAND,
    TG_MAX_FILE_SIZE)

import time
import aria2p
import asyncio
from tobrot.helper_funcs.extract_link_from_message import extract_link
from tobrot.helper_funcs.download_aria_p_n import call_apropriate_function, call_apropriate_function_g, aria_start
from tobrot.helper_funcs.download_from_link import request_download
from tobrot.helper_funcs.display_progress import progress_for_pyrogram
from tobrot.helper_funcs.youtube_dl_extractor import extract_youtube_dl_formats
from tobrot.helper_funcs.admin_check import AdminCheck
from tobrot.helper_funcs.ytplaylist import yt_playlist_downg
from tobrot.helper_funcs.download import down_load_media_f


async def incoming_purge_message_f(client, message):
    """/purge command"""
    i_m_sefg2 = await message.reply_text("Purging...", quote=True)
    if await AdminCheck(client, message.chat.id, message.from_user.id):
        aria_i_p = await aria_start()
        # Show All Downloads
        downloads = aria_i_p.get_downloads()
        for download in downloads:
            LOGGER.info(download.remove(force=True))
    await i_m_sefg2.delete()


async def incoming_message_f(client, message):
    """/leech command"""
    i_m_sefg = await message.reply_text("processing", quote=True)
    is_zip = False
    is_unzip = False
    is_unrar = False
    is_untar = False
    if len(message.command) > 1:
        if message.command[1] == "archive":
            is_zip = True
        elif message.command[1] == "unzip":
            is_unzip = True
        elif message.command[1] == "unrar":
            is_unrar = True
        elif message.command[1] == "untar":
            is_untar = True
    # get link from the incoming message
    dl_url, cf_name, _, _ = await extract_link(message.reply_to_message, "LEECH")
    LOGGER.info(dl_url)
    LOGGER.info(cf_name)
    if dl_url is not None:
        await i_m_sefg.edit_text("extracting links")
        # start the aria2c daemon
        aria_i_p = await aria_start()
        LOGGER.info(aria_i_p)
        current_user_id = message.from_user.id
        # create an unique directory
        new_download_location = os.path.join(
            DOWNLOAD_LOCATION,
            str(current_user_id),
            str(time.time())
        )
        # create download directory, if not exist
        if not os.path.isdir(new_download_location):
            os.makedirs(new_download_location)
        await i_m_sefg.edit_text("trying to download")
        # try to download the "link"
        sagtus, err_message = await call_apropriate_function(
            aria_i_p,
            dl_url,
            new_download_location,
            i_m_sefg,
            is_zip,
            cf_name,
            is_unzip,
            is_unrar,
            is_untar,
            message
        )
        if not sagtus:
            # if FAILED, display the error message
            await i_m_sefg.edit_text(err_message)
    else:
        await i_m_sefg.edit_text(
            "**FCUK**! wat have you entered. \nPlease read /help \n"
            f"<b>API Error</b>: {cf_name}"
        )


#
async def incoming_gdrive_message_f(client, message):
    """/gleech command"""
    i_m_sefg = await message.reply_text("processing", quote=True)
    is_zip = False
    is_unzip = False
    is_unrar = False
    is_untar = False
    if len(message.command) > 1:
        if message.command[1] == "archive":
            is_zip = True
        elif message.command[1] == "unzip":
            is_unzip = True
        elif message.command[1] == "unrar":
            is_unrar = True
        elif message.command[1] == "untar":
            is_untar = True
    txt = " ".join(message.command)
    c_file_name = None
    if txt.find("rename") > -1 and len(txt[txt.find("rename") + 7:]) > 0:
        c_file_name = txt[txt.find("rename") + 7:]
        c_file_name = await sanitize_file_name(c_file_name)
        c_file_name = await sanitize_text(c_file_name)
    # get link from the incoming message
    dl_url, cf_name, _, _ = await extract_link(message.reply_to_message, "GLEECH")
    LOGGER.info(dl_url)
    LOGGER.info(cf_name)
    if cf_name is None and c_file_name is not None:
        cf_name = c_file_name
    if dl_url is not None:
        await i_m_sefg.edit_text("extracting links")
        # start the aria2c daemon
        aria_i_p = await aria_start()
        LOGGER.info(aria_i_p)
        current_user_id = message.from_user.id
        # create an unique directory
        new_download_location = os.path.join(
            DOWNLOAD_LOCATION,
            str(current_user_id),
            str(time.time())
        )
        # create download directory, if not exist
        if not os.path.isdir(new_download_location):
            os.makedirs(new_download_location)
        await i_m_sefg.edit_text("trying to download")
        # try to download the "link"
        downloaded_file = await call_apropriate_function_g(
            aria_i_p,
            dl_url,
            new_download_location,
            i_m_sefg,
            is_zip,
            cf_name,
            is_unzip,
            is_unrar,
            is_untar,
            message
        )
        return downloaded_file
    else:
        await i_m_sefg.edit_text(
            "**FCUK**! wat have you entered. \nPlease read /help \n"
            f"<b>API Error</b>: {cf_name}"
        )


async def incoming_youtube_dl_f(client, message):
    """ /ytdl command """
    i_m_sefg = await message.reply_text("processing", quote=True)
    # LOGGER.info(message)
    # extract link from message
    dl_url, cf_name, yt_dl_user_name, yt_dl_pass_word = await extract_link(
        message.reply_to_message, "YTDL"
    )
    LOGGER.info(dl_url)
    # if len(message.command) > 1:
    # if message.command[1] == "gdrive":
    # with open('blame_my_knowledge.txt', 'w+') as gg:
    # gg.write("I am noob and don't know what to do that's why I have did this")
    LOGGER.info(cf_name)
    if dl_url is not None:
        await i_m_sefg.edit_text("extracting links")
        current_user_id = message.from_user.id
        # create an unique directory
        user_working_dir = os.path.join(DOWNLOAD_LOCATION, str(current_user_id))
        # create download directory, if not exist
        if not os.path.isdir(user_working_dir):
            os.makedirs(user_working_dir)
        # list the formats, and display in button markup formats
        thumb_image, text_message, reply_markup = await extract_youtube_dl_formats(
            dl_url,
            cf_name,
            yt_dl_user_name,
            yt_dl_pass_word,
            user_working_dir
        )
        print(thumb_image)
        req = requests.get(f"{thumb_image}")
        gau_tam = f"{current_user_id}.jpg"
        open(gau_tam, 'wb').write(req.content)
        if thumb_image is not None:
            await message.reply_photo(
                # text_message,
                photo=gau_tam,
                quote=True,
                caption=text_message,
                reply_markup=reply_markup
            )
            await i_m_sefg.delete()
        else:
            await i_m_sefg.edit_text(
                text=text_message,
                reply_markup=reply_markup
            )
    else:
        await i_m_sefg.edit_text(
            "**FCUK**! wat have you entered. \nPlease read /help \n"
            f"<b>API Error</b>: {cf_name}"
        )


# playlist
async def g_yt_playlist(client, message):
    """ /pytdl command """
    # i_m_sefg = await message.reply_text("Processing...you should wait🤗", quote=True)
    if ("rename" not in message.command):
        usr_id = message.from_user.id
        G_DRIVE = False
        if len(message.command) > 1:
            if message.command[1] == "gdrive":
                G_DRIVE = True
        if 'youtube.com/playlist' in message.reply_to_message.text:
            i_m_sefg = await message.reply_text("Downloading...you should wait🤗", quote=True)
            await yt_playlist_downg(message.reply_to_message, i_m_sefg, G_DRIVE)

        else:
            await message.reply_text("Reply to youtube playlist link only 🙄")
    else:
        await message.reply_text("Rename Should not use with youtube playlist 🙄")


async def rename_message_f(client, message):
    message.command[0] = "rename"
    txt = " ".join(message.command)
    if txt.find("rename") > -1 and len(txt.strip()) > 7:
        download_loc = await down_load_media_f(client, message)
        response = {}
        LOGGER.info(response)
        user_id = message.from_user.id
        print(user_id)
        final_response = await upload_to_tg(
            message,
            f'/app/{download_loc}',
            user_id,
            response
        )
        LOGGER.info(final_response)
        await utils.generate_tag(message, final_response)
    else:
        await message.reply_text(f"Command needs to have new file name to rename  Ex:/{RENAME_COMMAND} new_file_name")


async def split_video(client, message):
    message.command[0] = "split"
    no_of_parts = None
    start_seconds = None
    end_seconds = None
    if len(message.command) > 1 and message.command[1].isdigit():
        if int(message.command[1]) > 20:
            await message.reply_text(f"presently {SPLIT_COMMAND} command support only 20 parts maximum")
        else:
            no_of_parts = int(message.command[1])
    elif len(message.command) > 1 and not message.command[1].isdigit() and len(message.command[1].split("-")) > 1:
        try:
            start_seconds = int(
                (datetime.datetime.strptime(message.command[1].split("-")[0], "%H:%M:%S")
                 - datetime.datetime(1900, 1, 1)).total_seconds())
            end_seconds = int(
                (datetime.datetime.strptime(message.command[1].split("-")[1], "%H:%M:%S") - datetime.datetime(
                    1900, 1, 1)).total_seconds())
            if end_seconds > 72000:
                await message.reply_text(
                    f"presently {SPLIT_COMMAND} command support maximum 20 hours end timestamp change end timestamp and try again")
                end_seconds = None
        except:
            await message.reply_text(f"Please enter timestamps in correct format Ex:/{SPLIT_COMMAND} 00:00:30-01:22:34")
    else:
        await message.reply_text(
            f"1.Command needs to have no.of parts or timestamps duration to split  \n Ex:/{SPLIT_COMMAND} 4 \n Ex:/split "
            "00:00:30-01:22:34 ")
    if no_of_parts is not None or start_seconds is not None and end_seconds is not None:
        download_loc = await down_load_media_f(client, message)
        splits_parts_dir_loc = await split_file_to_parts_or_by_start_end_seconds(message, download_loc, no_of_parts,
                                                                                 start_seconds, end_seconds)
        if splits_parts_dir_loc is not None:
            response = {}
            LOGGER.info(response)
            user_id = message.from_user.id
            final_response = await upload_to_tg(
                message,
                splits_parts_dir_loc,
                user_id,
                response
            )
            LOGGER.info(final_response)
        await utils.generate_tag(message,final_response)


async def gp_link_generate(client, message):
    message.command[0] = "gplink"
    txt = " ".join(message.command)
    if txt.find("gplink") > -1 and len(txt.strip()) > 7:
        url_to_shorten = txt[txt.find("gplink") + 7:]
        file_name = None
        if (url_to_shorten.find('workers.dev')>-1):
            file_name = url_to_shorten.split('/')[-1]
        if file_name is not None and len(file_name) > 0:
            await generate_gp_link(message, url_to_shorten, file_name)
        else:
            await generate_gp_link(message, url_to_shorten, None)
    else:
        await message.reply_text(f"Please enter URL to shorten Ex:/{GP_LINKS_COMMAND} https://google.com")


async def incoming_gdrive_and_tg_message_f(client,message):
    download_loc = await incoming_gdrive_message_f(client, message)
    if os.path.getsize(download_loc) < TG_MAX_FILE_SIZE:
        response = {}
        LOGGER.info(response)
        user_id = message.from_user.id
        print(user_id)
        final_response = await upload_to_tg(
            message,
            f'/app/{download_loc}',
            user_id,
            response
        )
        LOGGER.info(final_response)
        await utils.generate_tag(message, final_response)
    else:
        await message.reply_text(f"File size is greater than 2GB So upload to Telegarm is stopped for gtleech command")