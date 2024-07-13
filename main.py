import os
import yaml
from telethon import TelegramClient, events
from download_handler import handle_download

# 读取配置文件
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
#phone_number = config['telegram']['phone_number']
bot_token = config['telegram']['bot_token']

proxy = {
    'proxy_type': config['proxy']['type'],  # socks5, socks4, http
    'addr': config['proxy']['host'],
    'port': config['proxy']['port'],
    'username': config['proxy'].get('username'),
    'password': config['proxy'].get('password')
}

# 创建会话文件夹
if not os.path.exists('session'):
    os.makedirs('session')

# 创建用户身份的Telegram客户端
#user_client = TelegramClient('session/user_session', api_id, api_hash, proxy=proxy)
bot = TelegramClient('session/bot_session', api_id, api_hash, proxy=proxy).start(bot_token=bot_token)

@bot.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if event.message.file:
        await handle_download(bot, event.message, config['rclone'])

async def main():
    print("Bot started!")
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
