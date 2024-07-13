import os
import hashlib
from telethon import TelegramClient
from uploader import upload_to_cloud
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel

# 创建下载和临时文件夹
if not os.path.exists('download'):
    os.makedirs('download')
if not os.path.exists('temp'):
    os.makedirs('temp')


def calculate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


async def handle_download(client: TelegramClient, message, rclone_config):
    await download_and_compare(client, message, rclone_config)


async def handle_private_group_download(client: TelegramClient, message, rclone_config):
    try:
        link = message.message.strip()
        if not link.startswith("https://t.me/"):
            print("非t.me链接，不处理")
            return

        parts = link.split('/')
        if len(parts) < 5:
            print("链接格式错误")
            return

        group_name = parts[-2]
        message_id = int(parts[-1])

        # 获取群组对象
        dialogs = await client.get_dialogs()
        channel = next((dialog for dialog in dialogs if dialog.entity.username == group_name), None)
        if not channel:
            print("未找到指定群组")
            return

        # 创建InputPeerChannel对象
        peer_channel = InputPeerChannel(channel.entity.id, channel.entity.access_hash)

        # 使用GetHistoryRequest获取消息
        history = await client(GetHistoryRequest(
            peer=peer_channel,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=1,
            max_id=message_id,
            min_id=message_id,
            hash=0
        ))

        if history.messages:
            target_message = history.messages[0]
            if target_message.file:
                await download_and_compare(client, target_message, rclone_config)
            else:
                print("消息中没有文件")
        else:
            print("未找到指定消息")
    except Exception as e:
        print(f'处理私密群组消息下载时出错: {e}')


async def download_and_compare(client: TelegramClient, message, rclone_config):
    try:
        file_name = message.file.name or f'{message.id}'
        temp_path = os.path.join('temp', file_name)
        download_path = os.path.join('download', file_name)

        await client.download_media(message, temp_path)

        if os.path.exists(download_path):
            existing_hash = calculate_hash(download_path)
            temp_hash = calculate_hash(temp_path)

            if existing_hash == temp_hash:
                os.remove(temp_path)
                print(f'文件已存在且相同，删除临时文件: {temp_path}')
            else:
                base, extension = os.path.splitext(file_name)
                new_file_name = f"{base}_new{extension}"
                new_download_path = os.path.join('download', new_file_name)
                os.rename(temp_path, new_download_path)
                print(f'文件已重命名并保存到: {new_download_path}')
                if rclone_config.get('upload'):
                    await upload_to_cloud(new_download_path, rclone_config)
        else:
            os.rename(temp_path, download_path)
            print(f'文件已下载并保存到: {download_path}')
            if rclone_config.get('upload'):
                await upload_to_cloud(download_path, rclone_config)
    except Exception as e:
        print(f'下载过程中出错: {e}')
