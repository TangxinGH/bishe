import logging
import os

from tqdm import tqdm
from itertools import (takewhile, repeat)


def walk_dir(dir,tb=True):
    """
    遍历目录下所有文件包括子目录
    :param: postfix_n extra desc state name
    :return: 返回路径+文件
    """
    # len([lists for lists in os.listdir(dir) if         os.path.isfile(os.path.join(dir, lists))])
    if tb:
        tbar = tqdm(total=total_file_count(dir), desc='文件数量进度：')
    for root, dirs, files in os.walk(dir, topdown=False):  # 分布式解决
        for name in files:
            if tb:
                tbar.update()
                tbar.set_postfix(file="当前文件 {}".format(name))
            yield os.path.join(root, name)
        for name in dirs:
            logging.debug("当前目录下的文件夹：" + os.path.join(root, name))
        # yield os.path.join(root, name)
    if tb:
        tbar.close()  # 关闭
    # root 所指的是当前正在遍历的这个文件夹的本身的地址
    # dirs 是一个 list ，内容是该文件夹中所有的目录的名字(不包括子目录)
    # files 同样是 list , 内容是该文件夹中所有的文件(不包括子目录)


def total_file_count(dir):
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for file in filenames:
            file_count = file_count + 1
    return file_count


def iter_count_line(file_name):
    """
    计算行数
   :param file_name:
   :return: 文件行数
   """
    buffer = 1024 * 1024
    with open(file_name, 'r', encoding='UTF-8') as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)
