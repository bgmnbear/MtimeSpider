import os
import requests
from pyquery import PyQuery as pq

from utils import log


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def cached_url(url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    filename = '{}.html'.format(url.split('/top100', 1)[-1])
    # /
    # \
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
        return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def get(url):
    return cached_url(url)


def download_image(url, filename):
    # 通过 url 获取到该图片的数据并写入文件
    r = requests.get(url)

    folder = 'image'
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)

    with open(path, 'wb') as f:
        f.write(r.content)


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        download_image(m.cover_url, filename)


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    log('div', type(div), div)
    e = pq(div)
    log('e', type(e), e)

    # 小作用域变量用单字符
    m = Movie()
    log('title', e('.title'))
    m.name = e('img').attr('alt')
    m.score = e('.total').text() + e('.total2').text()
    m.quote = e('.mt3').text()
    m.cover_url = e('img').attr('src')
    # log('pic', type(e('.pic')), type(e('.pic').find('em')), e('.pic'))
    m.ranking = e('.number em').text()
    return m


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    r = requests.get(url)
    page = r.content
    # log('page:', page)
    e = pq(page)
    items = e('.top_list li')
    # 调用 movie_from_div
    # log('items:', items)
    movies = [movie_from_div(i) for i in items]
    return movies


def get_movies(url):
    movies = movies_from_url(url)
    print('top100 movies', movies)
    save_cover(movies)


def main():
    # 单独处理第一页的内容
    url = 'http://www.mtime.com/top/movie/top100/'
    get_movies(url)

    for i in range(2, 11):
        url = 'http://www.mtime.com/top/movie/top100/index-{}.html'.format(i)
        get_movies(url)


if __name__ == '__main__':
    main()
