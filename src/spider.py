import logging
import re
import requests
from typing import Dict
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.config import Config
# from config import Config
Config = Config()

Logger = logging.getLogger("logger_all")


class Spider:
    def __init__(self, url : str, proxy : dict = None):
        '''
        url: 主页的url
        proxy: 代理服务器
        该类中函数的url参数为空时，都会从默认是self.url
        该类中函数的html参数为空时，都会从默认是从self.url获取html
        '''
        self.proxy = proxy
        self.url = url # 主页的url
    
    def _valid(self):     
        '''
        判断self.url是否合法，如果不合法则添加http头
        ''' 

        # 判断url是否合法，如果不合法则添加http头
        if self.url.startswith(Config.HTTP_HEAD) or self.url.startswith(Config.HTTPS_HEAD):
            return
        
        try:
            valid_url = Config.HTTPS_HEAD + self.url
            response = requests.get(valid_url, proxies = self.proxy,timeout = Config.TIME_OUT)
            response.raise_for_status() # 如果状态码不是200，则抛出异常
            self.url = valid_url
            return 
        except requests.exceptions.RequestException as e:
            valid_url = Config.HTTP_HEAD + self.url #请求错误则使用http头重定向
            self.url = valid_url
            return

    
    def _redirct(self, url : str):
        # 判断url是否合法，如果不合法则使用主页重定向
        try:
            response = requests.get(url, proxies = self.proxy,timeout = Config.TIME_OUT)
            response.raise_for_status() # 如果状态码不是200，则抛出异常
            return response.url
        except requests.exceptions.RequestException as e:
            url = url[1:] if url.startswith("/") and self.url.endswith("/") else url
            url = "/" + url if not self.url.endswith("/") and not url.startswith("/") else url
            url = self.url + url #请求错误则使用主页url重定向
            return url

    def _get_html(self, url : str):
        try: 
            Logger.info(f"正在访问: {url}")
            response = requests.get(url, proxies = self.proxy,timeout = Config.TIME_OUT)
            response.raise_for_status() # 如果状态码不是200，则抛出异常

        except requests.exceptions.ConnectionError as e:
            # print(f"链接错误: {e}")
            Logger.error(f"url: {url}\t链接错误: {e}")
            return Config.EMPTY
        
        except requests.exceptions.RequestException as e:
            # print(f"请求错误: {e}")
            Logger.error(f"url: {url}\t请求错误: {e}")
            return Config.EMPTY
        return response.text

    def get_html(self, url : str = Config.EMPTY):
        
        home_page_flag = url == Config.EMPTY

        if home_page_flag: # 如果url为空，则使用self.url
            url = self.url

        # 如果是有scheme的url，则直接返回
        if urlparse(url).scheme:
            return self._get_html(url)  
        
        # 如果是没有scheme的url，则添加头
        # Logger.info(f"正在尝试添加https头: {url}")
        valid_url = Config.HTTPS_HEAD + url #尝试添加https头
        html = self._get_html(valid_url)
        if not html:
            # Logger.info(f"正在尝试添加http头: {url}")
            valid_url = Config.HTTP_HEAD + url #请求错误则使用http头
            html = self._get_html(valid_url)
        Logger.info(f"获取到HTML: {valid_url}")

        if home_page_flag: # 如果是主页，则更新主页
            self.url = valid_url

        return html
        

        
    
    @staticmethod
    def get_html_from_cache(url : str = Config.EMPTY):
        '''
        从缓存中获取网页的html
        :param url: 网页的url
        :return: 网页的html
        '''
        if not url:
            return Config.EMPTY

        try:
            with open(Config.CACHE_PATH + f"{url}.html", 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            Logger.error(f"缓存文件不存在: {e}")
            return Config.EMPTY
        except Exception as e:
            Logger.error(f"读取缓存文件失败: {e}")
            return Config.EMPTY
        

    def find_contact(self,html : str = Config.EMPTY):
        '''
        根据提供的html，找到联系方式所在的url
        如果html为空，则获取主页的html
        :param html: 提供的html
        :return: 联系方式所在的url
        '''
        # Logger.info("正在寻找联系方式所在的URL")
        if not html: # 如果html为空，则获取主页的html
            Logger.info("[find_contact] HTML为空，正在获取主页的HTML")
            try:
                html = self.get_html()
            except Exception as e:
                Logger.error(f"[find_contact] 获取主页的HTML失败: {e}")
                return Config.EMPTY
        
        soup = BeautifulSoup(html, 'html.parser')

        # 根据关键词找到联系方式的url
        for keyword in Config.CONTACT_KEYWORDS:
            for link in soup.find_all('a'):
                # print(link.text)
                if keyword.lower() in link.text.lower():
                    contact_url = link.get('href')
                    if contact_url:
                        Logger.info(f"联系方式所在的URL: {contact_url}")
                        return contact_url

        # Logger.info("未找到联系方式所在的URL")
        return Config.EMPTY
    
    def find_email(self,html : str = Config.EMPTY):
        '''
        根据提供的html，找到邮箱
        如果html为空，则获取主页的html
        :param html: 提供的html
        :return: 邮箱列表
        '''
        email_list = []

        # 如果html为空，则获取主页的html
        if not html:
            Logger.info("[find_email] HTML为空，正在获取主页的HTML")
            try:
                html = self.get_html()
            except Exception as e:
                Logger.error(f"[find_email] 获取主页的HTML失败: {e}")
                return email_list

        soup = BeautifulSoup(html, 'html.parser')
    
        for link in soup.find_all():
            if link.name == 'script':
                continue
            # 如果文本中包含邮箱，则添加到email_list中
            text = link.text
            emails = re.findall(Config.EMAIL_RE, text)

            for email in emails:
                if email not in email_list and not email.endswith(Config.IMAGE_TYPE):
                    email_list.append(email)
        
        Logger.info(f"找到的邮箱列表: {email_list}")

        return email_list

    def check_schema(self,html : str):
        '''
        检查网站内容是否符合主题需求
        :param html: 网站内容
        :return: 是否符合主题需求
        '''

        if not html:
            Logger.info("[check_schema] HTML为空，正在获取主页的HTML")
            try:
                html = self.get_html()
            except Exception as e:
                Logger.error(f"[check_schema] 获取主页的HTML失败: {e}")
                return False

        soup = BeautifulSoup(html, 'html.parser')

        # 根据关键词判断是否符合主题需求
        all_text = soup.get_text()
        for keyword in Config.SCHEMA_KEYWORDS:
            if keyword.lower() in all_text.lower():
                Logger.info(f"网站内容包含关键词: {keyword}")
                return True
        
        return False



if __name__ == '__main__':
    url = 'www.ambitec.cl'

    spider = Spider(url, Config.PROXIES)
    html= spider.get_html()
    print(html[:500])
    # # spider._valid()
    # # print(f"主页的url: {spider.url}")

    # contact_url = spider._redirct(spider.find_contact())
    # print(f"联系方式的url: {contact_url}")

    # email_list = spider.find_email(spider.get_html(contact_url))
    # print(f"邮箱列表: {email_list}")