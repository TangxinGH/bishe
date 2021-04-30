import pathlib
import sys

from qiniu import Auth, BucketManager, build_batch_delete, put_file, etag
from typing import List, Dict
import os

# from Test.qiniuconfig import access_key, secret_key


class Sync:
    """
    同步目录至七牛云
    """

    def __init__(
            self,
            access_key: str,
            secret_key: str,
            bucket_name: str,
            sync_dir: str,
            exclude: List,
            cover: bool,
            remove_redundant: bool,
    ):
        self.bucket_name = bucket_name
        self.q = Auth(access_key, secret_key)
        self.bucket = BucketManager(self.q)
        self.sync_dir = sync_dir
        self.exclude = exclude
        self.cover = cover
        self.remove_redundant = remove_redundant
        self.sync()

    def sync(self):
        """
        同步操作
        :return:
        """
        remote_files = self.list_remote()
        local_files = self.list_local()
        # 首先删除远端仓库中多余的文件
        remove_remote_files = []
        for remote_filename in remote_files:
            if remote_filename not in local_files:
                remove_remote_files.append(remote_filename)
        self.bucket.batch(build_batch_delete(self.bucket_name, remove_remote_files))
        # 上传本地文件到远端(仅上传远端不存在的以及修改过的)
        for local_filename in local_files:
            win_path = local_filename.replace('\\', '/')
            if (
                    win_path not in remote_files
                    or local_files[win_path]["hash"]
                    != remote_files[win_path]["hash"]
            ):
                print("puting " + win_path)
                ret, info = put_file(
                    self.q.upload_token(self.bucket_name, win_path, 3600),
                    win_path,
                    local_files[local_filename]["fullpath"],
                )

    def list_remote(self) -> Dict:
        """
        列出远程仓库所有的文件信息
        :return: List
        """
        result = {}
        for file in self.bucket.list(self.bucket_name)[0]["items"]:
            result[file["key"]] = file
        return result

    def list_local(self) -> Dict:
        """
        列出本地仓库所有的文件信息
        """
        files = {}

        def get_files(path):
            for filename in os.listdir(path):
                if filename in self.exclude:
                    continue
                if filename.startswith('.git'): 
                    continue
                fullpath = os.path.join(path, filename)
                if os.path.isfile(fullpath):
                    key = fullpath.split(self.sync_dir)[1]
                    files[key.replace('\\', '/')] = {"fullpath": fullpath, "hash": etag(fullpath)}
                else:
                    get_files(fullpath)

        get_files(self.sync_dir)
        return files


if __name__ == "__main__":
    # 不要开代理
    access_key = sys.argv[1]
    secret_key = sys.argv[2]

    Sync(
        access_key=access_key,  # access_key
        secret_key=secret_key,  # secret_key
        bucket_name="bi-she",  # bucket_name
        sync_dir="./",  # 静态文件目录(后面必须有斜杠/)
        exclude=["qiniu_upload.py",'.git','.gitignore'],
        cover=True,
        remove_redundant=True,
    )
