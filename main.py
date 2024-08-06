import flet as ft
from datetime import datetime
from src.database import Database
import logging

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

    logger = logging.getLogger('logger_all')
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件和控制台
    fh = logging.FileHandler(f'./logs/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log')
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

if __name__ == "__main__":
    
    db = Database('./db/urls.db')
    db.init_from_excel(excel_file="./example/test.xlsx")
    # ft.app(main)