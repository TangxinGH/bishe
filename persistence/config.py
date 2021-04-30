# ----------------------------------------
from utils.parse_yaml import global_config

jobs_json_file = 'G:\\数据集\\zhaopincom\\DP\\storage_jobs\\finally_storage_drop_nan_file.json'
job_detail_json_file = 'G:\\数据集\\zhaopincom\\DP\\storage_job_info\\finally_job_detail_storage_drop_nan.json'
job_recommend_json_file = 'G:\\数据集\\zhaopincom\\DP\\storage_job_info\\finally_recommend_storage_drop_nan.json'
# ----------------------------------------
mongo_url = "mongodb://localhost:27017/"
mongo_DB = 'ERADV'
mongo_col_jobs = "jobs"
mongo_col_job_info = 'job_info'
mongo_col_job_recommend = 'recommend_job'
# id mongo id 默认在数据处理时 number 改为了_id
# ------------------------------------------
elastic_index_jobs = 'jobs'
elastic_index_job_detail = 'job_info'  # 索引名
elastic_index_job_recommend_data = 'recommend_job'
id_column_name = 'number'  # 要作id 的列'

if global_config.get('global_data_source'):
    # 如果配置存在,覆盖
    db_config = global_config.get('global_database').get('db').get(global_config.get('global_data_source'))
    if global_config.get('global_data_source') == 'mongo':
        mongo_url = db_config.get('mongo_url')
        mongo_DB = db_config.get('db_name')
        mongo_col_jobs = db_config.get('col')
    else:
        elastic_index_jobs = db_config.get('col')
        id_column_name = db_config.get('id_column_name')
