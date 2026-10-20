"""Read-only Telegram airdrop channel scanner.
Uses the user's own saved session (explicitly authorized by user to keep).
NO joins, NO sends, NO clicks, NO link opens. Only reads messages.
"""
import asyncio, json, re, sys
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat

API_ID = 20412538
API_HASH = 'e75fb2931ecd43aaf7171d36d2be2cc5'
SESSION = '/home/hatch/workspace/wallet-bot/telegram/yunobi.session'
OUT = '/home/hatch/workspace/goals/airdrop-testnet-farming-automation/hidden_files/tg-scan-raw.json'

KEYWORDS = re.compile(r'airdrop|testnet|farming|garap|cuan|crypto|drop|whitelist|faucet', re.I)
SINCE_HOURS = 72

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print('NOT_AUTHORIZED'); await client.disconnect(); return
    me = await client.get_me()
    print('logged in as:', me.id)

    dialogs = await client.get_dialogs()
    candidates = []
    for d in dialogs:
        e = d.entity
        name = getattr(e, 'title', '') or ''
        if isinstance(e, (Channel, Chat)) and KEYWORDS.search(name or ''):
            candidates.append({'id': e.id, 'name': name,
                               'broadcast': getattr(e, 'broadcast', False)})
    print('candidate channels:', len(candidates))
    for c in candidates:
        print(' -', c['name'])

    since = datetime.now(timezone.utc) - timedelta(hours=SINCE_HOURS)
    result = {'scanned_at': datetime.now(timezone.utc).isoformat(),
              'since_hours': SINCE_HOURS, 'channels': []}
    for c in candidates[:12]:
        try:
            msgs = []
            async for m in client.iter_messages(c['id'], limit=60):
                if m.date and m.date < since:
                    break
                text = (m.text or '')[:2000]
                if not text.strip():
                    continue
                msgs.append({'date': m.date.isoformat() if m.date else None,
                             'text': text})
            result['channels'].append({'name': c['name'], 'id': c['id'],
                                       'messages': msgs})
            print(f"{c['name']}: {len(msgs)} msgs")
        except Exception as ex:
            result['channels'].append({'name': c['name'], 'id': c['id'],
                                       'error': str(ex)[:200]})
            print(f"{c['name']}: ERROR {ex}")
    with open(OUT, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print('saved ->', OUT)
    await client.disconnect()

asyncio.run(main())
