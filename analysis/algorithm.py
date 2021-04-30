import jieba.analyse
import numpy
import pymongo
from bokeh.plotting import figure
from efficient_apriori import apriori
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from analysis.config import reserve_word_file
from utils.parse_yaml import global_config

jieba.load_userdict(reserve_word_file)  # 用户字典

db_config = global_config.get('global_database').get('db').get(global_config.get('global_data_source'))  # 得到节点
myclient = pymongo.MongoClient(db_config.get('mongo_url'))
mydb = myclient[db_config.get('db_name')]
mycol = mydb[db_config.get('col')]


def db_mon(kw, max_rows=1000):
    """
    返回拼接的职位描述字段
    :param max_rows:
    :param kw:
    :return: 返回所有文档相加
    """
    # 查找文档
    posts = mycol.find({'kw': kw}, {'职位描述': 1, '_id': 0}).limit(max_rows)
    # 处理相加
    return '\n'.join(v.get('职位描述') for v in posts if v.get('职位描述') is not None)


def k_m(text, ture_k):
    """

    :param text: 完整的文本
    :param ture_k: k值
    :return: tuple(k_means_sum,score,clusters)
    """
    text_cut = " ".join(jieba.cut(text))
    text_li = [num for num in text_cut.split('\n') if num.strip() != '']  # 分组

    # k-meanspip install -U scikit-learn
    count_v1 = CountVectorizer()
    X = count_v1.fit_transform(text_li)
    # 然后再TF-IDF 预处理
    X = TfidfTransformer().fit_transform(X).toarray()
    # https://stackabuse.com/text-classification-with-python-and-scikit-learn/
    # boken = list(tuple())
    # for ture_k in range(2, 6):
    k_means = KMeans(n_clusters=ture_k)
    k_means.fit(X)
    labels = k_means.predict(X)

    clusters = {}
    n = 0
    for item in labels:
        if item in clusters:
            clusters[item].append(text_li[n])
        else:
            clusters[item] = [text_li[n]]
        n += 1

    k_means_sum = k_means.inertia_  # 样本到最近聚类中心的距离总和 。误差平方和。SSE值
    print(k_means_sum, 'SSE值')
    score = k_means.score(X)  # Calinski-Harabasz 分数值，代表聚合效果
    print(score, '分数')
    print(clusters, '\n', '聚类后')
    # boken.append((ture_k, k_means_sum, score, clusters))
    # text_rank(clusters)
    # x = list(zip(*boken))[0]
    # y = list(zip(*boken))[1]
    # p = figure(title="手肘法", x_axis_label='x', y_axis_label='y')
    # p.line(x, y, legend_label="SSE.", line_width=2)
    # show(p)
    return k_means_sum, score, clusters


def text_rank(clusters):
    """

    :param clusters: 聚类后的
    :return: 返回一个list 的boken 图像对象
    """
    # 还有完整的文本？整个职位的。先聚类。后text rank  xxxxxx

    list_p = list()
    for k, v in clusters.items():
        x_dic = {}
        for weight, w in jieba.analyse.textrank((''.join(v)).replace(' ', ''), topK=10, withWeight=True,
                                                allowPOS=('ns', 'n', 'vn', 'v')):
            print('%s %s' % (weight, w))
            x_dic[weight] = w
        weight = list(x_dic.values())
        kw = list(x_dic.keys())
        dot = figure(title="k text rank", tools="",
                     y_range=[0, 1.2], x_range=kw, plot_width=490, plot_height=270)
        dot.segment(x0=kw, y0=0, x1=kw, y1=weight, line_width=2, line_color="green", )
        dot.circle(kw, weight, size=15, fill_color="orange", line_color="green", line_width=3, )
        list_p.append(dot)
    return list_p


def online_ap(kw, columns, min_support=0.5, min_confidence=1, max_rows=1000):

    inter = numpy.array([0, 3000, 3001, 6000, 6001, 9000, 9001, 12000, 12001, 15000, 9999999])
    inter_exp = numpy.array([0, 3, 4, 7, 10, 9999999])

    # 查找文档
    posts = mycol.find({'kw': kw}, columns).limit(max_rows)
    # 处理 hash
    if len(columns) == 2:
        transactions = [tuple(jieba.cut(list(v.values()))) for v in posts if v is not None]
    else:
        transactions = list()
        for v in posts:
            li_tu = list()
            for k, i in v.items():
                if type(i) == list:  # 列表的话再解一下。
                    li_tu += i
                else:
                    if type(i) == dict:  # 不可hash 类
                        pass
                        # li_tu.append( str(i.values()) ) # 粗暴一点
                    else:
                        if k == '薪酬':
                            s_where = numpy.where(inter <= i)
                            start = inter[s_where[-1].max()]
                            li_tu.append(str(start) + '以上工资')
                        if k == '经验':
                            s_exp = numpy.where(inter_exp <= i)
                            start = inter[s_exp[-1].max()]
                            li_tu.append(str(start) + '以上经验')

                        else:
                            li_tu.append(i)
            transactions.append(tuple(li_tu))
        # transactions = [tuple(v.values()) for v in posts if v is not None]

    itemsets, rules = apriori(transactions, min_support=min_support, min_confidence=min_confidence)
    return itemsets, rules  # [{eggs} -> {bacon}, {soup} -> {bacon}]


if __name__ == '__main__':
    # analysis_text = db_mon('jobs', '物业经理')
    # k_m(analysis_text)  # 聚类
    online_ap('物业经理', {'职位描述': 1, '薪酬': 1, 'location': 1, '工作城市': 1, '福利待遇': 1, '_id': 0})  # 检查columns为0 1
