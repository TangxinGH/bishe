"""
配置文件
"""
from utils.parse_yaml import global_config

seleniumChrome_category_dir = 'E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\Data\\' + 'category.txt'  # 项目数据目录，绝对路径好
zhaopin_projectDataDir = 'G:\\数据集\\\zhaopincom\\zhaopinData'  # 职位数据抓取保存的位置  ，绝对路径好
job_details_handle_data_dir = "G:\\数据集\\\zhaopincom\\zhaopinData"  # 从这里目录取出详细页的url
job_info_projectDataDir = 'G:\\数据集\\zhaopincom\jobDetails'  # job详细信息 html文件解析后 存储在这个目录下
chrome_user_dir = 'E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\myspider\\AutomationProfile'  # 登录保存信息用户目录
chromedriver_dir = 'E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\myspider\\chromedriver.exe'

if global_config.get('global_spider'):
    # 如果配置存在,覆盖
    for k, v in global_config.get('global_spider').items():
        globals()[k] = v  # eval(x) How to get the value of a variable given its name in a string? [duplicate]
