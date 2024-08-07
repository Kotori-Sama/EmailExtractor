import logging
import requests
from typing import Dict
from bs4 import BeautifulSoup
from urllib.parse import urlparse

Logger = logging.getLogger("logger_all")

class Constant:
    EMPTY = ''
    HTTP_HEAD = 'http://'
    HTTPS_HEAD = 'https://'

class Spider:
    def __init__(self, url : str, proxy : dict = None):
        self.proxy = proxy
        self.url = self._valid(url)
    
    def _valid(self, url : str):      
        # 判断url是否合法，如果不合法则添加http头
        if url.startswith(Constant.HTTP_HEAD) or url.startswith(Constant.HTTPS_HEAD):
            return url
        
        return Constant.HTTPS_HEAD + url

    def get_html(self):
        try: 
            Logger.info(f"正在访问: {self.url}")
            response = requests.get(self.url, proxies = self.proxy)
            response.raise_for_status() # 如果状态码不是200，则抛出异常

        except requests.exceptions.ConnectionError as e:
            # print(f"链接错误: {e}")
            Logger.error(f"链接错误: {e}")
            return Constant.EMPTY
        
        except requests.exceptions.RequestException as e:
            # print(f"请求错误: {e}")
            Logger.error(f"请求错误: {e}")
            return Constant.EMPTY
        
        return response.text
    
    def get_html_and_save(self, file_name : str):
        html = self.get_html()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def find_contact(self):
        html = self.get_html()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find('a', href = '/contacto')

if __name__ == '__main__':
    url = 'www.fb.org'

    http_proxy = "http://127.0.0.1:7890"
    https_proxy = "http://127.0.0.1:7890"
    proxies = {
        "http": http_proxy,
        "https": https_proxy,
    }
    spider = Spider(url, proxies)
    html = spider.get_html()
    # print(html)
    print(spider.url)