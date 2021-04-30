import json
import re

import progressbar  # pip3 install progressbar2
import pymongo
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from tqdm import tqdm

from config import jobs_json_file, mongo_url, mongo_DB, elastic_index_jobs

es = Elasticsearch(timeout=500, max_retries=10)  # es = Elasticsearch(hosts, http_compress=True)
"""
参见https://elasticsearch-py.readthedocs.io/en/v7.12.0/
"""

tbar = tqdm()


def to_elastic(json_file, elastic_index_name, id_column_name='number'):
    """
    位数越多，第一个就越大，6位数的就10万一次了。
    可以取两位数，奇数则。。。
    :return:
    """
    f = open(json_file, 'r', encoding='UTF-8')
    line = f.readline()
    dd = re.sub(r'\],\"\d*?\":\[', ',', line).removeprefix('{\"0\":').removesuffix('}')
    data_list = json.loads(dd)
    le = len(data_list)
    with progressbar.ProgressBar(max_value=le) as bar:
        actions = []

    li = list(tuple())
    figures = len(str(le))  # 位数
    for num, f in enumerate(str(le)):
        li.append((f, figures - num - 1))
    for tu in li:  # 循环第位数
        L, N = tu
        for i in range(int(L)):  # 循环该位数的大小
            step = pow(10, int(N))  # 多少个zero
            for ii in range(step):
                bar.update(le - len(data_list))
                el = data_list.pop()
                number = el[id_column_name]
                del el[id_column_name]
                actions.append({
                    "_index": elastic_index_name,  # The index on Elasticsearch
                    "_id": number,
                    "_source": el
                })
            helpers.bulk(es, actions)
            actions = []

        # try:
        #   result = es.create(index='job222s', id=number, body=job)  #
        # except Exception as ex:
        #     print(ex,result,'？try catch')


def one_by_one(json_file, elastic_index_name, id_column_name='number'):
    f = open(json_file, 'r', encoding='UTF-8')
    line = f.readline()
    dd = re.sub(r'\],\"\d*?\":\[', ',', line).removeprefix('{\"0\":').removesuffix('}')
    data_list = json.loads(dd)
    for el in tqdm(data_list):
        number = el[id_column_name]
        del el[id_column_name]
        try:
            result = es.create(index=elastic_index_name, id=number, body=el)  #
        except Exception as ex:
            print(ex, result, '？try catch')


# 有数组形式的，直接导入
def to_mongo(json_file, mongo_col):
    myclient = pymongo.MongoClient(mongo_url)
    mydb = myclient[mongo_DB]
    mycol = mydb[mongo_col]
    with open(json_file, 'r', encoding='UTF-8') as f:
        readline = f.readline()
        # for item in  json.loads(readline):
        dd = re.sub(r'\],\"\d*?\":\[', ',', readline).removeprefix('{\"0\":').removesuffix('}')

        xx = json.loads(dd.replace("number", '_id'), )
        try:
            # mongodb的要改geojson 形式
            xx['location'] = {
                "type": "Point",
                "coordinates": [xx['location'].get('longitude'), xx['location'].get('latitude')]
            }
        except Exception:
            pass
        try:
            mycol.insert_many(xx, ordered=False)
        except pymongo.errors.BulkWriteError as e:
            print(e.details['writeErrors'])


if __name__ == '__main__':
    """elastic 同样的id bluk方法会被更新，create则会错误 """
    to_elastic(jobs_json_file, elastic_index_jobs)
    # mongo，建设 shell mongodbimport 导入更快 推荐文件导入
