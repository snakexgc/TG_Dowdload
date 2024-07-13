import os
import yaml
from telethon import TelegramClient, events
from download_handler import handle_download, handle_private_group_download

# 读取配置文件
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
phone_number = config['telegram']['phone_number']
bot_token = config['telegram']['bot_token']

proxy_type = config['proxy']['type'].lower()
proxy_host = config['proxy']['host']
proxy_port = config['proxy']['port']
proxy_username = config['proxy'].get('username')
proxy_password = config['proxy'].get('password')

# 创建会话文件夹
if not os.path.exists('session'):
    os.makedirs('session')

# 配置代理
if proxy_username and proxy_password:
    proxy = (proxy_type, proxy_host, proxy_port, True, proxy_username, proxy_password)
else:
    proxy = (proxy_type, proxy_host, proxy_port)

# 创建用户身份的Telegram客户端
user_client = TelegramClient('session/user_session', api_id, api_hash, proxy=proxy)
bot = TelegramClient('session/bot_session', api_id, api_hash, proxy=proxy).start(bot_token=bot_token)

async def main():
    await user_client.start(phone_number)
    print("User client started!")

    @bot.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        if event.message.file:
            await handle_download(user_client, event.message, config['rclone'])
        elif event.message.message and 't.me' in event.message.message:
            await handle_private_group_download(user_client, event.message, config['rclone'])

    await bot.run_until_disconnected()

user_client.loop.run_until_complete(main())
