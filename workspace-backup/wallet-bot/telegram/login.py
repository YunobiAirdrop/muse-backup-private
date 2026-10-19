import asyncio, json, os
from telethon import TelegramClient

API_ID = 20412538
API_HASH = 'e75fb2931ecd43aaf7171d36d2be2cc5'
PHONE = '+6285894336189'
SESSION = '/home/hatch/workspace/wallet-bot/telegram/yunobi.session'

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print('ALREADY_LOGGED_IN:', me.phone or me.id)
    else:
        sent = await client.send_code_request(PHONE)
        print('CODE_SENT_OK')
        # save phone_code_hash for next step
        with open('/home/hatch/workspace/wallet-bot/telegram/.code_hash', 'w') as f:
            f.write(sent.phone_code_hash)
    await client.disconnect()

asyncio.run(main())
