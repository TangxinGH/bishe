from analysis.icu import stop_words, my_stop_words
import pandas as pd
stop_word = stop_words()
my_word = my_stop_words()

combine_np = pd.concat([my_word, stop_word]).apply(lambda x: x.strip()).to_numpy()


def del_stop_word(s):
    text = s
    for value in combine_np:
        text = text.replace(value, '')  # 先删除自己的停用词

    # 分词，分成数组？？？
    # text_li = jieba.cut(text)  # 返回list
    # text = {'original': text, 'cut_li': list(text_li)}  # 空格分隔 数组
    # text = thu1.cut(text, text=True)  # thu1 词性好
    return text