import asyncio
from telethon import TelegramClient

API_ID = 20412538
API_HASH = 'e75fb2931ecd43aaf7171d36d2be2cc5'
PHONE = '+6285894336189'
SESSION = '/home/hatch/workspace/wallet-bot/telegram/yunobi.session'

PROXY = ('http', 'hatch-egress-proxy', 3128, True,
         'hatch-runtime', '04106e32602a4da884b14a1ed28b7212')

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH, proxy=PROXY)
    await client.connect()
    print('connected:', client.is_connected())
    if await client.is_user_authorized():
        me = await client.get_me()
        print('ALREADY_LOGGED_IN:', me.id)
    else:
        sent = await client.send_code_request(PHONE)
        print('CODE_SENT_OK')
        with open('/home/hatch/workspace/wallet-bot/telegram/.code_hash', 'w') as f:
            f.write(sent.phone_code_hash)
    await client.disconnect()

asyncio.run(main())
