import threading
import time
import sys

sys.path.append('spiders')
from config import job_info_projectDataDir


# 目录问题
# https://blog.csdn.net/ym404232992/article/details/115429984?utm_medium=distribute.pc_relevant.none-task-blog-baidujs_baidulandingword-0&spm=1001.2101.3001.4242

class JobInfoSpider(threading.Thread):  # 类括号中的是继承线程，调用 start 方法就行
    def __init__(self, thread_name, html_el_list, url_item):
        """
        传入处理的数据
        :param thread_name: 线程名
        :param html_el_list: 当前html的script list
        :param url_item: path
        """
        threading.Thread.__init__(self)
        self.name = thread_name
        self.flow = html_el_list
        self.url_item = url_item

    flow = ''
    url_item = ''

    def run(self) -> None:
        super().run()
        self.parse(self.flow)

    def parse(self, flow):  # 解析的方法，html 元素
        scripts = list(filter(lambda el: str(el.get_attribute('innerHTML')).startswith("__INITIAL_STATE__="), flow))
        # scripts = re.findall("<script>__INITIAL_STATE__=(.*)</script>", text_html)  # 正则好啊
        # 解析
        if scripts.__len__() > 0 and scripts[0].get_attribute('innerHTML').removeprefix("__INITIAL_STATE__="):

            with open(job_info_projectDataDir + '/' + self.url_item,  # 重复值会覆盖文件 w模式
                      'w', encoding='UTF-8') as file_handle:  # 覆盖模式
                file_handle.write(scripts[0].get_attribute('innerHTML').removeprefix("__INITIAL_STATE__="))
                # file_handle.write('#' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')  # 加个时间stamp
                file_handle.flush()  # 立即存入
                file_handle.close()


        else:
            """
                记录当前进度，防止中断继续
                # 没有数据说明。。。记录一下时间就行
                :return: 
                """
            with open('current_climb_progress.txt', 'a+', encoding='utf-8') as f:
                f.write(self.url_item + "#driver get 了但 没有数据#" + time.strftime("%Y-%m-%d %H:%M:%S"))  # 记录当前进度，防止中断继续
