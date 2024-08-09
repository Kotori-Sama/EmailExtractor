import sys
import time
import flet as ft
from datetime import datetime
from tqdm import tqdm
import multiprocessing


from src.database import Database
from src.spider import Spider
from src.config import Config
import logging

Config = Config()

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        ft.Row(
            [
                ft.IconButton(ft.icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

def setup_logging():
    # 设置sys.stdout和sys.stderr的编码为UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    logger = logging.getLogger('logger_all')
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件和控制台
    fh = logging.FileHandler(f'./logs/{Config.TODAY}.log',encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s]\t%(asctime)s - %(message)s',datefmt='%H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

Logger = setup_logging()


def _get_html(url : str):
    '''
    子进程函数，根据url获取HTML数据,并保存到html文件
    :param url: url
    :return: url
    '''
    # db = Database(db_name) # 每个进程独立的数据库连接
    process = multiprocessing.current_process()
    Logger.info(f"子进程 {process.name} 开始执行，url: {url}")

    # 获取HTML数据
    spider = Spider(url, proxy=Config.PROXIES)

    try:
        html = spider.get_html()
    except Exception as e:
        Logger.error(f" [{process.name}] 获取HTML数据失败，url: {url}")
        # db.close()
        return None
    
    if not html:
        Logger.info(f" [{process.name}] 获取HTML数据为空，url: {url}")
        return None
    
    # 判断HTML是否符合需求主题
    if not spider.check_schema(html):
        Logger.info(f" [{process.name}] 网站内容不符合需求主题，url: {url}")
        return None
    
    # 保存到html文件
    with open(f'./html/{url}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    Logger.info(f" [{process.name}] 保存HTML数据成功，url: {url}，文件路径: ./html/{url}.html")
    
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
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
   
    with tqdm(total=length,desc="获取HTML数据") as pbar:
        for url in pool.imap_unordered(_get_html, [url[0] for url in urls]):
            if not url:
                pbar.update()
                continue

            # 更新数据库
            try:
                db.update_data(table_name, {'html': f"./html/{url}.html",'last_access_time': Config.CURRENT_TIME}, condition=f"url = '{url}'")
            except Exception as e:
                Logger.error(f"更新数据库失败，错误信息: {e}")
                # 致命错误
                exit(1)

            Logger.info(f"更新数据库成功，url: {url}")
            success += 1
            pbar.update()

    pool.close()
    pool.join()

    Logger.info(f"获取HTML数据完成，成功获取 {success} 条数据")


def _get_email(url : str):
    '''
    子进程函数，根据url获取email
    保证url都是html不为空的，html数据保存在缓存中
    :param url: url
    :return: email
    '''
    process = multiprocessing.current_process()
    Logger.info(f"子进程 {process.name} 开始执行，url: {url}")

    spider = Spider(url, proxy=Config.PROXIES)
    # 使用缓存
    html = spider.get_html_from_cache(url)
    # 获取联系方式所在的url，可能为空
    contact_url = spider._redirct(spider.find_contact(html))
    # 获取email
    # 一个triky... 如果contact_url为空，则在主站中找email，而不在contact_url中找
    # get_html的鲁棒性造就了这个triky
    email_list = spider.find_email(spider.get_html(contact_url))

    Logger.info(f" [{process.name}] 获取email成功，url: {url}，email: {email_list}")

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
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    with tqdm(total=length,desc="获取email数据") as pbar:
        for email_list, url in pool.imap_unordered(_get_email, [url[0] for url in urls]):
            
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

    pool.close()
    pool.join()

    Logger.info(f"获取email数据完成，成功获取 {success} 条数据")



if __name__ == "__main__":
    
    db = Database(Config.DATABASE_PATH)
    table_name = db.init_from_excel(excel_file="./example/test.xlsx")
    get_html_from_db(db,table_name=table_name)
    Logger.info("#"*50)
    Logger.info("#"*10+"获取HTML数据完成"+ "#"*10)
    Logger.info("#"*50)
    get_email_from_db(db,table_name=table_name)