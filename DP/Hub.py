"""
运行main 多进程来做
"""
import logging
import time
from io import StringIO

import pandas as pd

from DP.config import data_washed_file, storage_dir_jobs, job_detail_urls
from DP.dp import data_process
from DP.dup_store import stage_data, storage_data
from DP.wash_quantify import wash_data, quantization, regex_useless

memory_string_io = StringIO()
memory_string_io.write('[')


def wash_list_fun(json_str, default_kw, is_first):
    """
    清洗从dp过来的数据，放入全局memory_string_io 中
    :param json_str: json字符串流
    :param default_kw:
    :return: 是否是第一个数据
    """
    json_str = regex_useless(json_str)  # 处理一此子字段
    fair = wash_data(pd.read_json(StringIO(json_str)), default_kw)  # 清洗数据
    tmp_str = fair.to_json(orient="records",
                           force_ascii=False)  # File path or object. If not specified, # the result is returned as a string.
    if is_first:
        memory_string_io.write(tmp_str.removeprefix('[').removesuffix(']'))  # 放入内存
    else:
        memory_string_io.write(',' + tmp_str.removeprefix('[').removesuffix(']'))  # 放入内存


def finally_merge_dup():
    print("StopIteration 之后，被 调用的函数", time.strftime("%Y-%m-%d %H:%M:%S"))
    memory_string_io.write(']')
    memory_string_io.seek(0)  # read之前，定位回开头
    data_frame = pd.read_json(memory_string_io)  # 放入pandas
    stage_data(data_frame, data_washed_file)

    frame = quantization(data_frame)  # 量化
    data = storage_data(frame)

    stage_data(data, job_detail_urls, True)  # 保存url 文件

    # 返回，再正则表达式一下


# 多进程用的, 修改config的目录，分几个,多运行几次，就是多进程了，去重，在一个文件夹里去重就行，了，之后用数据库，再去一下。
if __name__ == '__main__':
    data_process(wash_list_fun)
    finally_merge_dup()
    memory_string_io.close()  # 关闭流
