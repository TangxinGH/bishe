from utils.parse_yaml import global_config

reserve_word_file = 'E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\analysis\\保留字.txt'  # 用户字典
stop_words_dir = 'E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\analysis\\stopWord\\'
custom_stop_word_file = 'E:\\WorkSpacePyCharm\\PythonLearn\\ERDAV\\analysis\\mystopWord\\自定义停用词.txt'
# --------------------- 全局配置覆盖------------------------------------
if global_config.get('analysis'):
    # 如果配置存在,覆盖
    for k, v in global_config.get('analysis').items():
        globals()[k] = v  # eval(x) How to get the value of a variable given its name in a string? [duplicate]
