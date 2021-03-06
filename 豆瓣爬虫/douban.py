from urllib import request
from bs4 import BeautifulSoup as bs
import re
import jieba
import pandas as pd
import numpy
import matplotlib.pyplot as plt

# % matplotlib inline
# 获取页面信息
resp = request.urlopen('https://movie.douban.com/nowplaying/hangzhou/')
html_data = resp.read().decode('utf-8')
# 分析页面信息，提取所需信息
soup = bs(html_data, 'html.parser')
nowplaying_movie = soup.find_all('div', id='nowplaying')
nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')

# 获取电影ID及名称
nowplaying_list = []
for item in nowplaying_movie_list:
    nowplaying_dict = {}
    nowplaying_dict['id'] = item['data-subject']
    for tag_img_item in item.find_all('img'):
        nowplaying_dict['name'] = tag_img_item['alt']
        nowplaying_list.append(nowplaying_dict)
# 获取电影ID对应的短评
requrl = 'https://movie.douban.com/subject/' + nowplaying_list[1]['id'] + '/comments' + '?' + 'start=0' + '&limit=20'
resp = request.urlopen(requrl)
html_data = resp.read().decode('utf-8')
soup = bs(html_data, 'html.parser')
comment_div_list = soup.find_all('div', class_='comment')
# 获取短评数据
eachCommentList = []
for item in comment_div_list:
    if item.find_all('p')[0].string is not None:
        eachCommentList.append(item.find_all('p')[0].string)
# print(eachCommentList)
# 数据清洗
comments = ''
for k in range(len(eachCommentList)):
    comments = comments + (str(eachCommentList[k])).strip()
# print(comments)
# 利用RE正则清洗掉所有符号，保留汉字
pattern = re.compile(r'[\u4e00-\u9fa5]+')
filterdata = re.findall(pattern, comments)
cleaned_comments = ''.join(filterdata)
# print(cleaned_comments)

# 统计词频率
segment = jieba.lcut(cleaned_comments)
words_df = pd.DataFrame({'segment': segment})
# print(words_df.head())

# 停用词去除
# quoting=3全不引用
stopwords = pd.read_csv("d:\pycharm\stopwords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'],
                        encoding="GB2312")
words_df = words_df[~words_df.segment.isin(stopwords.stopword)]
# print(words_df.head())

words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数": numpy.size})
words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)
# print(words_stat.head())

import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
from wordcloud import WordCloud  # 词云包

wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", max_font_size=80)  # 指定字体类型、字体大小和字体颜色
word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}
word_frequence_list = []
for key in word_frequence:
    temp = (key, word_frequence[key])
    word_frequence_list.append(temp)

wordcloud = wordcloud.fit_words(dict(word_frequence_list))
plt.imshow(wordcloud)
plt.show(wordcloud)