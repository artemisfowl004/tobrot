#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | gautamajay52

# the logging things
import logging
import math

from tobrot.helper_funcs import gplink_generator
from tobrot.helper_funcs.utils import sanitize_text

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

import asyncio
import pyrogram.types as pyrogram
import os
import time
import subprocess
import re
from hurry.filesize import size
import requests
import shutil
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from tobrot.helper_funcs.display_progress import progress_for_pyrogram, humanbytes
from tobrot.helper_funcs.help_Nekmo_ffmpeg import take_screen_shot
from tobrot.helper_funcs.split_large_files import split_large_files
from tobrot.helper_funcs.copy_similar_file import copy_file
from requests.utils import requote_uri
from pathlib import Path

from tobrot import (
    TG_MAX_FILE_SIZE,
    EDIT_SLEEP_TIME_OUT,
    DOWNLOAD_LOCATION,
    DESTINATION_FOLDER,
    RCLONE_CONFIG,
    INDEX_LINK,
    UPLOAD_AS_DOC,
    CHANNEL_URL,
    GP_LINKS_API_KEY,
    user_specific_config)

from pyrogram.types import (
    InputMediaDocument,
    InputMediaVideo,
    InputMediaAudio
)


# stackoverflow🤐

def getFolderSize(p):
    from functools import partial
    prepend = partial(os.path.join, p)
    return sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in map(prepend, os.listdir(p))])


async def upload_to_tg(
        message,
        local_file_name,
        from_user,
        dict_contatining_uploaded_files,
        edit_media=False
):
    LOGGER.info(local_file_name)
    LOGGER.info(message.command)
    if message.reply_to_message is not None:
        txt = getattr(message.reply_to_message, 'text', '')
        if txt is not None and txt.find("rename") > -1 and len(txt[txt.find("rename") + 7:]) > 0 and os.path.isfile(local_file_name):
            rename_text = txt[txt.find("rename") + 7:]
            rename_text = await sanitize_text(rename_text)
            print("BAJ LocFileName Before : " + local_file_name)
            absName = os.path.join(os.path.dirname(local_file_name), rename_text + Path(local_file_name).suffix)
            os.rename(local_file_name, absName)
            local_file_name = absName
            print("BAJ LocFileName After : " + local_file_name)
    base_file_name = os.path.basename(local_file_name)
    caption_str = ""
    caption_str += "<code>"
    caption_str += base_file_name
    caption_str += "</code>"
    if CHANNEL_URL is not None:
        caption_str += "\n\nJoin and Support: "
        caption_str += "<a href='"
        caption_str += f"{CHANNEL_URL}"
        caption_str += "'>"
        caption_str += f"{CHANNEL_URL}"
        caption_str += "</a>"
    if os.path.isdir(local_file_name):
        directory_contents = os.listdir(local_file_name)
        directory_contents.sort()
        # number_of_files = len(directory_contents)
        LOGGER.info(directory_contents)
        new_m_esg = message
        if not message.photo:
            new_m_esg = await message.reply_text(
                "Found {} files".format(len(directory_contents)),
                quote=True
                # reply_to_message_id=message.message_id
            )
        for single_file in directory_contents:
            # recursion: will this FAIL somewhere?
            await upload_to_tg(
                new_m_esg,
                os.path.join(local_file_name, single_file),
                from_user,
                dict_contatining_uploaded_files,
                edit_media
            )
    else:
        if os.path.getsize(local_file_name) > TG_MAX_FILE_SIZE:
            LOGGER.info("TODO")
            d_f_s = humanbytes(os.path.getsize(local_file_name))
            i_m_s_g = await message.reply_text(
                "Telegram does not support uploading this file.\n"
                f"Detected File Size: {d_f_s} 😡\n"
                "\n🤖 trying to split the files 🌝🌝🌚"
            )
            splitted_dir = await split_large_files(local_file_name)
            totlaa_sleif = os.listdir(splitted_dir)
            totlaa_sleif.sort()
            number_of_files = len(totlaa_sleif)
            LOGGER.info(totlaa_sleif)
            ba_se_file_name = os.path.basename(local_file_name)
            await i_m_s_g.edit_text(
                f"Detected File Size: {d_f_s} 😡\n"
                f"<code>{ba_se_file_name}</code> splitted into {number_of_files} files.\n"
                "trying to upload to Telegram, now ..."
            )
            for le_file in totlaa_sleif:
                # recursion: will this FAIL somewhere?
                await upload_to_tg(
                    message,
                    os.path.join(splitted_dir, le_file),
                    from_user,
                    dict_contatining_uploaded_files
                )
        else:
            sent_message = await upload_single_file(
                message,
                local_file_name,
                caption_str,
                from_user,
                edit_media
            )
            if sent_message is not None:
                dict_contatining_uploaded_files[os.path.basename(local_file_name)] = sent_message.message_id
    # await message.delete()
    return dict_contatining_uploaded_files


# coded by © gautamajay52 thanks to Rclone team for this wonderful tool.🧘

async def upload_to_gdrive(file_upload, message, messa_ge, g_id):
    tam_link = None
    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
    del_it = await message.edit_text("🔊 Now Uploading to ☁️ Cloud!!!")
    # subprocess.Popen(('touch', 'rclone.conf'), stdout = subprocess.PIPE)
    with open('rclone.conf', 'a', newline="\n", encoding='utf-8') as fole:
        fole.write("[DRIVE]\n")
        fole.write(f"{RCLONE_CONFIG}")
    destination = f'{DESTINATION_FOLDER}'
    if os.path.isfile(file_upload):
        g_au = ['rclone', 'copy', '--config=/app/rclone.conf', f'/app/{file_upload}', 'DRIVE:'f'{destination}', '-v']
        tmp = await asyncio.create_subprocess_exec(*g_au, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
        pro, cess = await tmp.communicate()
        LOGGER.info(pro.decode('utf-8'))
        LOGGER.info(cess.decode('utf-8'))
        gk_file = re.escape(file_upload)
        LOGGER.info(gk_file)
        with open('filter.txt', 'w+', encoding='utf-8') as filter:
            print(f"+ {gk_file}\n- *", file=filter)

        t_a_m = ['rclone', 'lsf', '--config=/app/rclone.conf', '-F', 'i', "--filter-from=/app/filter.txt",
                 "--files-only", 'DRIVE:'f'{destination}']
        gau_tam = await asyncio.create_subprocess_exec(*t_a_m, stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)
        # os.remove("filter.txt")
        gau, tam = await gau_tam.communicate()
        LOGGER.info(gau)
        gautam = gau.decode("utf-8")
        LOGGER.info(gautam)
        LOGGER.info(tam.decode('utf-8'))
        # os.remove("filter.txt")
        gauti = f"https://drive.google.com/file/d/{gautam}/view?usp=drivesdk"
        gau_link = re.search("(?P<url>https?://[^\s]+)", gauti).group("url")
        LOGGER.info(gau_link)
        # indexurl = f"{INDEX_LINK}/{file_upload}"
        # tam_link = requests.utils.requote_uri(indexurl)
        gjay = size(os.path.getsize(file_upload))
        LOGGER.info(gjay)
        button = []
        button.append([pyrogram.InlineKeyboardButton(text="☁️ CloudUrl ☁️", url=f"{gau_link}")])
        if INDEX_LINK:
            indexurl = f"{INDEX_LINK}/{file_upload}"
            tam_link = requests.utils.requote_uri(indexurl)
            tam_link = tam_link.replace('+', '%2B')
            LOGGER.info(tam_link)
            button.append([pyrogram.InlineKeyboardButton(text="ℹ️ IndexUrl ℹ️", url=f"{tam_link}")])
        button_markup = pyrogram.InlineKeyboardMarkup(button)
        await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        await messa_ge.reply_text(
            f"🤖: {file_upload} has been Uploaded successfully to your Cloud <a href='tg://user?id={g_id}'>🤒</a>\n📀 Size: {gjay}",
            reply_markup=button_markup)
        # await message.edit_text(f"""🤖: {file_upload} has been Uploaded successfully to your cloud 🤒\n\n☁️ Cloud URL:  <a href="{gau_link}">FileLink</a>\nℹ️ Direct URL:  <a href="{tam_link}">IndexLink</a>""")
        if not messa_ge.command[0] in ["rename","gtleech"]:
            LOGGER.info('deleting the downloaded file after uploading to Gdrive beacuse it is not rename command')
            os.remove(file_upload)
        else:
            LOGGER.info('Not deleting the downloaded file Even after uploading to Gdrive beacuse it is rename command')
        await del_it.delete()
    else:
        tt = os.path.join(destination, file_upload)
        LOGGER.info(tt)
        t_am = ['rclone', 'copy', '--config=/app/rclone.conf', f'/app/{file_upload}', 'DRIVE:'f'{tt}', '-v']
        tmp = await asyncio.create_subprocess_exec(*t_am, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
        pro, cess = await tmp.communicate()
        LOGGER.info(pro.decode('utf-8'))
        LOGGER.info(cess.decode('utf-8'))
        g_file = re.escape(file_upload)
        LOGGER.info(g_file)
        with open('filter1.txt', 'w+', encoding='utf-8') as filter1:
            print(f"+ {g_file}/\n- *", file=filter1)

        g_a_u = ['rclone', 'lsf', '--config=/app/rclone.conf', '-F', 'i', "--filter-from=/app/filter1.txt",
                 "--dirs-only", 'DRIVE:'f'{destination}']
        gau_tam = await asyncio.create_subprocess_exec(*g_a_u, stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)
        # os.remove("filter1.txt")
        gau, tam = await gau_tam.communicate()
        LOGGER.info(gau)
        gautam = gau.decode("utf-8")
        LOGGER.info(gautam)
        LOGGER.info(tam.decode('utf-8'))
        # os.remove("filter1.txt")
        gautii = f"https://drive.google.com/folderview?id={gautam}"
        gau_link = re.search("(?P<url>https?://[^\s]+)", gautii).group("url")
        LOGGER.info(gau_link)
        # indexurl = f"{INDEX_LINK}/{file_upload}/"
        # tam_link = requests.utils.requote_uri(indexurl)
        # print(tam_link)
        gjay = size(getFolderSize(file_upload))
        LOGGER.info(gjay)
        button = []
        button.append([pyrogram.InlineKeyboardButton(text="☁️ CloudUrl ☁️", url=f"{gau_link}")])
        if INDEX_LINK:
            indexurl = f"{INDEX_LINK}/{file_upload}/"
            tam_link = requests.utils.requote_uri(indexurl)
            tam_link=tam_link.replace('+', '%2B')
            LOGGER.info(tam_link)
            button.append([pyrogram.InlineKeyboardButton(text="ℹ️ IndexUrl ℹ️", url=f"{tam_link}")])
        button_markup = pyrogram.InlineKeyboardMarkup(button)
        await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        await messa_ge.reply_text(
            f"🤖: Folder has been Uploaded successfully to {tt} in your Cloud <a href='tg://user?id={g_id}'>🤒</a>\n📀 Size: {gjay}",
            reply_markup=button_markup)
        # await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        # await messa_ge.reply_text(f"""🤖: Folder has been Uploaded successfully to {tt} in your cloud 🤒\n\n☁️ Cloud URL:  <a href="{gau_link}">FolderLink</a>\nℹ️ Index Url:. <a href="{tam_link}">IndexLink</a>""")
        if not messa_ge.command[0] == "rename":
            LOGGER.info('Not deleting the downloaded file Even after uploading to Gdrive beacuse it is rename command')
            shutil.rmtree(file_upload)
        await del_it.delete()
        # os.remove('rclone.conf')
    if GP_LINKS_API_KEY is not None and tam_link is not None:
        await gplink_generator.generate_gp_link(messa_ge,tam_link,file_upload)


#


async def upload_single_file(message, local_file_name, caption_str, from_user, edit_media):
    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
    sent_message = None
    start_time = time.time()
    #
    thumbnail_location = os.path.join(
        DOWNLOAD_LOCATION,
        "thumbnails",
        str(from_user) + ".jpg"
    )
    LOGGER.info(thumbnail_location)

    dyna_user_config_upload_as_doc = False
    for key in iter(user_specific_config):
        if key == from_user:
            dyna_user_config_upload_as_doc=user_specific_config[key].upload_as_doc
            LOGGER.info(f'Found dyanamic config for user {from_user}')
    #
    if UPLOAD_AS_DOC.upper() == 'TRUE' or dyna_user_config_upload_as_doc:
        thumb_image_path = None
        if thumbnail_location is not None and os.path.exists(thumbnail_location):
            thumb_image_path = await copy_file(
                thumbnail_location,
                os.path.dirname(os.path.abspath(local_file_name))
            )
        if thumb_image_path is not None and os.path.exists(thumb_image_path):
            Image.open(thumb_image_path).convert(
                "RGB"
            ).save(thumb_image_path)
            img = Image.open(thumb_image_path)
            # https://stackoverflow.com/a/37631799/4723940
            img.resize((32, 32))
            img.save(thumb_image_path, "JPEG")
        thumb = None
        if thumb_image_path is not None and os.path.isfile(thumb_image_path):
            thumb = thumb_image_path
        message_for_progress_display = message
        if not edit_media:
            message_for_progress_display = await message.reply_text(
                "starting upload of {}".format(os.path.basename(local_file_name)))
        sent_message = await message.reply_document(
            document=local_file_name,
            # quote=True,
            thumb=thumb,
            caption=caption_str,
            parse_mode="html",
            disable_notification=True,
            # reply_to_message_id=message.reply_to_message.message_id,
            progress=progress_for_pyrogram,
            progress_args=(
                "",
                message_for_progress_display,
                start_time
            )
        )
        if message.message_id != message_for_progress_display.message_id:
            await message_for_progress_display.delete()
        os.remove(local_file_name)
    else:
        try:
            message_for_progress_display = message
            if not edit_media:
                message_for_progress_display = await message.reply_text(
                    "starting upload of {}".format(os.path.basename(local_file_name))
                )
            if local_file_name.upper().endswith(("MKV", "MP4", "WEBM")):
                metadata = extractMetadata(createParser(local_file_name))
                duration = 0
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
                width = 0
                height = 0
                thumb_image_path = None
                if os.path.exists(thumbnail_location):
                    thumb_image_path = await copy_file(
                        thumbnail_location,
                        os.path.dirname(os.path.abspath(local_file_name))
                    )
                else:
                    LOGGER.info("Taking Screenshot")
                    thumb_image_path = await take_screen_shot(
                        local_file_name,
                        os.path.dirname(os.path.abspath(local_file_name)),
                        math.floor(duration / 2)
                    )
                    # get the correct width, height, and duration for videos greater than 10MB
                if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    # ref: https://t.me/PyrogramChat/44663
                    # https://stackoverflow.com/a/21669827/4723940
                    Image.open(thumb_image_path).convert(
                        "RGB"
                    ).save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    # https://stackoverflow.com/a/37631799/4723940
                    img.resize((320, height))
                    img.save(thumb_image_path, "JPEG")
                    # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
                #
                thumb = None
                if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                    thumb = thumb_image_path
                # send video
                if edit_media and message.photo:
                    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                    sent_message = await message.edit_media(
                        media=InputMediaVideo(
                            media=local_file_name,
                            thumb=thumb,
                            caption=caption_str,
                            parse_mode="html",
                            width=width,
                            height=height,
                            duration=duration,
                            supports_streaming=True
                        )
                        # quote=True,
                    )
                else:
                    sent_message = await message.reply_video(
                        video=local_file_name,
                        # quote=True,
                        caption=caption_str,
                        parse_mode="html",
                        duration=duration,
                        width=width,
                        height=height,
                        thumb=thumb,
                        supports_streaming=True,
                        disable_notification=True,
                        # reply_to_message_id=message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "",
                            message_for_progress_display,
                            start_time
                        )
                    )
                if thumb is not None:
                    os.remove(thumb)
            elif local_file_name.upper().endswith(("MP3", "M4A", "M4B", "FLAC", "WAV")):
                metadata = extractMetadata(createParser(local_file_name))
                duration = 0
                title = ""
                artist = ""
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
                if metadata.has("title"):
                    title = metadata.get("title")
                if metadata.has("artist"):
                    artist = metadata.get("artist")
                thumb_image_path = None
                if os.path.isfile(thumbnail_location):
                    thumb_image_path = await copy_file(
                        thumbnail_location,
                        os.path.dirname(os.path.abspath(local_file_name))
                    )
                thumb = None
                if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                    thumb = thumb_image_path
                # send audio
                if edit_media and message.photo:
                    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                    sent_message = await message.edit_media(
                        media=InputMediaAudio(
                            media=local_file_name,
                            thumb=thumb,
                            caption=caption_str,
                            parse_mode="html",
                            duration=duration,
                            performer=artist,
                            title=title
                        )
                        # quote=True,
                    )
                else:
                    sent_message = await message.reply_audio(
                        audio=local_file_name,
                        # quote=True,
                        caption=caption_str,
                        parse_mode="html",
                        duration=duration,
                        performer=artist,
                        title=title,
                        thumb=thumb,
                        disable_notification=True,
                        # reply_to_message_id=message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "",
                            message_for_progress_display,
                            start_time
                        )
                    )
                if thumb is not None:
                    os.remove(thumb)
            else:
                thumb_image_path = None
                if os.path.isfile(thumbnail_location):
                    thumb_image_path = await copy_file(
                        thumbnail_location,
                        os.path.dirname(os.path.abspath(local_file_name))
                    )
                # if a file, don't upload "thumb"
                # this "diff" is a major derp -_- 😔😭😭
                thumb = None
                if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                    thumb = thumb_image_path
                #
                # send document
                if edit_media and message.photo:
                    sent_message = await message.edit_media(
                        media=InputMediaDocument(
                            media=local_file_name,
                            thumb=thumb,
                            caption=caption_str,
                            parse_mode="html"
                        )
                        # quote=True,
                    )
                else:
                    sent_message = await message.reply_document(
                        document=local_file_name,
                        # quote=True,
                        thumb=thumb,
                        caption=caption_str,
                        parse_mode="html",
                        disable_notification=True,
                        # reply_to_message_id=message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "",
                            message_for_progress_display,
                            start_time
                        )
                    )
                if thumb is not None:
                    os.remove(thumb)
        except Exception as e:
            await message_for_progress_display.edit_text("**FAILED 😞**\n" + str(e))
            LOGGER.exception(e)
        else:
            if message.message_id != message_for_progress_display.message_id:
                await message_for_progress_display.delete()
        os.remove(local_file_name)
    return sent_message
