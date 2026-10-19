import asyncio
from telethon import TelegramClient
from telethon.network import ConnectionTcpFull

API_ID = 20412538
API_HASH = 'e75fb2931ecd43aaf7171d36d2be2cc5'
PHONE = '+6285894336189'
SESSION = '/home/hatch/workspace/wallet-bot/telegram/yunobi.session'

async def main():
    # coba via port 80
    client = TelegramClient(SESSION, API_ID, API_HASH,
                            connection=ConnectionTcpFull,
                            proxy=None)
    # override port via dc
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
