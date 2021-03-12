#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

import pyrogram

from tobrot import (
    AUTH_CHANNEL
)


async def new_join_f(client, message):
    chat_type = message.chat.type
    if chat_type != "private":
        await message.reply_text(f"Current CHAT ID: <code>{message.chat.id}</code>")
        # leave chat
        await client.leave_chat(
            chat_id=message.chat.id,
            delete=True
        )
    # delete all other messages, except for AUTH_CHANNEL
    await message.delete(revoke=True)


async def help_message_f(client, message):
    # await message.reply_text("", quote=True)
    #channel_id = str(AUTH_CHANNEL)[4:]
    #message_id = 99
    # display the /help
    button = []
    link = "https://telegra.ph/Help-Message-03-12"
    button.append([pyrogram.InlineKeyboardButton(text="Click to Read", url=f"{link}")])
    button_markup = pyrogram.InlineKeyboardMarkup(button)
    await message.reply_text("**Hello** 👾 !\n__This is Telegram Leech bot 🧲__ \n__Click Below to know how to use me📄__\n\n**Developer 👨🏻‍💻**: @Gillz_13",reply_markup=button_markup)

