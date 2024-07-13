import subprocess


async def upload_to_cloud(file_path, rclone_config):
    try:
        rclone_binary = rclone_config['binary_path']
        remote_name = rclone_config['remote_name']
        remote_path = rclone_config['remote_path']
        destination = f"{remote_name}:{remote_path}"

        result = subprocess.run([rclone_binary, "copy", file_path, destination], capture_output=True, text=True)

        if result.returncode == 0:
            print(f'文件已成功上传到: {destination}')
        else:
            print(f'上传文件时出错: {result.stderr}')
    except Exception as e:
        print(f'上传过程中出错: {e}')
