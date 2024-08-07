import sys
import time
import flet as ft
from datetime import datetime
from tqdm import tqdm
import multiprocessing
from multiprocessing import Process, Queue

from src.database import Database
from src.spider import Spider
import logging

class Constant:
    HTTP_PROXY = "http://127.0.0.1:7890"
    HTTPS_PROXY = "http://127.0.0.1:7890"
    PROXIES = {
        "http": HTTP_PROXY,
        "https": HTTPS_PROXY,
    }
    CURRENT_TIME = datetime.now().strftime("%Y-%m-%d")
    TIME_OUT = 10

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
    fh = logging.FileHandler(f'./logs/{Constant.CURRENT_TIME}.log',encoding='utf-8')
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

def get_html_by_url(url : str):
    '''
    子进程函数，根据url获取HTML数据
    :param url: url
    :return: url
    '''
    # db = Database(db_name) # 每个进程独立的数据库连接
    process = multiprocessing.current_process()
    Logger.info(f"子进程 {process.name} 开始执行，url: {url}")

    # 获取HTML数据
    spider = Spider(url, proxy=Constant.PROXIES)
    try:
        html = spider.get_html()
    except Exception as e:
        Logger.error(f" [{process.name}] 获取HTML数据失败，url: {url}")
        # db.close()
        return None
    
    if not html:
        Logger.info(f" [{process.name}] 获取HTML数据为空，url: {url}")
        return None
    
    # 保存到html文件
    with open(f'./html/{url}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    Logger.info(f" [{process.name}] 保存HTML数据成功，url: {url}，文件路径: ./html/{url}.html")
    
    # db.close()
    return url

def worker_with_timeout(url, queue):

    try:
        result = get_html_by_url(url)
        queue.put(result)
    except Exception as e:
        queue.put(None)

    return

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
        for url in pool.imap_unordered(get_html_by_url, [url[0] for url in urls]):
            if not url:
                pbar.update()
                continue
            # 更新数据库
            try:
                db.update_data(table_name, {'html': f"./html/{url}.html"}, condition=f"url = '{url}'")
            except Exception as e:
                Logger.error(f"更新数据库失败，错误信息: {e}")
                # 致命错误
                exit(1)

            Logger.info(f"更新数据库成功，url: {url}")
            success += 1
            pbar.update()

    # results = []
    # with tqdm(total=length,desc="获取HTML数据") as pbar:
    #     for url in urls:
    #         url = url[0]
    #         result = pool.apply_async(get_html_by_url, args=(url,))
    #         results.append((result, url))
    #         pbar.update()

    #     # 等待所有结果  

    #     for result, url in results:
    #         try:
    #             html_content = result.get(timeout=10)  # 设置超时时间为10秒
    #         except multiprocessing.TimeoutError:
    #             Logger.error(f"获取HTML数据超时，url: {url}")
    #             continue
    #         if not html_content:
    #             continue
            
    #         # 更新数据库
    #         try:
    #             db.update_data(table_name, {'html': f"./html/{url}.html"}, condition=f"url = '{url}'")
    #         except Exception as e:
    #             Logger.error(f"更新数据库失败，错误信息: {e}")
    #             # 致命错误
    #             exit(1) 
            
    # results = pool.starmap(updata_db_by_url, [(url[0], db._get_name ,table_name) for url in urls])

    pool.close()
    pool.join()

    Logger.info(f"获取HTML数据完成，成功获取 {success} 条数据")


if __name__ == "__main__":
    
    db = Database('./db/urls.db')
    db.init_from_excel(excel_file="./example/test.xlsx")
    # ft.app(main)
    get_html_from_db(db,table_name="test")