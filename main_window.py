import os
import sys
from random import random
from time import sleep

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QPushButton, QStackedLayout
)
# 这个 QtWebEngineWidgets 不能注释
from PyQt5 import QtWebEngineWidgets
# from PySide6 import QtWidgets
from PyQt5.uic import loadUi  # 标红是bug 不是我的错
from qt_material import apply_stylesheet

from analysis.machine_learn.product_predict import get_predict_result
from utils import pythontail


# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(tuple)
    current_climb_progress_job_info = None
    nlines = 3
    fname = './myspider/current_climb_progress.txt'
    fname1 = './myspider/current_jobinfo_json_file.txt'
    fname2 = './myspider/item_url_count.txt'

    def run(self):
        """Long-running task."""

        while True:
            sleep(2)
            i = 0
            if os.path.exists(self.fname) and os.path.exists(self.fname1) and os.path.exists(self.fname2):
                with open(self.fname, 'r', encoding='utf-8') as f:
                    content = f.readlines()
                with open(self.fname1, 'r', encoding='utf-8') as f:
                    content1 = f.readlines()
                with open(self.fname2, 'r', encoding='utf-8') as f:
                    content2 = f.readlines()
                count = len(content)
                if count < self.nlines:
                    dec_num_line = count
                else:
                    dec_num_line = self.nlines
                content_tail = list()
                for i in range(count - dec_num_line, count):
                    content_tail.append(content[i])
                self.progress.emit(('\r'.join(content_tail), '\r'.join(content1), '\r'.join(content2)))  # 提交一些数据
                content_tail.clear()  # 清空
        self.finished.emit()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 两个方法
        # Translating   the content of your  .ui files into Python code using   Python  pyuic5
        # Loading   the content of the  .ui files dynamically using  uic.loadUi()
        # loadUi("main_ui.ui", self)
        loadUi("ui/main_window2.ui", self)

        # string value
        # title = "网络招聘数据分析可视化"
        # set the title
        # self.setWindowTitle(title)
        # self.pb_start_spider.clicked.connect(self.click_start_spider_jobs)# 注册点击事件

        self.process = QtCore.QProcess(self)  # 进程
        self.process.readyReadStandardOutput.connect(self.handleStdOut)
        self.process.readyReadStandardError.connect(self.handleStdErr)
        self.process.finished.connect(self.process_end)
        self.pushButton_kill_end.clicked.connect(self.process_kill_end)

        self.tail_thread = QtCore.QThread()
        self.worker = Worker()  # Step 3: Create a worker object
        # self.worker.current_climb_progress_job_info = self.current_climb_progress_job_info  # 要写的数据
        self.worker.moveToThread(self.tail_thread)  # Step 4: Move worker to the thread
        self.tail_thread.started.connect(self.worker.run)  # # Step 5: Connect signals and slots
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.tail_thread.start()  # # Step 6: Start the thread

        # 再开一进程
        self.process2 = QtCore.QProcess(self)
        self.process2.readyReadStandardOutput.connect(self.handle_dp_console_output)
        self.process2.readyReadStandardError.connect(self.handle_dp_console_error)
        self.cursor = self.textEdit_dp_bottom.textCursor() # 游标
        self.textEdit_dp_bottom.ensureCursorVisible()

    # 信号与槽
    # 代码说明：
    #
    # @pyqtSlot()是这种方式的修饰关键词，他表明下面函数是信号槽函数
    #
    # 由于没有connect来初始化，在初始化函数中，没有说明是那个控件信号的关键词。
    #
    # 所以，在@pyqtSlot()方式里，函数名称有特殊要求
    #
    # on_(控件对象名)_信号名(self,内置参数)
    #
    # 内置参数可以缺省
    # ————————————————
    # 版权声明：本文为CSDN博主「集电极」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
    # 原文链接：https://blog.csdn.net/qq_38463737/article/details/107806432
    # (控件名称).(信号名称).connect(槽函数名称)

    # ---------------输出console qt 上 --------------------
    # 直接Process.start("cmd.exe")跳不出cmd界面

    def handleStdOut(self):
        data = self.process.readAllStandardOutput().data()
        self.textBrowser_stdout_console.append(
            data.decode('utf-8'))  # 另一进程 cmd 默认gbk编码 mitmdump是utf-8 。所以先chcp 65001 统一utf8

    def handleStdErr(self):
        data = self.process.readAllStandardError().data()
        self.textBrowser_stdout_console.append(data.decode('utf-8'))

        # 另一种
    def handle_dp_console_output(self):
        # if random() < 0.5:
        #     return
        # cursor.beginEditBlock();
        # cursor.insertText("Hello");
        # cursor.insertText("World");
        # cursor.endEditBlock();
        # textDocument->undo();
        self.textEdit_dp_bottom.undo()
        data = self.process2.readAllStandardOutput().data()
        self.cursor.movePosition(QtGui.QTextCursor.Start)
        self.cursor.insertText(data.decode('utf-8'))
        # self.textEdit_dp_bottom.setText(data.decode('utf-8'))

    def handle_dp_console_error(self):
        # if random() < 0.5:
        #     return
        self.textEdit_dp_bottom.undo()
        data = self.process2.readAllStandardError().data()
        self.cursor.movePosition(QtGui.QTextCursor.Start)
        self.cursor.insertText(data.decode('utf-8'))
        # self.textEdit_dp_bottom.setText(data.decode('utf-8'))

    # --------------end 输出console----------------------------------

    # ------------- spider stast ---------------------------
    def reportProgress(self, s):
        s0, s1, s2 = s
        self.current_climb_progress_job_info.setText(s0)
        self.pt_command_line_job_info.setPlainText(s1)
        self.tl_item_url_count_job_info.setText(s2)

    def process_end(self):
        # QProcess::kill()
        print("进程结束，状态为？", self.process.state(), self.process.exitStatus())

    def process_kill_end(self):
        self.process.kill()  # 杀掉进程

    # 使用槽来注册响应事件
    @pyqtSlot()
    def on_pb_start_spider_clicked(self):
        sender = self.sender()  # 指的是发送信号的对象
        self.tabWidget_last_bottom.setCurrentIndex(1)  # 定位到相应page
        print('执行cmd 命令')
        os.system('chcp 65001')  # 字符中文UTF-8
        # 追加目录
        # sys.path.append(os.getcwd()+'/myspider/spiders') # 绝对路径
        print(os.getcwd())
        # os.chdir('./myspider')
        # https://blog.csdn.net/yrk0556/article/details/104308866  && 前面成功，才会执行后面
        # os.system(' cd myspider && mitmdump -s  addons.py')  # 执行命令
        # popen = os.popen('mitdump -s addons.py')
        # print('popen', popen)
        # 2 - 带空格，无法启动
        # 运行指定 程序
        # 运行cmd ,是这样写。 如果只有start 像ping baiudu.com就可以。要指定程序
        self.process.setProgram("cmd")
        # 注意，如果字符串加有引号，可以接受用命令分隔符 “&&” 分隔多个命令
        # https://blog.walterlv.com/post/cmd-startup-arguments.html
        self.process.setArguments(['/c', ' chcp 65001 && cd myspider && mitmdump -s  addons.py'])
        self.command_line_input.setText(' 执行命令 chcp 65001 && cd myspider && python   mitmdump -s  addons.py')
        # self.process.setArguments(['/c', 'dir'])
        self.process.start()

    # -------------- end spider -----------------------

    # -----------------DP 类--------------------
    @pyqtSlot()
    def on_pb_start_spider_job_info_clicked(self):
        self.tabWidget_last_bottom.setCurrentIndex(1)  # 定位到相应page
        print('执行cmd  on_pb_start_spider_job_info_clicked命令')
        os.system('chcp 65001')  # 字符中文UTF-8
        self.process.setProgram("cmd")
        self.process.setArguments(['/c', ' chcp 65001 && cd myspider && python   seleniumChrome.py arg1'])
        self.tl_command_line_job_public_dp.setText('执行命令 chcp 65001 && cd myspider && python  seleniumChrome.py')
        self.process.start()

    @pyqtSlot()
    def on_pb_dp_jobs_wash_clicked(self):
        self.tabWidget_last_bottom.setCurrentIndex(1)  # 定位到相应page
        print('执行命令cmd dp')
        os.system('chcp 65001')  # 字符中文UTF-8
        # self.process.kill()
        self.process.setProgram("cmd")
        self.process.setArguments(['/c', ' chcp 65001 && cd DP && python  Hub.py'])
        self.tl_command_line_job_public_dp.setText('执行命令 chcp 65001 && cd DP && python  Hub.py')
        self.process.start()

    @pyqtSlot()
    def on_pb_dp_job_info_wash_clicked(self):  # 详细页数据清洗
        self.tabWidget_last_bottom.setCurrentIndex(2)  # 定位到相应page
        print('执行命令cmd dp_job_info')
        os.system('chcp 65001')  # 字符中文UTF-8
        # self.process.kill()
        self.process2.setProgram("cmd")
        self.process2.setArguments(['/c', ' chcp 65001 && cd DP && python   dp_job_info.py'])
        self.tl_command_line_job_public_dp.setText('执行命令 chcp 65001 && cd DP && python   dp_job_info.py')
        self.process2.start()

    @pyqtSlot()
    def on_pb_dp_storge_db_clicked(self):  # 详细页数据清洗
        self.tabWidget_last_bottom.setCurrentIndex(1)  # 定位到相应page
        print('执行命令cmd elastic')
        os.system('chcp 65001')  # 字符中文UTF-8
        # self.process.kill()
        self.process.setProgram("cmd")
        self.process.setArguments(['/c', ' chcp 65001 && cd persistence && python   elastic.py'])
        self.tl_command_line_job_public_dp.setText('执行命令 chcp 65001 && cd persistence && python   elastic.py')
        self.process.start()

    @pyqtSlot()
    def on_pb_warning_break_job_wash_clicked(self):
        self.process.kill() #杀掉进程job 清洗

    @pyqtSlot()
    def on_pb_success_break_job_info_wash_clicked(self):
        self.process.kill()  # 杀掉进程job info  清洗
    # ---------------end DP ---------------------------

    # --------------- 分段执行 ------------------------
    @pyqtSlot()
    def on_stage_dp_info_clicked(self):
        self.tabWidget_last_bottom.setCurrentIndex(1)  # 定位到相应page
        print(f'执行命令cmd DP STAGE,currentIndex值为{ self.stage_select.currentIndex()}')
        os.system('chcp 65001')  # 字符中文UTF-8
        # self.process.kill()
        self.process.setProgram("cmd")
        self.process.setArguments(
            ['/c',
             f'chcp 65001 && cd DP && python  dp_job_info.py {self.stage_select.currentIndex()}'])
        self.tl_command_line_job_public_dp.setText(
            f'执行命令 chcp 65001 && cd DP && python  dp_job_info.py {self.stage_select.currentIndex()}')
        self.process.start()

    # ------------------------machine learn ---------------
    @pyqtSlot()
    def on_predict_clicked(self):
        predict_json = [self.company_size_predict.value(),
                        self.education_predict.currentText(),
                        self.work_city_predict.text(),
                        self.work_type_predict.currentText(),
                        self.exp_predict.value(), self.kw_predict.text()]
        label, prob, log_prob = get_predict_result(predict_json)
        if label[0]:
            self.lcdNumber.display(6000 + 6000 * prob[0][1])
        else:
            self.lcdNumber.display(6000 - 6000 * prob[0][1])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # setup stylesheet
    apply_stylesheet(app, theme='dark_yellow.xml')#light_teal dark_teal light_yellow
    lcdFontId = QFontDatabase.addApplicationFont('ui/NotoSerifSC-Light.otf')
    app.setFont(QFont(QFontDatabase.applicationFontFamilies(lcdFontId)[0]))
    app.setWindowIcon(QIcon('ui/favicon.ico'))
    win = Window()
    win.show()
    sys.exit(app.exec())
