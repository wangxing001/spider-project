import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
import re
import os 
from hashlib import md5


def get_page_index(offset,keyword):
    data = {
        "offset": offset,
        "format": "json",
        "keyword": keyword,
        "autoload": "true",
        "count": "20",
        "en_qc": 1,
        "cur_tab": 1
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        pass
    except RequestException:
        pass

def parse_page_index(html):
    #将字符串形式的html转换成json格式变量
    data = json.loads(html)
    if data and 'data' in data.keys():#首先判断data的关键词里有没有data
        for item in data.get('data'): 
            yield item.get('article_url') #构造生成器
            # if item.get("article_url"): #去掉None，数据过滤
                # print(item.get("article_url")) 

def get_page_detail(url):
    try:
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
        response = requests.get(url,headers=headers)#详情页需要添加headers
        if response.status_code == 200:
            print("请求详情页成功：")
            return response.text
    except RequestException:
        pass

def parse_page_detail(detail_html):
    #组图信息存储在html页面的gallery中
    soup = BeautifulSoup(detail_html,'lxml')
    title = soup.select('title')[0].get_text()
    # print(title)
    images_pattern = re.compile('gallery: JSON.parse\("(.*)"\)',re.S) #正则表达式可能存在问题(加上转义，group（）不会选择)
    result = re.search(images_pattern, detail_html)
    if result:
        print("匹配成功")
        # print(result.group(1))
        #处理匹配的gallery数据，提取图片链接
        #将\"替换成"
        test=re.sub(r'\\"',r'"',result.group(1))
        # print(test)
        data = json.loads(test)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            # print('title:',title,'images:',images,sep='\n')
            # print(type(images))#list类型
            save_url = []
            for images_url in images:
                change_url = re.sub(r'\\', r'', images_url)
                save_url.append(change_url)
            print('title:',title,'\n','images_url:',save_url)
            for item in save_url:
                download_image(item)
            print('存储图片成功')
    else:
        pass

def download_image(down_image_url):
    try:
        response = requests.get(down_image_url)
        if response.status_code == 200:
            save_image(response.content) #存储image(二进制形式)
        pass
    except RequestException:
        print('请求图片出错',down_image_url)
        return None

def save_image(content):
    file_path = '{0}/{1}.{2}'.format('image',md5(content).hexdigest(),'jpg') #md5防止图片名称重复
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content) 
            f.close()

def main():
    for i in range(10):
        html = get_page_index((i+1)*10,'街拍')

        for url in parse_page_index(html):
            if url and url[8:11]!='api':
                print('\n')
                print(url)
                detail_html = get_page_detail(url)
                if detail_html:
                    parse_page_detail(detail_html)

if __name__ == '__main__':
    main()
