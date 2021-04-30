import json

# original_data_dir = "G:\\数据集\\zhaopincom\\DP\\test"  # 要处理的数据目录
from utils.parse_yaml import global_config

original_data_dir = "G:\\数据集\\zhaopincom\\zhaopinData\\"  # 要处理的数据目录
"""# ---------------- 阶段储存 -----------------------"""
# 方便中断继续，中断，用main,改参数输入
storage_dir_jobs = 'G:\\数据集\\zhaopincom\\DP\\storage_jobs'  # 存放的目录 ,
storage_dir_job_info = 'G:\\数据集\\zhaopincom\\DP\\storage_job_info'
data_washed_file = 'data_washed.json'  # 清洗后
data_quantized_file = 'data_quantized.json'  # 量化后
finally_storage__one_line_file = 'finally_storage_one_line.json'  # 处理完的数据
finally_storage_multi_line_file = 'finally_storage_multi_line.json'  # 一行一json
finally_storage_drop_nan_file = 'finally_storage_drop_nan_file.json'  # 去掉nan
job_detail_urls = 'urls_info.csv'
"""---------------------------------------------------"""

# 要去掉的列
wash_useless_columns = ['applyType',
                        'chatWindow',
                        'liveCard',
                        # 'companyScaleTypeTagsNew',最佳雇主，上市公司
                        'deliveryPath',
                        'distance',
                        'needMajor',
                        'companyId',  # 没有用
                        'cityId',  # workcity 代替
                        'jobId',  # 删除job_id,应该没有重复的吧
                        'companyRootId',  # 无用的东西
                        'companyNumber',
                        'tradingArea',
                        'cityDistrict',  # 经纬度够了
                        # 'positionCommercialLabel',  # 急招
                        'positionURL',  # 去掉
                        'positionUrl',  # 去掉，到时候动态生成
                        'menVipLevel',
                        'positionHighlight',  # 共同的企业，共同的事业
                        'positionSourceType',
                        'positionSourceTypeUrl',
                        'recallSign',
                        'companyUrl',
                        'salaryCount',
                        'salary60',  # 工资 jobinfo里会有
                        'staffCard',  # 人事主管信息
                        'hasAppliedPosition']

# 汉化
sinicization = {
    'companySize': '公司规模',
    'companyScaleTypeTagsNew': '公司荣誉称号',
    'positionCommercialLabel': '职位商业标签',
    'name': '职位',
    'education': '学历',
    'property': '公司性质',
    'publishTime': '发布时间',
    'salaryReal': '薪酬',
    'skillLabel': '技能',
    'welfareLabel': '福利待遇',
    'workCity': '工作城市',
    'workingExp': '经验',
    'workType': '用工制',
    'companyName': '公司名'
}

urls_col = 'number'  # url所在的列

# ----------------- job info detail ----------------

original_job_detail_data_dir = "G:\\数据集\\zhaopincom\\jobDetails\\jobDetailslinux\\"
# original_job_detail_data_dir = "G:\\数据集\\zhaopincom\\jobDetails\\test\\"  # 测试用

stage_job_info_file_one = '保存第一阶段.json'
stage_job_info_file_two = '第二阶段文件.json'
finally_job_detail_storage_drop_nan_file = 'finally_job_detail_storage_drop_nan.json'
finally_recommend_storage_drop_nan_file = 'finally_recommend_storage_drop_nan.json'
# --------------------------------------------------
#  保留哪些job_info列
# desc 类
# number
# lat lon


# ----------------- 行业大类-------------
# genre='行业'
if global_config.get('global_data_process').get('genres'):
    genres = json.loads(
        open(global_config.get('global_data_process').get('genres'), 'r', encoding='utf-8').readline())
else:  # 使用默认的
    genres = json.loads(
        open('E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\Data\\category.json', 'r', encoding='utf-8').readline())

#   详细页与概要页 数据 两表合并，要存储的目录与文件名
storage_dir_merge = 'G:\\数据集\\zhaopincom\\DP\\storage_merge\\'
finally_elastic_merge_nan_file = 'finally_elastic_merge_nan_file.json'
finally_mongo_merge_nan_file = 'finally_mongo_merge_nan_file.json'
finally_mongo_merge_line_file = 'finally_mongo_merge_line_file.json'

# --------------------- 全局配置覆盖------------------------------------
if global_config.get('global_data_process').get('finally_two_table_merge_storage'):
    # 如果配置存在,覆盖
    for k, v in global_config.get('global_data_process').get('finally_two_table_merge_storage').items():
        globals()[k] = v  # eval(x) How to get the value of a variable given its name in a string? [duplicate]

if global_config.get('global_data_process').get('jobs_dp'):
    # 如果配置存在,覆盖
    for k, v in global_config.get('global_data_process').get('jobs_dp').items():
        globals()[k] = v  # eval(x) How to get the value of a variable given its name in a string? [duplicate]

if global_config.get('global_data_process').get('jobs_info_dp'):
    # 如果配置存在,覆盖
    for k, v in global_config.get('global_data_process').get('jobs_info_dp').items():
        globals()[k] = v  # eval(x) How to get the value of a variable given its name in a string? [duplicate]

if global_config.get('global_data_process').get('urls_col'):
    urls_col=global_config.get('global_data_process').get('urls_col')