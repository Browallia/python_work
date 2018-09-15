import urllib.parse
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup
from hashlib import md5
from multiprocessing import Pool
import re
import requests
import json
import pymongo
import os
from 头条mongo import *

client = pymongo.MongoClient(MONGO_URL,connect=False)
db = client[MONGO_DB]



def get_page_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 3,
        'from': 'gallery'
    }
    url = "https://www.toutiao.com/search_content/?" + urllib.parse.urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引页出错")
        return None

def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass


def get_page_detail(url):
    try:
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"}
        response = requests.get(url,headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错",url)
        return None

def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    tit= soup.select('title')[0].get_text()
    print(tit)
    images_pattern = re.compile('gallery: JSON.parse\\((.*?)\\)',re.S)
    result = re.search(images_pattern,html)
    if result:
        data = json.loads(json.loads(result.group(1)))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:
                download_images(image)
            return{
                'title': tit,
                'url': url,
                'images': images
            }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print("储存的MongoDB成功",result)
        return True
    return False

def download_images(url):
    print("正在下载",url)
    try:
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"}
        response = requests.get(url,headers=header)
        if response.status_code == 200:
            save_images(response.content)
        return None
    except RequestException:
        print("请求图片出错",url)
        return None

def save_images(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()
def main(offset):
    html = get_page_index(offset,"路人女主的养成方法")
    for url in parse_page_index(html):
        html1 = get_page_detail(url)
        if html1:
            result = parse_page_detail(html1,url)
            if result:save_to_mongo(result)


if __name__ == "__main__":
    groups = [X*20 for X in range(GROUP_START,GROUP_END+1)]
    pool = Pool()
    pool.map(main,groups)