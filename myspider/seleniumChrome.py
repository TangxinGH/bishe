import json
import logging
import os
import random
import sys
import time

# import pydevd_pycharm
import validators
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from spiders.jobInfo import JobInfoSpider
from spiders.config import job_details_handle_data_dir, seleniumChrome_category_dir, chrome_user_dir, chromedriver_dir

# opt.headless = True   无界面
# pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)  # 连接调试服务器并挂起
from utils.walk_file import walk_dir

options = webdriver.ChromeOptions()  # 获取谷歌浏览器选项
if len(sys.argv) == 0:
    options.add_argument('--proxy-server=127.0.0.1:8080')  # 以8080端口启动谷歌浏览器
else:
    print('selenium里的参数为{}'.format(sys.argv))

options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
options.add_argument("--no-sandbox")  # bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
options.add_argument('--user-data-dir=' + chrome_user_dir)  # 指定用户文件夹
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(executable_path=chromedriver_dir,
                          options=options)  # 使用修改后的浏览器选项启动浏览器
# 借鉴移除Selenium中的window.navigator.webdriver的内容
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})


# --------------------------------职位列表-----------------------------------------------------------

def get_kws():
    """
    得到职位名称   大类有#   数组有可能为空
    :return:
    """
    with open(seleniumChrome_category_dir, 'r', encoding='UTF-8') as f:
        code_list = f.readlines()
        list = []
        for line in code_list:
            if line != '#':  # 总大类去掉
                list.append(line.strip('\n'))  # 去掉换行
        return list


kws = get_kws()


def check_next_button():
    try:
        for button in driver.find_element_by_class_name("pagination").find_elements_by_tag_name("button"):
            if button.text == "下一页":
                return button
    except Exception as ex:
        logging.error(ex)  # page-empty可能没有职位了
        print(time.strftime("%Y-%m-%d %H:%M:%S") + "下一页" + "按钮没见有?，1 继续")
        # if s == 1:
        #     pass


def clear_input_content(input_e):
    """
    value是改变不了的，只能输入事件来，应该是绑定之类的
    :param input_e:
    :return:
    """
    input_e.click()  # 选中
    # 方法一：双击输入框，再输入新的内容
    ActionChains(driver).double_click(input_e).perform()  # 有三击的吗？三个click()连起来？
    input_e.send_keys(Keys.BACKSPACE)  # back_pace????
    if input_e.get_attribute("value") == "":
        return True
    else:
        # 方法二：通过键盘全选，然后直接输入新的内容，就不用clear了
        input_e.send_keys(Keys.CONTROL, 'a')
        input_e.send_keys(Keys.BACKSPACE)  # 清空
        if input_e.get_attribute("value") == "":
            return True


def do_climb():
    # Tips    pydevd_pycharm.settrace()  # 在需要断点的地方调用一次pydevd_pycharm.settrace(), 后面的代码就可以正常断点了，
    driver.get("https://sou.zhaopin.com/")
    # 等待
    for type in kws:
        if type.startswith("#"):  # 中断继续 直接在文件中注释，然后再撤消回去就行
            continue  # 跳过
        time.sleep(random.randint(3, 5))

        wait_element("""//*[@id="filter-hook"]/div/div[1]/div/div[1]/input""", "input_type")  # to# 等待元素出现函数
        driver.execute_script(
            """document.querySelector("#filter-hook > div > div.query-search > div > div.query-search__content-input__wrap > input").click()""")  # 点击输入框，！！
        input = driver.find_element_by_xpath("""//*[@id="filter-hook"]/div/div[1]/div/div[1]/input""")

        if clear_input_content(input) is not True:
            s = input("无法清空输入框，请手动清空，输入1继续")
            if s == 1:
                pass
        # input.clear()#清空不起作用
        input.send_keys(type)  # 模拟键盘输入
        time.sleep(random.randint(1, 5))
        driver.find_element_by_xpath("""//*[@id="filter-hook"]/div/div[1]/div/button/i""").click()  # 点击搜索

        for i in range(24):  # 2n个城市
            # if type=="算法工程师" and i<16: #这个有问题，只能完成第一次 ，还是会有20次
            #     continue #跳过已经climb的，i是无法賦值的,所以只能continue 不是其它的
            wait_element("""//*[@id="filter-hook"]/div/div[2]/div[1]/div[1]""", "下拉按钮")  # to# 元素img是否可用
            driver.execute_script(
                """document.querySelector("#filter-hook > div > div.query-location > div > div:nth-child(1) > img").click()""")  # 点击 下拉城市img
            wait_element("""//*[@id="filter-hook"]/div/div[2]/div[2]/div[1]/ul""",
                         "元素城市是否可用")  # to# 元素城市是否可用 query-city 或者list-box比较好driver.find_element_by_css_selector("#filter-hook > div > div.query-location > div.query-city > div.list-box > ul")
            if driver.find_element_by_xpath("""//*[@id="filter-hook"]/div/div[2]/div[1]/div[1]""").get_attribute(
                    "class") == "content-s__item content-s__item--active":
                # 说明城市列表激活了
                pass
            else:
                input(time.strftime("%Y-%m-%d %H:%M:%S") + "没有激活，请手动激活城市列表，任意键继续")
            # wait_elemnt_clickable("""//*[@id="filter-hook"]/div/div[2]/div[2]/div[1]/ul""","不展开的话为空") #不展开的话为空
            # 判断一下是否有这些多个城市，可能会变
            city_select = driver.find_element_by_css_selector(
                "#filter-hook > div > div.query-location > div.query-city > div.list-box > ul").find_elements_by_tag_name(
                "li")
            if len(city_select) > i:
                city_select[i].click()  # 点击城市
            else:
                break  # 退出城市循环，下一个职位

            time.sleep(random.randint(3, 8))  # to# 先睡眠一会 然后等待元素出现 visibility_of
            wait_element("""//*[@id="filter-hook"]/div/div[2]/div[1]/div[1]""", "下拉按钮")  # ?

            while True:
                time.sleep(random.randint(2, 6))
                # tips 用下一页这个词代替 find_element_by_link_text('下一页') 更健壮 等待文本的wait出现 EC.text_to_be_present_in_element((By.ID, "operations_monitoring_tab_current_ct_fields_no_data"), "No data to display")？？
                # wait_element("""//*[@id="positionList-hook"]/div/div[31]/div/div/button[2]""","下一页按钮") # to# 检查下一页按钮是否存在
                # wait_element_text("button","标签button 元素下一页","下一页"),这个不行
                next_button = check_next_button()
                if next_button is None:  # 没有的情况也可能是因为一条数据都没有,看页面就知道了
                    logging.warning(time.strftime(
                        "%Y-%m-%d %H:%M:%S") + "next_button" + "没有?，修改代码然后热更新？， 下一个城市")  # driver.execute_script 来修改代理，或者之前在浏览器中修改,记得改回来
                    try:
                        if driver.find_element_by_class_name("page-empty") is not None:
                            break  # 说明一页数据也没有下一个城市
                    except Exception as ex:
                        # 有异常说明，没有这个元素，即不空数据，也不没有下一按钮
                        s = input("有异常说明，没有这个元素，即不空数据，也不没有下一按钮,按1继续")
                        if s == 1:
                            pass

                if next_button.get_attribute("class") == 'btn soupager__btn':  #
                    # 下一页可点击
                    next_button.click()  # 下一页
                    # to# 等待元素出现
                    time.sleep(random.randint(3, 6))
                else:
                    break


def wait_element_text(tag_name, myDynamicElement, text):
    try:
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.TAG_NAME, tag_name), text))
    except Exception as ex:
        print(ex)
        s = input(time.strftime("%Y-%m-%d %H:%M:%S") + myDynamicElement + "超时了，1 继续")
        if s == 1:
            pass


def wait_element(xpath, myDynamicElement):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except Exception as ex:
        print(ex)
        s = input(time.strftime("%Y-%m-%d %H:%M:%S") + myDynamicElement + "超时了，1 继续")
        if s == 1:
            pass


def wait_elemnt_clickable(xpath, myDynamicElement):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except Exception as ex:
        print(ex)
        s = input(time.strftime("%Y-%m-%d %H:%M:%S") + myDynamicElement + "超时了?，1 继续")
        if s == 1:
            pass


# ------------------------------job_detail--------------------------------------------

def get_next_job_url():
    """得到列表,使用生成器，yield 生成器函数
    数组的话就可以 重复值覆盖，其它不行 os.fork 什么清洗去重都是假的
    """
    file_path_iterator = walk_dir(job_details_handle_data_dir)  # 获得迭代器
    while True:
        try:
            file_path = next(file_path_iterator)  # 得到一条路径
            with open("current_jobinfo_json_file.txt", 'a', encoding='UTF-8') as f:  # 追加形式
                f.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S") + "当前处理文件位置：" + str(file_path))  # 记录当前位置
            with open(str(file_path), 'r', encoding='UTF-8') as f:
                iter_f = iter(f)  # 创建迭代器
                for line in iter_f:  # 遍历文件内容，一行行遍历，读取文本
                    if str(line).startswith("#"):
                        continue  # 跳过
                    else:
                        try:
                            job_overviews = json.loads(line)
                            for item_job in job_overviews.get('data').get('list'):
                                yield item_job.get('positionUrl')  # 保存堆栈并返回 url
                        except Exception as ex:
                            logging.error("json转换出错，job_info_climb ing ")
                            pass

        except StopIteration:
            break  # 结束了


def record_log_error_jobinfo(type, string):
    with open("record_log_error_jobinfo.txt", 'a', encoding='UTF-8') as f:
        f.write(type + "##" + string)
        f.write("\n")
        f.flush()


def do_job_info_climb():
    """爬取职位详细信息
    """
    time.sleep(random.randint(8, 10))  # debug，先让mitmproxy启动先
    item_urls_iterator = get_next_job_url()  # 得到一个迭代器
    j = 0
    while True:
        j = j + 1
        with open("item_url_count.txt", 'w') as f:
            f.write(str(j))  # 当前处理了多少url
        time.sleep(random.randint(1, 10))
        try:
            item_url = next(item_urls_iterator)  # 对迭代器进行取下一个
            logging.info(item_url + "打印itemurl为")
            if item_url is None or item_url == '':
                logging.error("没有url ，检查，中止")
                record_log_error_jobinfo("itemNonenull", item_url)  # logging.error("记录信息") 记录错误到文件
                break
            if validators.url(item_url):  # 如果 url合法的话
                pass
            else:
                logging.error("url错误" + item_url)
                record_log_error_jobinfo("urlerror", item_url)  # 记录错误到文件
                continue  # 跳过
            selenium_get_html(item_url)
            # try:
            #     driver.get(item_url)
            # except Exception as ex:
            #     with open("timeout_get_url.txt", 'a', encoding="UTF-8") as f:#可能是失败的url
            #         f.write(item_url)
            #         f.write("\n")
            #         f.flush()
            #     print("超时记录下失败的url") #During handling of the above exception, another exception occurred:  ex 是不能to str 的？？
            time.sleep(random.randint(2, 10))

        except StopIteration:
            break  # 结束了


# ----------------另一种方法------------------ 直接selenium----------
def selenium_get_html(item_url, ii=0):
    """
    递归，ii 不要传
    :param item_url: 要访问的url
    :param ii:
    :return:
    """
    time.sleep(random.randint(1, 4))
    try:
        driver.get(item_url)
    #     two way :
    #      p_url = item_url.rstrip() # remove https://stackoverflow.com/questions/275018/how-can-i-remove-a-trailing-newline
    #         # print('purl: ', p_url.rstrip('\n'), f"window.location.href='{p_url}'")
    #
    #         driver.execute_script(f"window.location.href='{p_url}'")  # get
    #         time.sleep(random.randint(3, 10))
    #         for j in range(20): # most  40s
    #             state = driver.execute_script("return document.readyState")
    #             if state == 'complete' or state == 'interactive' or state == 'loaded':
    #                 break
    #             else:
    #                 time.sleep(random.randint(1, 2))
    #                 if j == 19:
    #                     # 两次都不行，记录下
    #                     with open("selenium_timeout_get_url.txt", 'a', encoding="UTF-8") as f:  # 可能是失败的url
    #                         f.write(item_url)
    #                         f.write("\n")
    #                         f.flush()
    #                     print(
    #                         "超时记录下失败的url")  # During handling of the above exception, another exception occurred:  ex 是不能to str 的？？
    #                     return  # 放弃
    except Exception as ex:
        #   再试一次
        if ii == 0:
            selenium_get_html(item_url, ii + 1)  # 递归
            return  # 这一次肯定不要了，交给下一次
        else:  # 两次都不行，记录下
            with open("selenium_timeout_get_url.txt", 'a', encoding="UTF-8") as f:  # 可能是失败的url
                f.write(item_url)
                f.write("\n")
                f.flush()
            print(
                "超时记录下失败的url")  # During handling of the above exception, another exception occurred:  ex 是不能to str 的？？
            return  # 放弃
    try:
        scripts = driver.find_elements_by_tag_name("script")
    except Exception as ex:
        print('no get the document script give up ')
        return  # 放弃
    try:
        jobinfo_spider = JobInfoSpider("jobinfo" + time.strftime("%H%M%S"), scripts, item_url)
        jobinfo_spider.start()  # 开启线程处理数据
    except Exception as ex:
        print(ex)
        print("Error: 无法启动线程")

    time.sleep(random.randint(1, 5))


if __name__ == '__main__':
    do_job_info_climb()
