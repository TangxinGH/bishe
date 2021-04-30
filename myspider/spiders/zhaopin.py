import json
import logging
import threading
import time

from  config import zhaopin_projectDataDir

"""
负责处理数据
"""


def record_progress(content="none"):
    """
    记录当前进度，防止中断继续
    :param content: 传入内容
    :return:
    """
    with open('current_climb_progress.txt', 'w+') as f:
        f.write(content)  # 记录当前进度，防止中断继续


class ZhaopinSpider(threading.Thread):  # 类括号中的是继承线程，调用 start 方法就行
    def __init__(self, thread_name, flow):
        """
        传入处理的数据
        :param thread_name: 线程名
        :param flow: 当前页的数据
        """
        threading.Thread.__init__(self)
        self.name = thread_name
        self.flow = flow

    flow = ''

    def run(self) -> None:
        super().run()
        self.parse(self.flow)

    def parse(self, flow):  # 解析的方法，json 对象
        text = flow.response.get_text()
        logging.debug(text)
        # get 文件名
        request_content = None
        try:
            request_content = flow.request.content
        except Exception as ex:
            logging.error(ex)
            if input("request_content转换错误，是否继续？是1") == 1:
                pass

        try:
            dict_arg = json.loads(request_content)
            with open(zhaopin_projectDataDir + '/' + dict_arg.get(
                    "S_SOU_FULL_INDEX", "none") + "#" + dict_arg.get("S_SOU_WORK_CITY", "") + '.json',
                      'a', encoding='UTF-8') as file_handle:  # 追加模式
                file_handle.write(text)
                file_handle.write('\n')
                file_handle.write('#' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')  # 加个时间stamp
                file_handle.flush()  # 立即存入
                file_handle.close()

        except Exception as ex:
            logging.error(ex)
            logging.error("错误")
            s = input("转换response的txt错误，是否继续,继续1")
            if s == 1:
                pass
        record_progress(
            json.loads(request_content).get("S_SOU_FULL_INDEX", "none") + "#" + json.loads(request_content).get(
                "S_SOU_WORK_CITY", ""))
