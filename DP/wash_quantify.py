import re

import numpy as np
from numpy import mean
import pandas as pd
from DP.config import wash_useless_columns, data_quantized_file, sinicization, genres
from DP.dup_store import storage_data, stage_data


def qu_salary_real(s):
    if str(s).__contains__('-'):
        min, max = tuple(s.split('-'))

        return np.absolute(mean([int(min), int(max)], dtype=np.int16))  # average([min,max])# (min+max)/2
    else:
        return s


def qu_com_size(s):
    zero = np.absolute(min(0, 1), dtype=np.int16)
    try:
        x, y, z = re.findall('(\d+-\d+)人|(\d+)人以上|(\d+)人以下', s)[0]
    except Exception as ex:
        if s == '不限' or s == '无经验':
            pass
        else:
            print(ex, 's是', s)
        return zero
    if x.__contains__('-'):
        return qu_salary_real(x)
    else:
        try:
            absolute = np.absolute(int(z if y == '' else y), dtype=np.int16)
            return absolute
        except Exception as ex:
            print(ex, 'absoultue', x, 'x是s是', s)
            return zero


def qu_work_exp(s):
    zero = np.absolute(min(0, 1), dtype=np.int16)
    try:
        x, y, z = re.findall('(\d+-\d+)年|(\d+)年以下|(\d+)年以上', s)[0]
    except Exception as ex:
        if s == '不限' or s == '无经验':
            pass
        else:
            print(ex, 'exp s is ', s, )
        return zero
    if x.__contains__('-'):
        return qu_salary_real(x)
    else:
        try:
            absolute = np.absolute(int(z if y == '' else y), dtype=np.int16)
            return absolute
        except Exception as ex:
            if s == '不限' or s == '无经验':
                pass
            else:
                print(ex, 'exp absoultue', x, 'exp x是s是', s)
            return zero


def qu_commercial_label(sl):
    return thrift(sl, 'typeName')


def qu_skill(sk):
    return thrift(sk, 'value')


def qu_welfare(sk):
    return thrift(sk, 'value')


def thrift(value_sv, key_sk):
    """处理数组形的，去掉state,value这些字段key的"""
    if value_sv:
        values = []
        for ite in value_sv:
            values.append(ite.get(key_sk))
        if len(values) == 0:
            return np.NaN
        else:
            return values
    return np.NaN


def wash_data(tmp, default_kw=np.NaN):
    """对新加入的数据进行清洗"""
    # 管道一样处理一行数据，一个表，这样最后性能 好点
    for genre, v in genres.items():
        if default_kw in v:
            tmp['行业']=genre
            break
    tmp['kw'] = default_kw

    # 去掉无用列
    tmp.drop(wash_useless_columns, axis=1, inplace=True)  # inplace 是不复制  还有可能会抛出其它异常
    # inplace bool, default False If False, return a copy. Otherwise, do operation inplace and return None.
    # try:
    #     tmp.drop(['rpoProxied','rpoProxied'], axis=1, inplace=True)
    # except Exception as ex:
    #     print(ex,'跳过rpoProxied，rpoProxied，后面加入的字段')
    tmp.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    for column_name, Series in tmp.iteritems():  # 删除list 为[]的值
        try:
            tmp[column_name] = tmp[column_name].apply(lambda y: np.nan if len(y) == 0 else y)
        except Exception as ex:
            pass
    return tmp


def regex_useless(json_str):
    """在清洗的时候去掉一些多余的子字段"""
    dx = re.sub(r', \"typeShowLabel\": \".*?\"', '', json_str)
    dx = re.sub(r'\"type\": \d+?,', '', dx)
    dx = re.sub(r'\"rpoProxied\":.*?,|\"rpoProxy\":.*?,', '', dx)
    return dx.replace('\"state\": 0,', '')


def func_qu_fields():
    l = list(tuple())
    l.append(('salaryReal', qu_salary_real))
    l.append(('companySize', qu_com_size))
    l.append(('workingExp', qu_work_exp))
    l.append(('positionCommercialLabel', qu_commercial_label))
    l.append(('welfareLabel', qu_welfare))
    l.append(('skillLabel', qu_skill))
    return l


def quantization(frame):
    """
    量化
    """
    for field, func in func_qu_fields():
        frame[field] = frame[field].apply(func)
    # 汉化
    frame.rename(columns=sinicization, inplace=True)
    stage_data(frame, data_quantized_file)
    return frame
