import urllib

import aiohttp

from tobrot import LOGGER, GP_LINKS_API_KEY, CHANNEL_URL


async def generate_gp_link(message,link,file_name):
    try:
        # simple workaround for having plus in url as GP links replacing + with a space
        link = link.replace('+', '%2B')
        data = await get_shortlink(link)
        if not data["status"] == "error":
            caption_str = f'\n<b>{data["shortenedUrl"]}</b>' \
                          f'\n\n <b>👆👆👆👆👆👆👆👆👆👆</b>'
            if file_name is not None:
                file_name = urllib.parse.unquote(file_name)
                caption_str += f'\n<b>{file_name}</b>\n\n'
            caption_str += f"\n⚡Powered By:<b>MoviezTrends</b>"
            await message.reply(caption_str, quote=True, disable_web_page_preview=True)
        else:
            await message.reply(
                f'Unable to generate short Link due to FileName. Generate link from [Website](https://gplinks.in)',
                quote=True, disable_web_page_preview=True)
    except Exception as e:
        await LOGGER.info(f'Error: {e}', quote=True)


async def get_shortlink(link):
    url = 'https://za.gl/api'
    params = {'api': GP_LINKS_API_KEY, 'url': link}

    async with aiohttp.ClientSession() as session:
        LOGGER.info("Calling GP Links API")
        async with session.get(url, params=params, raise_for_status=True) as response:
            data = await response.json()
            return data