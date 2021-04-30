import logging
import threading
import time
import sys
import mitmproxy.http
from mitmproxy import ctx
# 在最前面
sys.path.append('./spiders/')  # 在要放最前面 解决目录引用问题 No module named 'config.config'; '

from seleniumChrome import do_climb
from spiders.zhaopin import ZhaopinSpider  # 目录问题

# Tips pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)  # 连接调试服务器并挂起

"""
相当于下载器，拿到responses 不由我控制？
"""
# 运行命令：mitmweb -s addons.py 默认打开默认浏览器 8080端口 mitmdump


# sys.path.append("../")  # spiders与插件不在同一模块下，所以要加上路径。查一下import的机制就知道了。尽量反斜杠
url_paths = '/c/i/search/position'


# url_paths = '/test'


class Jobinfo:

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.path.startswith(url_paths) and flow.request.method != 'OPTIONS':  # 还得排除option 方法，这个是请求资源元信息
            # Tips pydevd_pycharm.settrace()  # 在需要断点的地方调用一次pydevd_pycharm.settrace(), 后面的代码就可以正常断点了，
            logging.info(" and flow.request.method != 'option':" + flow.request.method != 'OPTIONS')
            try:
                zhaopin_spider = ZhaopinSpider("zhaopin" + time.strftime("%H%M%S"), flow)
                zhaopin_spider.start()  # 开启线程处理数据
            except Exception as ex:
                print(ex)
                print("Error: 无法启动线程")
                mitmproxy.ctx.log.error("thread")
            # 新开一个线程 调试

        return


class climb(threading.Thread):
    """只是开线程用而已
    你可以，用函数线程，代码简洁
    """

    def __init__(self, thread_name):
        threading.Thread.__init__(self)
        self.name = thread_name

    def run(self) -> None:
        super().run()
        time.sleep(1)
        do_climb()


"""
mitmproxy 钩子插件
"""
addons = [
    Jobinfo()  # 将类作为插件
]

th_names = []
for th in threading.enumerate():
    th_names.append(th.name)

if "climb_thread" in th_names:
    pass

else:
    climb("climb_thread").start()  # 为了调试
