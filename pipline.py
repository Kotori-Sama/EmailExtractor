import os
import sys
from datetime import datetime
from tqdm import tqdm
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor

from src.database import Database
from src.spider import Spider
from src.config import Config
import logging

Config = Config()

Logger = logging.getLogger("logger_all")


def _get_html(url : str):
    '''
    子进程函数，根据url获取HTML数据,并保存到html文件
    :param url: url
    :return: url
    '''
    # db = Database(db_name) # 每个进程独立的数据库连接
    # process = multiprocessing.current_process()
    # Logger.info(f"子进程 {process.name} 开始执行，url: {url}")

    # 获取HTML数据
    spider = Spider(url, proxy=Config.PROXIES)

    try:
        html = spider.get_html()
    except Exception as e:
        # Logger.error(f" [{process.name}] 获取HTML数据失败，url: {url}")
        # db.close()
        return None
    
    if not html:
        # Logger.info(f" [{process.name}] 获取HTML数据为空，url: {url}")
        return None
    
    # 判断HTML是否符合需求主题
    if not spider.check_schema(html):
        # Logger.info(f" [{process.name}] 网站内容不符合需求主题，url: {url}")
        return None
    
    # 保存到html文件
    with open(f'{Config.CACHE_PATH}{url}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    # Logger.info(f" [{process.name}] 保存HTML数据成功，url: {url}，文件路径: {Config.CACHE_PATH}{url}.html")
    
    # db.close()
    
    return url


def get_html_from_db(db : Database, table_name : str):
    '''
    从数据库中获取url，并获取HTML数据
    :param db: 数据库对象
    :param table_name: 表名
    :return:
    '''

    Logger.info(f"开始获取表 {table_name} 中url的HTML数据")
    urls = db.select_data_by_name(table_name, 'url')
    length = len(urls)
    Logger.info(f"共 {length} 条数据")

    success = 0
    # 使用多进程获取HTML数据
    # multiprocessing.freeze_support()
    # pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
   
    # with tqdm(total=length,desc="获取HTML数据") as pbar:
    #     for url in pool.imap_unordered(_get_html, [url[0] for url in urls]):
    #         if not url:
    #             pbar.update()
    #             continue

    #         # 更新数据库
    #         try:
    #             db.update_data(table_name, {'html': f"{Config.CACHE_PATH}{url}.html",'last_access_time': Config.CURRENT_TIME}, condition=f"url = '{url}'")
    #         except Exception as e:
    #             Logger.error(f"更新数据库失败，错误信息: {e}")
    #             # 致命错误
    #             exit(1)

    #         Logger.info(f"更新数据库成功，url: {url}")
    #         success += 1
    #         pbar.update()

    # pool.close()
    # pool.join()

    # 使用线程池获取HTML数据
    with ThreadPoolExecutor(max_workers=os.cpu_count()*4) as executor:
        with tqdm(total=length, desc="获取HTML数据") as pbar:
            futures = [executor.submit(_get_html, url[0]) for url in urls]
            for future in futures:
                url = future.result()
                if not url:
                    pbar.update()
                    continue

                # 更新数据库
                try:
                    db.update_data(table_name, {'html': f"{Config.CACHE_PATH}{url}.html",'last_access_time': Config.CURRENT_TIME}, condition=f"url = '{url}'")
                except Exception as e:
                    Logger.error(f"更新数据库失败，错误信息: {e}")
                    # 致命错误
                    exit(1)

                Logger.info(f"更新数据库成功，url: {url}")
                success += 1
                pbar.update()

    Logger.info(f"获取HTML数据完成，成功获取 {success} 条数据")


def _get_email(url : str):
    '''
    子进程函数，根据url获取email
    保证url都是html不为空的，html数据保存在缓存中
    :param url: url
    :return: email
    '''
    # process = multiprocessing.current_process()
    # Logger.info(f"子进程 {process.name} 开始执行，url: {url}")

    spider = Spider(url, proxy=Config.PROXIES)
    # 使用缓存
    html = spider.get_html_from_cache(url)
    # 获取联系方式所在的url，可能为空
    contact_url = spider._redirct(spider.find_contact(html))
    # 获取email
    # 一个triky... 如果contact_url为空，则在主站中找email，而不在contact_url中找
    # get_html的鲁棒性造就了这个triky
    email_list = spider.find_email(spider.get_html(contact_url))

    Logger.info(f"获取email成功，url: {url}，email: {email_list}")

    return email_list,url

def get_email_from_db(db : Database, table_name : str):
    '''
    从数据库中获取url，并根据HTML数据获取email
    :param db: 数据库对象
    :param table_name: 表名
    :return:
    '''
    Logger.info(f"开始获取表 {table_name} 中url的email数据")
    # 找到html不为空的url
    urls = db.select_data_by_name(table_name, 'url',condition = f"html != \'{Config.EMPTY}\'")
    # html_paths = db.select_data_by_name(table_name, 'html', condition = f"html != {Config.EMPTY}")
    length = len(urls)
    Logger.info(f"共 {length} 条数据")

    success = 0
    # 使用多进程获取HTML数据
    # pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    # with tqdm(total=length,desc="获取email数据") as pbar:
    #     for email_list, url in pool.imap_unordered(_get_email, [url[0] for url in urls]):
            
    #         if len(email_list) == 0:
    #             pbar.update()
    #             continue

    #         # 更新数据库
    #         try:
    #             db.update_data(table_name, {'emails': ",".join(email_list)}, condition=f"url = \'{url}\'")
    #         except Exception as e:
    #             Logger.error(f"更新数据库失败，错误信息: {e}")
    #             Logger.error("################致命错误，程序退出################")
    #             # 致命错误
    #             exit(1)

    #         Logger.info(f"插入Email数据成功，url: {url}")
    #         success += 1
    #         pbar.update()

    # pool.close()
    # pool.join()

    # 使用线程池获取HTML数据
    with ThreadPoolExecutor(max_workers=os.cpu_count()*4) as executor:
        with tqdm(total=length, desc="获取email数据") as pbar:
            futures = [executor.submit(_get_email, url[0]) for url in urls]
            for future in futures:
                email_list, url = future.result()
                if len(email_list) == 0:
                    pbar.update()
                    continue

                # 更新数据库
                try:
                    db.update_data(table_name, {'emails': ",".join(email_list)}, condition=f"url = \'{url}\'")
                except Exception as e:
                    Logger.error(f"更新数据库失败，错误信息: {e}")
                    Logger.error("################致命错误，程序退出################")
                    # 致命错误
                    exit(1)

                Logger.info(f"插入Email数据成功，url: {url}")
                success += 1
                pbar.update()


    Logger.info(f"获取email数据完成，成功获取 {success} 条数据")

def append_emails(db : Database, table_name : str):
    '''
    后处理，将已经人工添加的email添加到数据库中
    :param db: 数据库对象
    :param table_name: 表名
    '''
    Logger.info(f"开始后处理，将已经人工添加的email添加到数据库中")

    # 找到email_1或email_2不为空的url
    datas = db.select_data_by_name(table_name, 'url,email_1,email_2,emails',condition = f"email_1 != \'{Config.EMPTY}\' or email_2 != \'{Config.EMPTY}\'")
    # urls = db.select_data_by_name(table_name, 'url',condition = f"email_1 != \'{Config.EMPTY}\'")
    length = len(datas)
    Logger.info(f"共 {length} 条数据")

    success = 0
    for data in datas:
        url = data[0]
        email_1 = data[1]
        email_2 = data[2]
        emails = data[3]
        # 更新数据库
        try:
            if emails == Config.EMPTY:
                email_set = set()
            else:
                email_set = set(emails.split(","))
            if email_1 != Config.EMPTY:
                email_set.add(email_1)
            if email_2 != Config.EMPTY:
                email_set.add(email_2)
            db.update_data(table_name, {'emails': ",".join(email_set)}, condition=f"url = \'{url}\'")
            # db.update_data(table_name, {'emails': f"{emails},{email_1},{email_2}"}, condition=f"url = \'{url}\'")
        except Exception as e:
            Logger.error(f"更新数据库失败，错误信息: {e}")
            Logger.error("################致命错误，程序退出################")
            # 致命错误
            exit(1)

        # Logger.info(f"后处理成功，url: {url}")
        success += 1

    Logger.info(f"后处理完成，成功处理 {success} 条数据")


if __name__ == "__main__":
    
    db = Database(Config.DATABASE_PATH)
    # print(os.cpu_count())
    # table_name = db.init_from_excel(excel_file="./example/test.xlsx")
    get_html_from_db(db,table_name="test")
    # Logger.info("#"*50)
    # Logger.info("#"*10+"获取HTML数据完成"+ "#"*10)
    # Logger.info("#"*50)
    # get_email_from_db(db,table_name=table_name)
    # append_emails(db,table_name="test")
    # db.merge_table("test_4","test_5")
    # db.export_to_excel("test_10","./example/test_9.xlsx")