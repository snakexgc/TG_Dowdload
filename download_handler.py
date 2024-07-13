import os
import hashlib
from telethon import TelegramClient
from uploader import upload_to_cloud

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
