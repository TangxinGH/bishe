import json
import logging
import os
import re
import time

import numpy as np
from tqdm import tqdm

# pd.set_option('display.max_columns', None)  # 打印选项
# pd.set_option("max_colwidth", None)  # 列宽度
from DP.config import original_data_dir
from utils.walk_file import walk_dir, iter_count_line

is_first_el = 0


def data_process(func_wash_data):
    """
     读文件数据,取出list节点。去掉list没有内容的
    :param func_wash_data:  回调函数
    :return:
    """

    file_path_iterator = walk_dir(original_data_dir, False)  # 获得迭代器
    while True:
        try:
            file_path = next(file_path_iterator)  # 得到一条路径
        except StopIteration:
            print("文件读取完毕,io  结束")
            # 回调通知结束 , 文件赢取结束了，主要放结束符
            break  # 结束了

        with open(str(file_path), 'r', encoding='UTF-8') as f:
            t = tqdm(f, total=iter_count_line(file_path), desc=file_path)

            for line in t:  # 遍历文件内容，一行行遍历，读取文本
                if str(line).startswith("#") or str(line).startswith(" #") or str(line).strip() == '' or str(
                        line) == '\n' or str(line) == '\r\n':
                    continue  # 跳过
                else:
                    try:
                        job_overviews = json.loads(line)
                        if job_overviews.get('code') != 200:
                            print('code不等于200', job_overviews.get('code'))
                            t.set_postfix({'code!=200 跳过第': str(t.n) + '行'})
                            continue
                        if len(job_overviews.get('data').get('list')) > 0 and job_overviews.get('data').get(
                                'count') > 0:  # count 不为0 list不一它不是0
                            pass
                        else:
                            t.set_postfix({'no data 跳过第': str(t.n) + '行'})
                            # 没有就是没有咯，
                            continue  # 没有数据，跳过
                    except Exception as ex:
                        # 记录文件出错的行数，文件名
                        print('错误行数行数', file_path, ' 行', t.n, '\n')
                        t.write("json转换出错,会跳过这行，data_pd_process ing ")
                        t.write(ex)
                        with open("record_data_process_json_file_error.log", 'a',
                                  encoding='UTF-8') as f:  # 追加形式
                            f.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S") + "当前处理json错误的文件位置：" + str(
                                file_path) + "行" + str(t.n))  # 记录当前位置
                        continue
                    t.close()
                    pretreatment_json(job_overviews.get('data').get('list'),
                                      os.path.split(file_path)[1], func_wash_data)  # list


def pretreatment_json(job_list, file_name, func_wash):
    """
    用于分离文件名
    list表，文件名用于kw，清洗回调函数
    :param job_list:
    :param file_name:
    :param func_wash:
    :return:
    """
    global is_first_el
    """预处理"""
    default_kw = np.nan  # 代表未知
    # 文件名分割
    try:
        file_name_split = re.findall('(.*)#(.*)\.json', file_name)  # 这时候file name 是对象
        if len(file_name_split) > 0 and file_name_split[0][1] != '':
            default_kw, city_id = file_name_split[0]
    except Exception as ex:
        logging.error("异常分割文件名" + file_name)
        print(ex)
    is_first_el += 1
    if is_first_el == 1:
        func_wash(json.dumps(job_list), default_kw, True)  # json.dumps转为json str
    else:
        func_wash(json.dumps(job_list), default_kw, False)  # json.dumps转为json str
