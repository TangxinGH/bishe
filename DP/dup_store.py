import os
import time

from DP.config import finally_storage__one_line_file, finally_storage_multi_line_file, storage_dir_jobs, urls_col, \
    finally_storage_drop_nan_file


def storage_data(ultimate_data):
    """去重后安一定的数据存储"""
    print("去重前的行数和时间" + time.strftime("%Y-%m-%d %H:%M:%S"))
    print(ultimate_data.shape)
    # 去掉重复的数据
    ultimate_data.drop_duplicates(subset=['number'],
                                  ignore_index=True,
                                  inplace=True)  # TypeError: unhashable type: 'list' 18  You've got inplace=False so you're not modifying df
    # main_data_frame to persistence file line by line 导出数据 If ‘orient’ is ‘records’ write out line delimited json
    # format. Will throw ValueError if incorrect ‘orient’ since others are not list like.
    ultimate_data.to_json(path_or_buf=storage_dir_jobs + '/' + finally_storage_multi_line_file, orient="records", lines=True, force_ascii=False)  # DataFrame:default is ‘columns’
    ultimate_data.to_json(path_or_buf=storage_dir_jobs + '/' + finally_storage__one_line_file, orient="records", force_ascii=False)
    #   从main_data_farme 中生成公司表，城市表 以后再说
    ultimate_data.apply(lambda x: [x.dropna()], axis=1).to_json(path_or_buf=storage_dir_jobs + '/' + finally_storage_drop_nan_file, orient="index", force_ascii=False)

    print("去重后的行数" + time.strftime("%Y-%m-%d %H:%M:%S"))
    print(ultimate_data.shape)
    return ultimate_data


def stage_data(data_frame, file_path, urls=False):
    """
    储存各个阶段的文件，中断可继续
    :return:
    """
    if not os.path.isdir(storage_dir_jobs):
        os.mkdir(storage_dir_jobs)

    if urls:
        data_frame[urls_col] = data_frame[urls_col].apply(lambda url: 'https://jobs.zhaopin.com/' + url + '.htm')  # 拼接
        data_frame.to_csv(storage_dir_jobs + '/' + file_path, columns=[urls_col], index=False)  # 保存url
        return

    data_frame.to_json(storage_dir_jobs + '/' + file_path, orient="records", force_ascii=False)
    print(file_path, '已经保存')
