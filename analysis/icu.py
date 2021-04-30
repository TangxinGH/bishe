import pandas
# from thulac import thulac

from analysis.config import stop_words_dir, custom_stop_word_file
from utils.walk_file import walk_dir


def stop_words():
    stopwords = []
    generator_file = walk_dir(stop_words_dir)

    while True:
        try:
            file_next = next(generator_file)
            words = [line.strip() for line in open(file_next, 'r', encoding='utf-8').readlines()]
            stopwords = stopwords + words
        except StopIteration:
            print("文件读取完毕,io  结束")
            return pandas.Series(stopwords)  # 结束了


def my_stop_words():
    return pandas.Series([line.strip() for line in
                          open(custom_stop_word_file, 'r',
                               encoding='utf-8').readlines()])


# def retain_genders():
#     thu1 = thulac()
#     text = """
#     <p>岗位职责：</p><p>1、充分了解高精尖中心的项目和产品，结合中心项目及产品体系，针对教育行业进行市场分析，洞察市场及学校需求，优化商务模式及产品方向；</p><p>2、负责现有合作资源关系建设、维护，建立良好合作关系；</p><p>3、负责拓展项目落地学校及区域，协调教育行业合作伙伴及业务资源，促进项目合作指标的有效达成；</p><p>4、完成上级主管领导要求的其他任务。</p><p>任职要求：</p><p>1、本科及以上学历，年龄35周岁及以下，有教育学、信息技术、经济学、管理学、心理学等学科背景者优先；</p><p>2、具有市场推广经验，线上教育相关行业经验者优先；</p><p>3、性格踏实勤恳，责任心强，具备较好的执行能力、沟通协作能力，能够承受高强度的工作压力；</p><p>4、具有学校人脉或资源者优先，教育行业市场推广或快速招商成功案例者优先。</
#     """
#     cut_t = thu1.cut(text)
#     print(cut_t)


