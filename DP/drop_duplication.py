import json
import threading
import time
import unittest
import multiprocessing as mp
from concurrent.futures.thread import ThreadPoolExecutor
from io import StringIO
import  re
from queue import PriorityQueue
from numpy import mean
import  numpy as np
from numpy import average
import pandas as pd

from DP.wash_quantify import qu_com_size


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
    def qu_com_size(self,s):
        x, y, z = re.findall('(\d+-\d+)人|(\d+)人以上|(\d+)人以下', s)[0]
        if x.__contains__('-'):
                return self.qu(x)
        else:
                return np.absolute(x,dtype=np.int16)
        return s
    def qu(self,s):
        if str(s).__contains__('-'):
            min,max=tuple(s.split('-'))
            pd.Series()
            return  np.absolute( mean([int(min),int(max)],dtype=np.int16))#average([min,max])# (min+max)/2
        else:
            return s
    def   qu_work_Exp(self,s):
        x,y =re.findall('(\d-\d)年|不限',s)[0]
        if x.__contains__('-'):
           return self.qu(x)
        else:
            return np.absolute(0,dtype=np.int16)
    def test_pandas(self):
        pd.set_option('display.max_columns', None)
        pd.set_option("max_colwidth", None) #列宽度
        # dp_read_json = pd.read_json("BD经理#530.json")#传入文件名，或者io
        # print(dp_read_json)
        with open("BD经理#530.json",'r',encoding="UTF-8") as f:
            default_kw=None#'NaN'#代表未知
            ee = re.findall('(.*)#(.*)\.json', f.name)
            if len(ee) > 0 and ee[0][1] != '':
                default_kw, cityid = ee[0]

            js= json.loads(f.readline())
            data_frame1 = pd.read_json(StringIO(json.dumps(js.get('data').get('list'))))
            data_frame2 =pd.read_json(StringIO(json.dumps(json.loads(f.readline()).get('data').get('list'))))
            # print(data_frame1)
            # print(data_frame2)
            # data_frame2.iloc[:,2] #修改数据
            data_frame2['companyScaleTypeTagsNew']=data_frame2['companyScaleTypeTagsNew'].apply(lambda y: np.nan if len(y) == 0 else y)

            data_frame2['salaryReal']= data_frame2['salaryReal'].apply(self.qu)
            data_frame2['companyScale']=data_frame2['companySize'].apply(qu_com_size)#qu_com_size
            data_frame2['w_Exp'] = data_frame2['workingExp'].apply(self.qu_work_Exp)  # EXP
            print("------------------------------------------------------------")
            data_frame1['kw']=default_kw
            data_frame2['kw']=default_kw+'另一个文件'
            conact=pd.concat([data_frame1,data_frame2],ignore_index=True ).drop_duplicates(subset=['jobId','cityId','number'],ignore_index=True) #TypeError: unhashable type: 'list'
            # merge=data_frame1.append(data_frame2,ignore_index=True)#追加 append() here does not modify df1 and returns its copy with df2 appended.

            print(conact)
            # pandas.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
        #     verify_integrity : boolean, default False. Check whether the new concatenated axis contains duplicates. This can be very expensive relative to the actual data concatenation.
            #导出数据
            # If ‘orient’ is ‘records’ write out line delimited json format. Will throw ValueError if incorrect ‘orient’ since others are not list like.
            to_json = conact.to_json(path_or_buf="export.json",orient="records",lines=True,force_ascii=False)#DataFrame:default is ‘columns’
            # csv=conact.to_csv(path_or_buf='cvs.json',index=False)


        pass
    def test_add_field(self):
        filename_split = "cityid.json".removesuffix(".json").split("#")
        ee=re.findall('(.*)#(.*)\.json', "cityid 567.json")
        if len(ee)>0 and ee[0][1] != '':
            ee_kw,cityid = ee[0]
        "xxx#".__contains__("#")
        self.default_valut(ee_kw)
        # with open("BD经理#530.json", 'r', encoding="UTF-8") as f:
        #     line = f.readline()
        #     json.loads(line) # 这样太麻烦了

    def  default_valut(self,xx="xxxdfd"):
        print(xx)

    def test_s(self):
        "100-900人".removesuffix("人").split('-')
        print(mp.cpu_count())

    def action(max):
        my_sum = 0
        for i in range(max):
            print(threading.current_thread().name + '  ' + str(i))
            my_sum += i
        return my_sum
    def test_s(self):


        # 创建一个包含2条线程的线程池
        pool = ThreadPoolExecutor(max_workers=1)
        # 向线程池提交一个task, 50会作为action()函数的参数
        future1 = pool.submit(self.action, 50)
        # 向线程池再提交一个task, 100会作为action()函数的参数
        future2 = pool.submit(self.action, 100)
        # 判断future1代表的任务是否结束
        print(future1.done())
        time.sleep(3)
        # 判断future2代表的任务是否结束
        print(future2.done())

        # 关闭线程池
        pool.shutdown()
    def test_quenue(self):
        q = PriorityQueue()

        q.put((2, 'code'))
        q.put((1, 'eat'))
        q.put((3, 'sleep'))

        while not q.empty():
            next_item = q.get()
            print(next_item)
if __name__ == '__main__':
    unittest.main()

