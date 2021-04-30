import json
import os
import re
import sys
import time
from io import StringIO

sys.path.append('../')
import jieba
import numpy as np
import pandas  as  pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from DP.config import original_job_detail_data_dir, storage_dir_job_info, \
    stage_job_info_file_one, stage_job_info_file_two, storage_dir_jobs, finally_storage_drop_nan_file, \
    storage_dir_merge, finally_elastic_merge_nan_file, finally_mongo_merge_line_file, finally_storage__one_line_file
from analysis.config import reserve_word_file
from analysis.icu import stop_words, my_stop_words
from utils.walk_file import walk_dir, iter_count_line

jieba.load_userdict(reserve_word_file)  # 用户字典
detailed_internal_string_io = StringIO()
detailed_internal_string_io.write('[')

stop_word = stop_words()
my_word = my_stop_words()


def del_stop_word(s):
    text = s
    for i in range(len(my_word)):
        text = text.replace(my_word.iloc[i].strip(), '')  # 先删除自己的停用词
    for i in range(len(stop_word)):
        text = text.replace(stop_word.iloc[i].strip(), '')  # del
    # 分词，分成数组？？？
    # text_li = jieba.cut(text)  # 返回list
    # text = {'original': text, 'cut_li': list(text_li)}  # 空格分隔 数组
    # text = thu1.cut(text, text=True)  # thu1 词性好
    return text


def pretreatment():
    file_path_iterator = walk_dir(original_job_detail_data_dir)  # 获得迭代器
    if os.path.exists(storage_dir_job_info + '/' + stage_job_info_file_one):  # 先删除原先的
        os.remove(storage_dir_job_info + '/' + stage_job_info_file_one)

    i = 0
    while True:
        try:
            file_path = next(file_path_iterator)  # 得到一条路径
            # try:
            with open(str(file_path), 'r', encoding='UTF-8') as f:
                i += 1
                line = f.readline()
                if str(line).startswith("#") or str(line).startswith(" #") or str(line).strip() == '' or str(
                        line) == '\n' or str(line) == '\r\n':
                    continue  # 跳过
                if not line.__contains__('jobNumber') or not line.__contains__('jobInfo'):
                    continue
                # try:

                # print(i)
                line = re.sub(r'}</script>.*', '}', line)
                job_overviews = json.loads(line)
                job_detail = job_overviews.get('jobInfo').get('jobDetail')

                # TODO 应该分阶段处理的，这样快
                soup = BeautifulSoup(job_detail['detailedPosition']['jobDesc'], features='lxml')
                job_detail['detailedPosition']['jobDesc'] = del_stop_word(
                    re.sub(r'\d{8,13}|\*+|www.*.com|工作地址.+?', '', soup.get_text('\n', True)))

                # 改一下结构
                job_detail['detailedPosition']['detailedCompany'] = job_detail['detailedCompany']
                del job_detail['detailedCompany']
                job_detail['detailedPosition']['detailedCompany']['companyDescription'] = del_stop_word(
                    job_detail['detailedPosition']['detailedCompany']['companyDescription'])

                with open(storage_dir_job_info + '/' + stage_job_info_file_one, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(job_detail['detailedPosition'], ensure_ascii=False) + '\n')  # 保存

        except StopIteration:
            print("文件读取完毕,io  第一阶段处理结束")
            break  # 结束了


def job_detail_process(job_detail):
    # 构造新的dict,企业描述不要了吧，重复率高。
    mer_field = {
        # '企业描述': job_detail.get('detailedCompany').get('companyDescription'),
        '融资阶段': job_detail.get('detailedCompany').get('financingStageName')}
    # 一些处理detailedCompany 节点
    if mer_field['融资阶段'] == '':
        del mer_field['融资阶段']

    # 要保留的列
    # 经纬度 转 geojson
    mer_field['位置'] = {
        "lat": job_detail['latitude'],  # 纬度
        "lon": job_detail['longitude']
    }
    mer_field['number'] = job_detail['number']
    # 汉化
    mer_field['职位描述'] = job_detail['jobDesc']
    # 删除没有中文的
    if mer_field['职位描述'] == '':
        del mer_field['职位描述']

        # 岗位职责 职责描述 任职要求 备注 基本要求 其他要求 任职条件 福利待遇 工作要求 工作职责 培训体系 工资待遇  条件： 冒号分割。 词性标签
    detailed_internal_string_io.write(json.dumps(mer_field) + ',')


def to_pandas_process(file_io):
    job_info_df = pd.read_json(file_io)

    # 量化
    for column_name, Series in job_info_df.iteritems():  # 删除list 为[]的值
        try:
            job_info_df[column_name] = job_info_df[column_name].apply(lambda y: np.nan if len(y) == 0 else y)
        except Exception as ex:
            pass
    # 去重,不用，直接覆盖crtl +v 文件的形式
    # 表连接
    total_time = time.perf_counter()
    start_read_t = time.perf_counter()
    jobs_l = pd.read_json(
        open(storage_dir_jobs + '/' + finally_storage__one_line_file, 'r', encoding='UTF-8'))  # 导入jobs 文件

    end_read_t = time.perf_counter()
    print("读取时间", end_read_t - start_read_t)
    # 设置索引
    start_read_t = time.perf_counter()
    jobs_l.set_index('number', inplace=True)
    job_info_df.set_index('number', inplace=True)
    end_read_t = time.perf_counter()
    print('设置索引时间', end_read_t - start_read_t)
    # 合并
    start_read_t = time.perf_counter()
    # result_finally_merge = pd.merge(jobs_l, job_info_df, how='left', on='number',copy=False)  # 左连接，
    result_finally_merge = jobs_l.join(job_info_df, how='left')
    end_read_t = time.perf_counter()
    print("合并时间", end_read_t - start_read_t)

    print("合并后的数据", result_finally_merge.shape)  # 合并后的形状
    # 复制index to column,恢复索引
    start_read_t = time.perf_counter()
    result_finally_merge.reset_index(inplace=True)  # numer会回去
    job_info_df.reset_index(inplace=True)  # 重置索引为0
    end_read_t = time.perf_counter()
    print('恢复索引时间', end_read_t - start_read_t)

    total_time_end = time.perf_counter()
    print('总共时间', total_time_end - total_time)
    # 储存
    if not os.path.isdir(storage_dir_merge):
        os.mkdir(storage_dir_merge)

    # result_finally_merge.to_pickle(path=storage_dir_merge+'/'+'pickle_finally_elastic_merge_nan_file.pkl')
    # elastic 用
    elastic_time = time.perf_counter()
    # result_finally_merge.apply(lambda x: [x.dropna()], axis=1).to_json( # 太慢
    #     path_or_buf=storage_dir_merge + '/' + finally_elastic_merge_nan_file, orient="index",
    #     force_ascii=False)
    # %time [ {k:v for k,v in m.items() if pd.notnull(v)} for m in df.to_dict(orient='rows')]
    result_finally_merge.to_json(
        path_or_buf=storage_dir_merge + '/' + finally_elastic_merge_nan_file, orient="index",
        force_ascii=False)
    elastic_time_end = time.perf_counter()
    print('drop na时间', elastic_time_end - elastic_time)

    # mongo用
    time_mon = time.perf_counter()
    result_finally_merge['位置'] = result_finally_merge['位置'].apply(mong_geojson)
    result_finally_merge.rename(columns={'number': '_id'}, inplace=True)
    result_finally_merge.to_json(path_or_buf=storage_dir_merge + '/' + finally_mongo_merge_line_file, orient="records",
                                 lines=True,
                                 force_ascii=False)
    time_mon_end = time.perf_counter()
    print('mongo用时', time_mon_end - time_mon)

    if not os.path.isdir(storage_dir_job_info):
        os.mkdir(storage_dir_job_info)
    # 储存已下载的urls
    job_info_df['number'] = job_info_df['number'].apply(lambda url: 'https://jobs.zhaopin.com/' + url + '.htm')  # 拼接
    job_info_df.to_csv(storage_dir_job_info + '/' + 'job_detailed_url.csv', columns=['number'], index=False)  # 保存url


def mong_geojson(el):
    try:
        # mongodb的要改geojson 形式
        return {
            "type": "Point",
            "coordinates": [float(el['lon']), float(el['lat'])]  # int 类型
        }

    except (TypeError, ValueError) as es:
        return el


# 拆分阶段函数
def select_stage(stage_num=0):
    l = list()
    l.append(pretreatment)  # 放入内存地址
    l.append(two_stage)
    l.append(lambda: to_pandas_process(open(storage_dir_job_info + '/' + stage_job_info_file_two)))  # 第三阶段
    l[stage_num]()  # 调用


def two_stage():
    with open(storage_dir_job_info + '/' + stage_job_info_file_one, 'r', encoding='utf-8')as f:
        # it = iter(f)
        for line in tqdm(f, total=iter_count_line(storage_dir_job_info + '/' + stage_job_info_file_one)):
            job_detail_process(json.loads(line))
        # 保存阶段文件
    detailed_internal_string_io.seek(0)  # 定位开头
    with open(storage_dir_job_info + '/' + stage_job_info_file_two, 'w', encoding='utf-8') as f:
        f.write(detailed_internal_string_io.getvalue().removesuffix(',') + ']')


if __name__ == '__main__':
    # Python program to demonstrate
    # 命令行启动
    print("This is the name of the program:", sys.argv[0])
    print("Argument List:", str(sys.argv))
    if len(sys.argv) > 1:
        select_stage(int(sys.argv[1]))
        print(f'阶段{sys.argv[1]}完成')
        sys.exit()  # 退出

    # 分三阶段
    pretreatment()
    # 第二阶段
    with open(storage_dir_job_info + '/' + stage_job_info_file_one, 'r', encoding='utf-8')as f:
        # it = iter(f)
        for line in tqdm(f, total=iter_count_line(storage_dir_job_info + '/' + stage_job_info_file_one)):
            job_detail_process(json.loads(line))
    # 保存阶段文件
    detailed_internal_string_io.seek(0)  # 定位开头
    with open(storage_dir_job_info + '/' + stage_job_info_file_two, 'w', encoding='utf-8') as f:
        f.write(detailed_internal_string_io.getvalue().removesuffix(',') + ']')

    # 第三阶段
    to_pandas_process(open(storage_dir_job_info + '/' + stage_job_info_file_two))
