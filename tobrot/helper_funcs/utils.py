import pyrogram


async def generate_tag(message, final_response):
    try:
        message_to_send = ""
        for key_f_res_se in final_response:
            local_file_name = key_f_res_se
            message_id = final_response[key_f_res_se]
            channel_id = str(message.chat.id)[4:]
            private_link = f"https://t.me/c/{channel_id}/{message_id}"
            message_to_send += "👉 <a href='"
            message_to_send += private_link
            message_to_send += "'>"
            message_to_send += local_file_name
            message_to_send += "</a>"
            message_to_send += "\n"
        if message_to_send != "":
            mention_req_user = f"<a href='tg://user?id={message.from_user.id}'>Your Requested Files</a>\n\n"
            message_to_send = mention_req_user + message_to_send
            message_to_send = message_to_send + "\n\n" + "#uploads"
        else:
            message_to_send = "<i>FAILED</i> to upload files. 😞😞"
        await message.reply_text(
            text=message_to_send,
            quote=True,
            disable_web_page_preview=True
        )
    except:
        pass


async def sanitize_text(input_text):
    sanitized_data = input_text.translate({ord(c): "-" for c in "+|"})
    sanitized_data = sanitized_data.translate({ord(c): "" for c in "™"})
    sanitized_data = sanitized_data.replace("  ", " ")
    return sanitized_data


async def sanitize_file_name(input_text):
    sanitized_fileName = input_text.translate({ord(c): "" for c in "/\:*?\"<>|"})
    return sanitized_fileName;


async def getMediaAttributes(message):
    if (isinstance(message, pyrogram.Message)):
        for kind in ("audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note"):
            media = getattr(message, kind, None)
            if media is not None:
                break
        return media
