import multiprocessing
import os
import flet as ft
import pipline
import sys
from pipline import Database,Spider,Config
import logging

class UIHandler(logging.Handler):
    def __init__(self, output_control):
        super().__init__()
        self.output_control = output_control
        self.turned_on = False

    def emit(self, record):
        if self.turned_on:
            log_entry = self.format(record)
            self.output_control.controls.append(ft.Text(log_entry))
            self.output_control.update()





class AppInf:
    Version = "v0.1.0"
    Author = "Wang Yuchao"
    Title = "邮箱提取工具"

class Int():
    def __init__(self,value):
        self.value = value

class List():
    def __init__(self,values : list):
        self.values : list = values
    
    def add(self,value):
        self.values.append(value)
    
    def clear(self):
        self.values.clear()

class String():
    def __init__(self,value):
        self.value = value




def main(page: ft.Page):
    # 日志显示窗口要提前设置
    search_log = ft.ListView(spacing=10, padding=20, auto_scroll=True, height=200)

    # 初始化数据库和日志
    def init_database():
        db = Database(Config.DATABASE_PATH)
        tables = db.get_tables()
        if len(tables) == 0:
            db.create_table("默认",Config.COLUMNS)

    init_database()
    

    def setup_logging():
        # 设置sys.stdout和sys.stderr的编码为UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

        logger = logging.getLogger('logger_all')
        logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件和控制台
        fh = logging.FileHandler(f'{Config.LOG_PATH}/{Config.TODAY}.log',encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ui_handler = UIHandler(search_log)
        ui_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(levelname)s]\t%(asctime)s - %(message)s',datefmt='%H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        ui_handler.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.addHandler(ui_handler)

        return logger

    Logger = setup_logging()

    def get_fonts():
        # 默认是黑体
        fonts = {'default': './assets/fonts/simhei.ttf'}

        # 获取字体文件，不区分大小写
        for file in os.listdir('./assets/fonts'):
            if file.endswith('.ttf',) or file.endswith('.ttc'):
                font_name = os.path.splitext(file)[0]
                fonts[font_name] = f'./assets/fonts/{file}'
            if file.endswith('.TTF',) or file.endswith('.TTC'):
                font_name = os.path.splitext(file)[0]
                fonts[font_name] = f'./assets/fonts/{file}'

        return fonts
    
    def toggle_theme(e):
        
        # 切换主题模式
        page.theme_mode = (ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK)
        # 切换图标
        theme_button.content.icon = ft.icons.NIGHTS_STAY_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.WB_SUNNY_OUTLINED
        # 刷新页面
        page.update()

    def on_nav_change(e):
        selected_index = e.control.selected_index
        content_column.controls.clear()
        if selected_index == 0:
            # content_column.controls.append(ft.Text("主页"))
            content_column.controls.append(home_image)
            content_column.controls.append(home_column)
            content_column.alignment =ft.MainAxisAlignment.CENTER,
            Logger.handlers[-1].turned_on = False
        elif selected_index == 1:
            # content_column.controls.append(ft.Text("数据库"))
            content_column.controls.append(database_text_container)
            content_column.controls.append(database_control_row)
            content_column.controls.append(database_scrollable_container)
            # content_column.horizontal_alignment =ft.CrossAxisAlignment.CENTER,
            content_column.alignment =ft.MainAxisAlignment.CENTER,
            Logger.handlers[-1].turned_on = False
        elif selected_index == 2:
            content_column.controls.append(search_text_container)
            content_column.controls.append(search_control_row)
            content_column.controls.append(search_cards_row)
            content_column.controls.append(ft.Divider(height=8,thickness=0, color=ft.colors.TRANSPARENT))
            content_column.controls.append(search_all_in_one_card)
            content_column.controls.append(ft.Divider(height=8,thickness=0, color=ft.colors.TRANSPARENT))
            content_column.controls.append(search_page_bar)
            content_column.controls.append(ft.Divider(height=8,thickness=0, color=ft.colors.TRANSPARENT))
            content_column.controls.append(search_log)
            content_column.controls.append(search_log_clean_row)
            Logger.handlers[-1].turned_on = True

            content_column.alignment = ft.MainAxisAlignment.START

            # content_column.controls.append(ft.Text("查找"))
        elif selected_index == 3:
            # content_column.controls.append(ft.Text("设置"))
            
            content_column.controls.append(ft.Row(
                [
                    ft.Row([ft.Text("路径设置",size=20,weight=ft.FontWeight.BOLD),ft.Icon(ft.icons.CACHED)]),
                    ft.Row(
                        [
                            ft.ElevatedButton("保存", on_click=on_settings_save),
                            ft.ElevatedButton("恢复默认设置", on_click=on_settings_default)
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ))
            content_column.controls.append(settings_path_card)
            content_column.controls.append(ft.Row([ft.Text("网络设置",size=20,weight=ft.FontWeight.BOLD),ft.Icon(ft.icons.WIFI)]))
            content_column.controls.append(settings_network_card)
            content_column.controls.append(ft.Row([ft.Text("爬虫设置",size=20,weight=ft.FontWeight.BOLD),ft.Icon(ft.icons.MANAGE_SEARCH)]))
            content_column.controls.append(settings_spider_card)
            content_column.alignment =ft.MainAxisAlignment.CENTER,
            Logger.handlers[-1].turned_on = False
        
        page.update()

    

    def on_datacell_tap_emails(e,row_index,col_index):
        
        # 缓存index
        database_edit_dialog_rowindex_cache.value = row_index
        database_edit_dialog_colindex_cache.value = col_index

        # 先打开编辑窗口
        # try:
        #     page.overlay.remove(database_edit_dialog)
        # except:
        #     pass
        page.overlay.clear()
        page.overlay.append(database_edit_dialog)
        database_edit_dialog.open = True
        emails = ",".join(e.control.content.content.controls[0].value.split("\n"))
        database_edit_dialog_textfield.value = emails # 窗口里的文本框内显示当前行的数据
        page.update()

        # 缓存当前index给编辑窗口
    
    def on_datacell_tap(e,row_index,col_index):
        
        # 缓存index
        database_edit_dialog_rowindex_cache.value = row_index
        database_edit_dialog_colindex_cache.value = col_index

        # 先打开编辑窗口
        # try:
        #     page.overlay.remove(database_edit_dialog)
        # except:
        #     pass
        page.overlay.clear()
        page.overlay.append(database_edit_dialog)
        database_edit_dialog.open = True
        data = e.control.content.content.value
        database_edit_dialog_textfield.value = data # 窗口里的文本框内显示当前行的数据
        page.update()

        # 缓存当前index给编辑窗口

    # 使用函数传参的方式保存index
    def create_database_table_emails_cell(init,row_index,col_index):
        return ft.DataCell(
            init,
            on_double_tap = lambda e: on_datacell_tap_emails(e,row_index,col_index)
        )
    
     # 使用函数传参的方式保存index
    def create_database_table_cell(init,row_index,col_index):
        return ft.DataCell(
            init,
            on_double_tap = lambda e: on_datacell_tap(e,row_index,col_index)
        )

    def updata_table_data(datas,table):
        database_table_data_index2id.clear()
        table.rows.clear()
        for index,(id, url, emails, last_access_time) in enumerate(datas):
            database_table_data_index2id.add(id)
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Container(content=ft.Text(index+1,size=16),width= 50)),
                        create_database_table_cell(ft.Container(content=ft.Text(url,size=16),width= 250),index,1),
                        create_database_table_emails_cell(
                            ft.Container(
                                ft.Column(
                                    [ft.Text("\n".join(emails.split(",")),size=16)],
                                    scroll=ft.ScrollMode.HIDDEN,
                                    # width= 250,
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                width= 300,
                            ),
                            row_index=index,
                            col_index=2
                        ),
                        create_database_table_cell(ft.Container(content=ft.Text(last_access_time,size=16),width= 150),index,3),
                    ]
                )
            )
        page.update()

    def parse_condition(condition_str):
        if condition_str == "无":
            condition = None
        elif condition_str == "邮箱非空":
            condition = f"emails != \'{Config.EMPTY}\'"
        elif condition_str == "邮箱为空":
            condition = f"emails = \'{Config.EMPTY}\'"
        else:
            condition = None
        return condition

    def on_tables_select(e):
        # print("on_tables_select")
        database_table_select_dropdown.error_text = None
        db = Database(Config.DATABASE_PATH)
        # table_name = e.control.value
        table_name = database_table_select_dropdown.value
        # print(type(e))

        condition_str = database_condition_select_dropdown.value
        condition = parse_condition(condition_str)
        datas = db.select_data_by_name(table_name,"id,url,emails,last_access_time",condition=condition)
        updata_table_data(datas,database_table_data_table)

        return 
    
    def get_database_tables_options():
        db = Database(Config.DATABASE_PATH)
        tables = db.get_tables()
        return [ft.dropdown.Option(table_name) for table_name in tables]
    
    def on_condition_select(e):
        condition_str = e.control.value
        condition = parse_condition(condition_str)
        db = Database(Config.DATABASE_PATH)
        table_name = database_table_select_dropdown.value
        # print(table_name)
        if not table_name:
            return
        datas = db.select_data_by_name(table_name,"id,url,emails,last_access_time",condition=condition)
        updata_table_data(datas,database_table_data_table)

        return
    
    def on_file_import(e):
        # 打开新窗口
        # e.control.page.dialog = database_file_import_dialog
        # try:
        #     page.overlay.remove(database_file_import_dialog)
        # except:
        #     pass
        page.overlay.clear()
        database_table_select_dropdown.error_text = None
        search_table_select_dropdown.error_text = None
        database_file_import_dialog_file_path_cache.value = ""
        database_file_import_dialog_file_alert.value = "" # 清除缓存
        database_file_import_dialog_file_switch.value = False

        page.overlay.append(database_file_import_dialog_file_filepicker)
        page.overlay.append(database_file_import_dialog)
        database_file_import_dialog.open = True
        page.update()
    
    def search_data(search_text):
        db = Database(Config.DATABASE_PATH)
        table_name = database_table_select_dropdown.value
        condition = parse_condition(database_condition_select_dropdown.value)
        if not condition:
            condition = f"url LIKE \'%{search_text}%\'"
        else:
            condition += f" AND url LIKE \'%{search_text}%\'"
        if not table_name:
            return
        datas = db.select_data_by_name(table_name,"id,url,emails,last_access_time",condition=condition)
        return datas


    def on_search_submit(e):
        search_text = e.data
        datas = search_data(search_text)
        updata_table_data(datas,database_table_data_table)

        # 更新搜索历史
        if search_text not in seaech_histories:
            if len(seaech_histories) < 5:
                seaech_histories.append(search_text)
            else:
                seaech_histories.pop(0)
                seaech_histories.append(search_text)
        
        # 关闭搜索框，并保留搜索内容
        database_search_bar.close_view(search_text)

        return
    
    def on_close_view_and_search(e):
        search_text = e.control.title.value
        # 关闭搜索框，并保留搜索内容
        database_search_bar.close_view(search_text)
        # 执行搜索操作
        datas = search_data(search_text)
        updata_table_data(datas,database_table_data_table)
        return

    
    def on_search_tap(e):
        database_search_bar.controls = [
            ft.ListTile(
                title=ft.Text(history),
                on_click=on_close_view_and_search
            )
            for history in seaech_histories
        ]
        database_search_bar.open_view()
    
    def clean_database_file_import_dialog_single(e):
        database_file_import_dialog_single_url.value = ""
        database_file_import_dialog_single_email.value = ""
        database_file_import_dialog_single_alert.value = ""
        database_file_import_dialog_single_url.update()
        database_file_import_dialog_single_email.update()
        database_file_import_dialog_single_alert.update()

    def clean_database_file_export_dialog(e):
        database_file_export_dialog_file_alert.value = ""
        database_file_export_dialog_file_name.value = ""
        database_file_export_dialog_file_name.update()
        database_file_export_dialog_file_alert.update()

    def clean_database_table_edit_dialog(e):
        
        database_table_edit_dialog_table_name.value = ""
        database_table_edit_dialog_alert.value = ""
        database_table_edit_dialog_table_name.update()
        database_table_edit_dialog_alert.update()
        # database_table_edit_dialog_delete_button.update()

    def on_insert_single_data(e):
        # 如果url输入为空则不执行插入操作
        if not database_file_import_dialog_single_url.value:
            database_file_import_dialog_single_url.error_text = "网址不可为空"
            database_file_import_dialog_single_url.focus()
            
            return
        # 如果没有选择表则不执行插入操作
        if not database_table_select_dropdown.value:
            database_table_select_dropdown.error_text = "请选择表"
            database_table_select_dropdown.focus()
            
            return
        db = Database(Config.DATABASE_PATH)
        table_name = database_table_select_dropdown.value
        if not table_name:
            return
        data = {
            "url" : database_file_import_dialog_single_url.value,
            "emails" : database_file_import_dialog_single_email.value,
            "last_access_time" : Config.CURRENT_TIME if database_file_import_dialog_single_email.value else Config.EMPTY
        }
        db.insert_data(table_name,data)
        on_tables_select(None) # 刷新表格
        database_file_import_dialog_single_url.value = ""
        database_file_import_dialog_single_email.value = ""
        database_file_import_dialog_single_alert.value = "插入成功"
        database_file_import_dialog_single_url.focus()
        database_file_import_dialog_single_url.update()
        database_file_import_dialog_single_email.update()
        database_file_import_dialog_single_alert.update()

    def on_single_url_textfield_change(e):
        database_file_import_dialog_single_url.error_text = ""
        database_file_import_dialog_single_url.update()

    def on_database_edit_dialog_textfield_change(e):
        database_edit_dialog_textfield.error_text = ""
        database_edit_dialog_textfield.update()

    def on_file_import_result(e):
        if not e.files:
            return
        # print(e.files)
        database_file_import_dialog_file_path_cache.value = e.files[0].path # 缓存文件路径
        file_name = e.files[0].path.split("\\")[-1]
        database_file_import_dialog_file_alert.value = f"文件已选择{file_name}"
        database_file_import_dialog_file_alert.update()

    
    def on_file_import_dialog_file_filepicker(e):
        
        database_file_import_dialog_file_filepicker.pick_files()
        
    def on_file_import_dialog_tabs_change(e : ft.ControlEvent):
        tabs_index = e.control.selected_index
        if tabs_index == 0:
            e.control.width = 500
            e.control.height = 300
        elif tabs_index == 1:
            e.control.width = 700
            e.control.height = 500
        elif tabs_index == 2:
            e.control.width = 500
            e.control.height = 300
        e.control.update()

    def on_file_export_dialog_tabs_change(e : ft.ControlEvent):
        pass

    def on_table_edit_dialog_tabs_change(e : ft.ControlEvent):
        pass

    def parse_col_index(col_index):
        if col_index == 1:
            column_name = "url"
        elif col_index == 2:
            column_name = "emails"
        elif col_index == 3:
            column_name = "last_access_time"
        else:
            return None

        return column_name

    def on_yes_database_edit_dialog(e):
        new_data = database_edit_dialog_textfield.value
        # 新数据可以为空
        
        table_name = database_table_select_dropdown.value
        if not table_name:
            return
        
        row_index = database_edit_dialog_rowindex_cache.value # 从缓存获取index
        col_index = database_edit_dialog_colindex_cache.value # 从缓存获取index

        column_name = parse_col_index(col_index)
        if not column_name:
            return

        id_ = database_table_data_index2id.values[row_index] # 从index获取id
        db = Database(Config.DATABASE_PATH)

        
        db.update_data(table_name,{column_name:new_data},condition=f"id = {id_}")
        on_tables_select(None) # 刷新表格

        # 关闭网页
        
        database_edit_dialog.open = False
        page.update()

    def on_no_database_edit_dialog(e):
        # 关闭网页

        database_edit_dialog.open = False
        page.update()

    def on_database_edit_dialog_delete(e):
        
        # try:
        #     page.overlay.remove(database_edit_dialog_delete_confirm)
        # except:
        #     pass
        page.overlay.clear()
        page.overlay.append(database_edit_dialog_delete_confirm)
        database_edit_dialog_delete_confirm.open = True
        page.update()

    def on_database_table_edit_dialog_delete(e):
        page.overlay.clear()
        page.overlay.append(database_table_edit_dialog_delete_confirm)
        database_table_edit_dialog_delete_confirm.open = True
        page.update()

    def on_yes_database_edit_dialog_delete_confirm(e):

        row_index = database_edit_dialog_rowindex_cache.value # 从缓存获取index
        col_index = database_edit_dialog_colindex_cache.value # 从缓存获取index

        column_name = parse_col_index(col_index)
        if not column_name:
            return
        
        id_ = database_table_data_index2id.values[row_index] # 从index获取id
        db = Database(Config.DATABASE_PATH)
        table_name = database_table_select_dropdown.value

        db.delete_data(table_name,condition=f"id = {id_}")
        on_tables_select(None) # 刷新表格

        database_edit_dialog_delete_confirm.open = False
        page.update()

    def on_no_database_edit_dialog_delete_confirm(e):

        database_edit_dialog_delete_confirm.open = False
        page.update()

    def on_yes_database_table_edit_dialog_delete_confirm(e):

        table_name = database_table_select_dropdown.value

        db = Database(Config.DATABASE_PATH)
        db.delete_table(table_name)
        init_database()# 如果把默认表格删除，则需要重新初始化
        database_table_select_dropdown.options = get_database_tables_options()
        search_table_select_dropdown.options = get_database_tables_options()
        database_table_select_dropdown.value = database_table_select_dropdown.options[0].key
        on_tables_select(None) # 刷新表格

        database_table_edit_dialog_delete_confirm.open = False
        page.update()

    def on_no_database_table_edit_dialog_delete_confirm(e):

        database_table_edit_dialog_delete_confirm.open = False
        page.update()

    
    def on_file_import_dialog_file_import(e):
        database_file_import_dialog.open = False
        page.update()
        file_path = database_file_import_dialog_file_path_cache.value

        if not file_path:
            return
        
        db = Database(Config.DATABASE_PATH)
        new_table = database_file_import_dialog_file_switch.value
        # 如果新建表
        if new_table:
            table_name = db.init_from_excel(excel_file=file_path)
            database_table_select_dropdown.options = get_database_tables_options()
            search_table_select_dropdown.options = get_database_tables_options()
            pipline.append_emails(db,table_name)
            if database_table_select_dropdown.value :
                on_tables_select(None)
        # 如果插入表
        else:
            table_name = database_table_select_dropdown.value
            if not table_name:
                database_file_import_dialog_file_alert.value = "您未选择任何表",
                database_table_select_dropdown.error_text = "您未选择任何表"
                database_file_import_dialog_file_alert.update()
                page.update()
                return
            
            db.add_from_excel(table_name=table_name,excel_file=file_path)
            pipline.append_emails(db,table_name)
            if database_table_select_dropdown.value :
                on_tables_select(None)

        
        page.update()


    def on_database_file_export_dialog_file_name_change(e):
        database_file_export_dialog_file_name.error_text = ""
        database_file_export_dialog_file_name.update()
    
    def on_database_table_edit_dialog_table_name_change(e):
        database_table_edit_dialog_table_name.error_text = ""
        database_table_edit_dialog_table_name.update()

    def on_database_table_edit_dialog_create(e):
        table_name = database_table_edit_dialog_table_name.value
        if not table_name:
            database_table_edit_dialog_table_name.error_text = "表名不可为空"
            database_table_edit_dialog_table_name.update()
            return
        
        db = Database(Config.DATABASE_PATH)
        table_names = db.get_tables()

        if table_name in table_names:
            database_table_edit_dialog_table_name.error_text = "表名已存在"
            database_table_edit_dialog_table_name.update()
            return
        
        try:

            db.create_table(table_name,Config.COLUMNS)

        except Exception as e:
            database_table_edit_dialog_table_name.error_text = "表名含有非法字符"
            database_table_edit_dialog_table_name.update()
            return
        
        database_table_edit_dialog_alert.value = "创建成功"
        database_table_select_dropdown.options = get_database_tables_options()
        search_table_select_dropdown.options = get_database_tables_options()
        page.update()


    
    def on_database_file_export_dialog_export(e):
        
        file_name = database_file_export_dialog_file_name.value
        # print(file_name)
        if not file_name:
            database_file_export_dialog_file_name.error_text = "文件名不可为空"
            database_file_export_dialog_file_name.update()
            return

        table_name = database_table_select_dropdown.value
        if not table_name:
            database_file_export_dialog_file_alert.value = "您未选择任何表",
            database_table_select_dropdown.error_text = "您未选择任何表"
            database_file_export_dialog_file_alert.update()
            return
        
        database_file_export_dialog.open = False
        page.update()
        db = Database(Config.DATABASE_PATH)
        if not os.path.exists(Config.EXPORT_PATH):
            os.mkdir(Config.EXPORT_PATH)
        db.export_to_excel(table_name,f"{Config.EXPORT_PATH}/{file_name}.xlsx")
        

        

    def on_file_export(e):
        page.overlay.clear()
        database_file_export_dialog_file_name.hint_text = f"保存至{Config.EXPORT_PATH}"
        database_file_export_dialog_file_alert.value = "" # 清除缓存
        
        page.overlay.append(database_file_export_dialog)
        database_file_export_dialog.open = True
        page.update()

    def on_table_edit(e):
        page.overlay.clear()
        database_table_edit_dialog_alert.value = "" 
        database_table_edit_dialog_delete_button.disabled = False if database_table_select_dropdown.value else True
        database_table_edit_dialog_delete_button.text = f"删除表格：{database_table_select_dropdown.value}" if database_table_select_dropdown.value else "请选择表"


        page.overlay.append(database_table_edit_dialog)
        database_table_edit_dialog.open = True

        page.update()

    def disable_all_search_button():
        left_nav.disabled = True
        search_log_clean_button.disabled = True
        search_table_select_dropdown.disabled = True
        search_step_card1_start.disabled = True
        search_step_card2_start.disabled = True
        search_all_in_one_start.disabled = True
        page.update()

    def enable_all_search_button():
        left_nav.disabled = False
        search_table_select_dropdown.disabled = False
        search_log_clean_button.disabled = False
        search_step_card1_start.disabled = False
        search_step_card2_start.disabled = False
        search_all_in_one_start.disabled = False
        page.update()

    def on_search_step_card1_start(e):
        table_name = search_table_select_dropdown.value
        if not table_name:
            search_table_select_dropdown.error_text = "您未选择任何表"
            search_table_select_dropdown.update()
            return
        
        disable_all_search_button()
        search_page_bar.value = None
        search_page_bar.update()

        db = Database(Config.DATABASE_PATH)
        pipline.get_html_from_db(db,table_name=table_name)

        search_page_bar.value = 1
        search_page_bar.update()
        enable_all_search_button()

    
    def on_search_step_card2_start(e):
        table_name = search_table_select_dropdown.value
        if not table_name:
            search_table_select_dropdown.error_text = "您未选择任何表"
            search_table_select_dropdown.update()
            return
        disable_all_search_button()
        search_page_bar.value = None
        search_page_bar.update()

        db = Database(Config.DATABASE_PATH)
        pipline.get_email_from_db(db,table_name=table_name)
        pipline.append_emails(db,table_name=table_name)

        search_page_bar.value = 1
        search_page_bar.update()
        enable_all_search_button()

    def on_search_all_in_one_start(e):
        table_name = search_table_select_dropdown.value
        if not table_name:
            search_table_select_dropdown.error_text = "您未选择任何表"
            search_table_select_dropdown.update()
            return
        disable_all_search_button()
        search_page_bar.value = None
        search_page_bar.update()

        db = Database(Config.DATABASE_PATH)
        pipline.get_html_from_db(db,table_name=table_name)
        pipline.get_email_from_db(db,table_name=table_name)
        pipline.append_emails(db,table_name=table_name)

        search_page_bar.value = 1
        search_page_bar.update()
        enable_all_search_button()

    def on_searche_table_select_change(e):
        search_table_select_dropdown.error_text = None
        search_table_select_dropdown.update()

    def on_search_log_clean(e):
        search_log.controls = []
        search_log.update()

    def on_settings_spider_theme_click(e):
        page.overlay.clear()
        page.overlay.append(settings_spider_theme_dialog)
        settings_spider_themes.values = [] # 奇妙的bug ：clear不行，只能重新赋值
        for theme in Config.SCHEMA_KEYWORDS:
            settings_spider_themes.add(theme)
        updata_settings_spider_theme_dialog_list_view()

        
        settings_spider_theme_dialog.open = True
        page.update()

    def on_settings_spider_contact_click(e):
        page.overlay.clear()
        page.overlay.append(settings_spider_contact_dialog)
        settings_spider_contacts.values = [] # 奇妙的bug ：clear不行，只能重新赋值
        for contact in Config.CONTACT_KEYWORDS:
            settings_spider_contacts.add(contact)
        updata_settings_spider_contact_dialog_list_view()

        settings_spider_contact_dialog.open = True
        page.update()

    def update_settings_spider_themes(e, index):
        settings_spider_themes.values[index] = e.control.value
    
    def update_settings_spider_contacts(e, index):
        settings_spider_contacts.values[index] = e.control.value

    def delete_settings_spider_themes(index):
        settings_spider_themes.values.pop(index)
        updata_settings_spider_theme_dialog_list_view()
    
    def delete_settings_spider_contacts(index):
        settings_spider_contacts.values.pop(index)
        updata_settings_spider_contact_dialog_list_view()

    def updata_settings_spider_theme_dialog_list_view():
        settings_spider_theme_dialog_list_view.controls.clear()
        for index, item in enumerate(settings_spider_themes.values):
            settings_spider_theme_dialog_list_view.controls.append(ft.Row([
                ft.TextField(value=item, expand=1, on_change=lambda e, i=index: update_settings_spider_themes(e, i),
                            hint_text="主题",height=40),
                ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, i=index: delete_settings_spider_themes(i))
            ]))
        page.update()
    
    def updata_settings_spider_contact_dialog_list_view():
        settings_spider_contact_dialog_list_view.controls.clear()
        for index, item in enumerate(settings_spider_contacts.values):
            settings_spider_contact_dialog_list_view.controls.append(ft.Row([
                ft.TextField(value=item, expand=1, on_change=lambda e, i=index: update_settings_spider_contacts(e, i),
                            hint_text="主题",height=40),
                ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, i=index: delete_settings_spider_contacts(i))
            ]))
        page.update()
    
    def on_settings_spider_theme_dialog_add_item(e):
        if settings_spider_theme_dialog_input_field.value:
            settings_spider_themes.add(settings_spider_theme_dialog_input_field.value)
            settings_spider_theme_dialog_input_field.value = ""
            updata_settings_spider_theme_dialog_list_view()
    
    def on_settings_spider_contact_dialog_add_item(e):
        if settings_spider_contact_dialog_input_field.value:
            settings_spider_contacts.add(settings_spider_contact_dialog_input_field.value)
            settings_spider_contact_dialog_input_field.value = ""
            updata_settings_spider_contact_dialog_list_view()

    def on_yes_settings_spider_theme_dialog(e):
        clean_settings_spider_themes = [theme.replace(" ", "") for theme in settings_spider_themes.values if theme]
        Config.SCHEMA_KEYWORDS = [theme for theme in clean_settings_spider_themes if theme]
        Config.write_config()


        settings_spider_theme_dialog.open = False
        page.update()

    def on_no_settings_spider_theme_dialog(e):

        settings_spider_theme_dialog.open = False
        page.update()

    def on_yes_settings_spider_contact_dialog(e):
        clean_settings_spider_contacts = [contact.replace(" ", "") for contact in settings_spider_contacts.values if contact]
        Config.CONTACT_KEYWORDS = [contact for contact in clean_settings_spider_contacts if contact]
        Config.write_config()

        settings_spider_contact_dialog.open = False
        page.update()

    def on_no_settings_spider_contact_dialog(e):

        settings_spider_contact_dialog.open = False
        page.update()

    def on_settings_save(e):
        Config.CACHE_PATH = f"{settings_cache_path.value}"
        Config.LOG_PATH = f"{settings_log_path.value}"
        Config.EXPORT_PATH = f"{settings_export_path.value}"
        http_proxy = f"{settings_http_proxy_prefix.value}{settings_http_proxy_ip.value}:{settings_http_proxy_port.value}"
        https_proxy = f"{settings_https_proxy_prefix.value}{settings_https_proxy_ip.value}:{settings_https_proxy_port.value}"
        Config.HTTP_PROXY = http_proxy
        Config.HTTPS_PROXY = https_proxy
        Config.PROXIES = {"http": http_proxy, "https": https_proxy}
        Config.TIME_OUT = int(settings_time_out.value)
        Config.write_config()
        Config.load_config()
    
    def on_settings_default(e):
        username = os.environ.get('USERNAME') 
        Config.CACHE_PATH = r"C:\Users\{}\AppData\Local\EmailExtractor\html".format(username)
        Config.LOG_PATH = r"C:\Users\{}\AppData\Local\EmailExtractor\logs".format(username)
        Config.EXPORT_PATH = r"C:\Users\{}\AppData\Local\EmailExtractor\export".format(username)
        http_proxy = "http://127.0.0.1:7890"
        https_proxy = "http://127.0.0.1:7890"
        Config.HTTP_PROXY = http_proxy
        Config.HTTPS_PROXY = https_proxy
        Config.PROXIES = {"http": http_proxy, "https": https_proxy}
        Config.TIME_OUT = 10
        Config.write_config()
        Config.load_config()

        settings_cache_path.value = r"C:\Users\{}\AppData\Local\EmailExtractor\html".format(username)
        settings_log_path.value = r"C:\Users\{}\AppData\Local\EmailExtractor\logs".format(username)
        settings_export_path.value = r"C:\Users\{}\AppData\Local\EmailExtractor\export".format(username)
        settings_http_proxy_ip.value = Config.HTTP_PROXY.split(":")[1].split("//")[1]
        settings_http_proxy_port.value = Config.HTTP_PROXY.split(":")[2]
        settings_https_proxy_ip.value = Config.HTTPS_PROXY.split(":")[1].split("//")[1]
        settings_https_proxy_port.value = Config.HTTPS_PROXY.split(":")[2]
        settings_http_proxy_prefix.value = Config.HTTP_PROXY.split(":")[0] + "://"
        settings_https_proxy_prefix.value = Config.HTTPS_PROXY.split(":")[0] + "://"
        settings_time_out.value = str(Config.TIME_OUT)
        page.update()

    def on_github_click(e):
        page.launch_url("https://github.com/Kotori-Sama/JSJ-Project")
    ####################################################################################

    page.fonts = get_fonts()
    page.theme = ft.Theme(font_family="default")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = AppInf.Title + " " + AppInf.Version

    left_nav = ft.NavigationRail(
        # min_width=100,
        min_extended_width=180,
        label_type=ft.NavigationRailLabelType.ALL,
        selected_index=0,
        group_alignment=-0.9,
        destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME, 
                    selected_icon=ft.icons.HOME_FILLED, 
                    label="主页"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.STORAGE, 
                    selected_icon=ft.icons.STORAGE_ROUNDED, 
                    label="数据库"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SEARCH,
                    selected_icon=ft.icons.SEARCH,
                    label="查找",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="设置",
                ),
            ],
        on_change=on_nav_change,
        extended = True,
        height = 600
    )
    

    theme_button = ft.Container(
        ft.IconButton(
            icon=ft.icons.NIGHTS_STAY_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.WB_SUNNY_OUTLINED,
            tooltip="切换夜间模式",
            on_click = toggle_theme
        ),
        alignment = ft.alignment.bottom_center,
        width=180    
    )



    # 数据库内容区
    database_content_column = [
        ft.DataColumn(
            ft.Text("序号"),
            on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
            
        ),
        ft.DataColumn(
            ft.Text("网站"),
            on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
        ),
        ft.DataColumn(
            ft.Text("邮箱"),
            on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
        ),
        ft.DataColumn(
            ft.Text("更新日期"),
            on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
        )
    ]

    database_table_data_index2id = List([])

    database_table_data_table = ft.DataTable(
        width=1000,
        # bgcolor="yellow",
        border=ft.border.all(1),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, "grey"),
        horizontal_lines=ft.border.BorderSide(1, "grey"),
        sort_column_index=0,
        sort_ascending=True,
        heading_row_color=ft.colors.BLACK12,
        # heading_row_height=100,
        # data_row_color={"hovered": "0x30FF0000"},
        show_checkbox_column=True,
        # divider_thickness=0,
        # column_spacing=0,
        columns = database_content_column,
        data_row_max_height=80
    )

    # 数据库滚动容器
    database_scrollable_container = ft.Container(
        content=ft.Column(
            controls=[database_table_data_table],
            scroll=ft.ScrollMode.AUTO,  # 自动显示滚动条
        ),
        height=500,  # 设置容器高度，以显示滚动条
    )

    database_text_container = ft.Container(
        content=ft.Text("数据库内容",size=20),
    )

    database_table_select_dropdown = ft.Dropdown(
        label="表格",
        hint_text="选择显示的表格名称",
        # focused_bgcolor="white",
        options = get_database_tables_options(),
        autofocus=True,
        on_change = on_tables_select,
        width=200,
        height=55,
    )

    database_condition_select_dropdown = ft.Dropdown(
        label="条件",
        hint_text="选择筛选条件",
        options = [
            ft.dropdown.Option("无"),
            ft.dropdown.Option("邮箱非空"),
            ft.dropdown.Option("邮箱为空"),
        ],
        autofocus=True,
        on_change = on_condition_select,
        width=200,
        height=55,
        value="邮箱非空",
    )

    seaech_histories = []

    database_search_bar = ft.SearchBar(
        divider_color=ft.colors.AMBER,
        bar_hint_text="搜索网站...",
        on_submit=on_search_submit,
        on_tap=on_search_tap,
        width=200,
        height=40,
        view_hint_text="搜索历史"
    )

    database_overview_control_row = ft.Row(
        controls=[
            database_table_select_dropdown,
            database_condition_select_dropdown,
            database_search_bar
        ]
    )

    database_file_control_row = ft.Row(
        controls=[
            ft.ElevatedButton("编辑",on_click=on_table_edit),
            ft.ElevatedButton("导入",on_click=on_file_import),
            ft.ElevatedButton("导出",on_click=on_file_export),
        ],
        alignment=ft.MainAxisAlignment.END
    )

    database_control_row = ft.Row(
        controls=[
            database_overview_control_row,
            database_file_control_row
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    database_file_import_dialog_single_url = ft.TextField(label="网址",hint_text="请输入网址（网址不可为空）",
                                                          on_change=on_single_url_textfield_change)
    database_file_import_dialog_single_email = ft.TextField(label="邮箱",hint_text="请输入邮箱")
    database_file_import_dialog_single_alert = ft.Text(value="",color=ft.colors.RED)

    database_file_import_dialog_file_filepicker = ft.FilePicker(on_result=on_file_import_result)
    # page.overlay.append(database_file_import_dialog_file_filepicker)
    database_file_import_dialog_file_switch = ft.Switch(label="新建表",value=False)
    database_file_import_dialog_file_alert = ft.Text(value="",color=ft.colors.RED)
    database_file_import_dialog_file_path_cache = String("")

    database_file_import_dialog_file_example = ft.DataTable(
        border=ft.border.all(1),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, "grey"),
        horizontal_lines=ft.border.BorderSide(1, "grey"),
        columns=[
            ft.DataColumn(ft.Text("网址(必填项)")),
            ft.DataColumn(ft.Text("邮箱1(选填项)")),
            ft.DataColumn(ft.Text("邮箱2(选填项)")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("https://www.example.com")),
                    ft.DataCell(ft.Text("example@example.com")),
                    ft.DataCell(ft.Text("example2@example.com")),
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("https://www.example2.com")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("example2@example2.com")),
                ]
            )
        ],
        # width=500,
    )

    database_file_import_dialog = ft.AlertDialog(
        title=ft.Text("导入数据"),
        content=ft.Tabs(
            [
                ft.Tab(
                    icon=ft.icons.ADD,
                    text="插入单条数据",
                    content=ft.Column(
                        controls=[
                            ft.Column(
                                controls=[
                                    database_file_import_dialog_single_url,
                                    database_file_import_dialog_single_email
                                ]
                            ),
                            ft.Row(
                                controls=[database_file_import_dialog_single_alert,
                                          ft.ElevatedButton("插入",on_click=on_insert_single_data)],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    )
                ),
                ft.Tab(
                    icon=ft.icons.FILE_UPLOAD,
                    text="导入文件",
                    content=ft.Column(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(value="文件格式示例：仅要求表格首列非空",color=ft.colors.BLUE_900),
                                    database_file_import_dialog_file_example,
                                ],

                            ),
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.ElevatedButton("选择文件",icon=ft.icons.FILE_UPLOAD_OUTLINED,on_click=on_file_import_dialog_file_filepicker),
                                            ft.Text(value="支持导入csv、xlsx文件",color=ft.colors.GREY_400),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER

                                    ),
                                    width=400,
                                    height=200,
                                    padding=10,
                                )
                            ),
                            ft.Row(
                                controls=[
                                    database_file_import_dialog_file_switch,
                                    database_file_import_dialog_file_alert,
                                    ft.ElevatedButton("导入",on_click=on_file_import_dialog_file_import)
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                ),
                ft.Tab(
                    text="更多导入方式敬请期待^ ^",
                    icon=ft.icons.ACCESS_TIME,
                    content=ft.Container(
                        ft.Text("更多导入方式敬请期待^ ^",size=20),
                        alignment=ft.alignment.center,
                        width=500,
                        height=300,
                    )
                    
                ),
            ],
            selected_index=0,
            animation_duration=300,
            width=500,
            height=300,
            on_change=on_file_import_dialog_tabs_change,
        ),
        on_dismiss=clean_database_file_import_dialog_single,
    )

    database_edit_dialog_textfield = ft.TextField(label="数据",hint_text="请输入新数据",on_change=on_database_edit_dialog_textfield_change)
    database_edit_dialog_rowindex_cache = Int(0)
    database_edit_dialog_colindex_cache = Int(0)


    database_edit_dialog = ft.AlertDialog(
        title=ft.Text("编辑数据"),
        content=ft.Column(
            controls=[
                database_edit_dialog_textfield
            ],
            width=400,
            height=150,
        ),
        actions=[
            ft.Row(
              controls=[
                  ft.Container(
                      ft.TextButton(content=ft.Text("删除该条数据",color="red"), on_click=on_database_edit_dialog_delete),
                  ),
                  ft.Container(
                      ft.Row(
                          controls=[
                            ft.TextButton("确定", on_click=on_yes_database_edit_dialog),
                            ft.TextButton("取消", on_click=on_no_database_edit_dialog),
                          ]
                      )
                  )
              ],
              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ],
    )

    database_edit_dialog_delete_confirm = ft.AlertDialog(
        title=ft.Text("是否删除该条数据？"),
        content=ft.Text("该操作不可逆，请谨慎操作"),
        actions=[
            ft.TextButton("确定", on_click=on_yes_database_edit_dialog_delete_confirm),
            ft.TextButton("取消", on_click=on_no_database_edit_dialog_delete_confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    database_file_export_dialog_file_name = ft.TextField(label="文件名",hint_text=f"保存至{Config.EXPORT_PATH}",on_change=on_database_file_export_dialog_file_name_change)
    database_file_export_dialog_file_alert = ft.Text(value="",color="red")
    database_file_export_dialog = ft.AlertDialog(
        title=ft.Text("导出数据"),
        content=ft.Tabs(
            [
                ft.Tab(
                    icon=ft.icons.FILE_DOWNLOAD,
                    text="导出为Excel文件",
                    content=ft.Column(
                        controls=[
                            ft.Column(
                                controls=[
                                    database_file_export_dialog_file_name
                                ]
                            ),
                            ft.Row(
                                controls=[database_file_export_dialog_file_alert,
                                          ft.ElevatedButton("导出",on_click=on_database_file_export_dialog_export)],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    )
                ),
                ft.Tab(
                    text="更多导出格式敬请期待^ ^",
                    icon=ft.icons.ACCESS_TIME,
                    content=ft.Container(
                        ft.Text("更多导出格式敬请期待^ ^",size=20),
                        alignment=ft.alignment.center,
                        width=400,
                        height=200,
                    )
                    
                ),
            ],
            selected_index=0,
            animation_duration=300,
            width=400,
            height=200,
            on_change=on_file_export_dialog_tabs_change,
        ),
        on_dismiss=clean_database_file_export_dialog,
    )


    database_table_edit_dialog_delete_confirm = ft.AlertDialog(
        title=ft.Text("是否删除该表格？"),
        content=ft.Text("该操作不可逆，请谨慎操作"),
        actions=[
            ft.TextButton("确定", on_click=on_yes_database_table_edit_dialog_delete_confirm),#on_yes_database_edit_dialog_delete_confirm),
            ft.TextButton("取消", on_click=on_no_database_table_edit_dialog_delete_confirm)#on_no_database_edit_dialog_delete_confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    database_table_edit_dialog_delete_button = ft.ElevatedButton(f"删除表格：{database_table_select_dropdown.value}"
                                          if database_table_select_dropdown.value else "请选择表格"
                                          ,on_click=on_database_table_edit_dialog_delete,
                                          disabled=False if database_table_select_dropdown.value else True)
    database_table_edit_dialog_alert = ft.Text(value="",color="red")
    database_table_edit_dialog_table_name = ft.TextField(label="表格名",hint_text="请输入表格名",on_change=on_database_table_edit_dialog_table_name_change)
    database_table_edit_dialog = ft.AlertDialog(
        title=ft.Text("编辑表格"),
        content=ft.Tabs(
            [
                ft.Tab(
                    icon=ft.icons.ADD_CARD,
                    text="新建表格",
                    content=ft.Column(
                        controls=[
                            ft.Column(controls=[database_table_edit_dialog_table_name]),
                            ft.Row(
                                controls=[database_table_edit_dialog_alert,
                                          ft.ElevatedButton("新建",on_click=on_database_table_edit_dialog_create)],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    )
                ),
                ft.Tab(
                    text="删除表格",
                    icon=ft.icons.DELETE,
                    content=ft.Container(
                        database_table_edit_dialog_delete_button,
                        alignment=ft.alignment.center,
                        width=400,
                        height=200,
                    )
                    
                ),
            ],
            selected_index=0,
            animation_duration=300,
            width=400,
            height=200,
            on_change=on_table_edit_dialog_tabs_change,#on_file_export_dialog_tabs_change,
        ),
        on_dismiss=clean_database_table_edit_dialog,
    )

    ##############################################################################################
    """ 查找 """
    search_text_container = ft.Container(content=ft.Text("爬取邮箱",size=20))
    search_table_select_dropdown = ft.Dropdown(
        label="表格",
        hint_text="选择爬取的表格名称",
        # focused_bgcolor="white",
        options = get_database_tables_options(),
        autofocus=True,
        on_change = on_searche_table_select_change,
        width=200,
        height=55,
    )

    search_overview_control_row = ft.Row(
        controls=[
            search_table_select_dropdown,
        ]
    )

    search_control_row = ft.Row(
        controls=[
            search_overview_control_row,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )


    search_step_card1_start = ft.TextButton("开始获取",on_click=on_search_step_card1_start)
    search_page_bar = ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee",value=0)
    search_step_card1 = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.MAPS_HOME_WORK_OUTLINED),
                        title=ft.Text("1. 获取主页数据",weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "获取表中网址的主页数据，将其缓存至本地。根据您数据库中网址的数量和网络状况，此步骤可能需要几分钟的时间。"
                        ),
                    ),
                    ft.Row(
                        [search_step_card1_start],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ]
            ),
            width=400,
            padding=10,
        )
    )

    search_step_card2_start = ft.TextButton("爬取邮箱",on_click=on_search_step_card2_start)
    search_step_card2 = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.ATTACH_EMAIL_OUTLINED),
                        title=ft.Text("2. 获取邮箱数据",weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "根据缓存的主页数据，获取表中网址的邮箱。此步骤将仅考虑缓存中的数据，因此您需要先完成第一步。"
                        ),
                    ),
                    ft.Row(
                        [search_step_card2_start],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ]
            ),
            width=400,
            padding=10,
        )
    )

    search_cards_row = ft.Row(
        controls=[
            search_step_card1,
            search_step_card2,
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY
    )

    search_all_in_one_start = ft.ElevatedButton("一键爬取",on_click=on_search_all_in_one_start)
    search_all_in_one_card = ft.Row(
        controls=[
            ft.Text("或者...",size=20),
            search_all_in_one_start,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    search_log_clean_button = ft.ElevatedButton("清空日志",on_click=on_search_log_clean)
    search_log_clean_row = ft.Row(
        controls=[
            search_log_clean_button,
        ],
        alignment=ft.MainAxisAlignment.END,
    )
    
    ################################################################################
    """ 设置 """
    settings_cache_path = ft.TextField(label="HTML缓存目录",height=50, border="underline",value=Config.CACHE_PATH)
    # settings_db_path = ft.TextField(label="数据库名称",height=50, border="underline",prefix="./assest/db/",value=Config.DATABASE_PATH,suffix=".db")
    settings_log_path = ft.TextField(label="日志文件目录", height=50,border="underline",value=Config.LOG_PATH)
    settings_export_path = ft.TextField(label="导出文件目录", height=50,border="underline",value=Config.EXPORT_PATH)

    settings_path_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    settings_cache_path,
                    # settings_db_path,
                    settings_log_path,
                    settings_export_path,
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=1000,
            padding=10,
        ),
        
    )

    settings_http_proxy_ip = ft.TextField(label="代理IP地址",value="127.0.0.1",width=300,height=40)
    settings_http_proxy_port = ft.TextField(label="端口",value="7890",width=150,height=40)
    settings_http_proxy_prefix = ft.RadioGroup(
                content=ft.Row(
                    controls=[
                        ft.Radio(value="http://", label="前缀：http://"),
                        ft.Radio(value="https://", label="前缀：https://"),
                    ],
                ),
                value=Config.HTTP_PROXY.split("://")[0] + "://",
            )
    setting_http_proxy = ft.Row(
        controls=[
            ft.Container(
                ft.Text("HTTP代理:"),
                alignment=ft.alignment.center
            ),
            ft.Row(
                controls=[
                    settings_http_proxy_ip,
                    ft.Text(":"),
                    settings_http_proxy_port,
                ]
            ),
            settings_http_proxy_prefix
        ],
        # alignment=ft.MainAxisAlignment.CENTER,
    )

    settings_https_proxy_ip = ft.TextField(label="代理IP地址",value="127.0.0.1",width=300,height=40)
    settings_https_proxy_port = ft.TextField(label="端口",value="7890",width=150,height=40)
    settings_https_proxy_prefix = ft.RadioGroup(
                content=ft.Row(
                    controls=[
                        ft.Radio(value="http://", label="前缀：http://"),
                        ft.Radio(value="https://", label="前缀：https://"),
                    ],
                ),
                value=Config.HTTPS_PROXY.split("://")[0] + "://",
            )
    setting_https_proxy = ft.Row(
        controls=[
            ft.Container(
                ft.Text("HTTPS代理:"),
                alignment=ft.alignment.center,
            ),
            ft.Row(
                controls=[
                    settings_https_proxy_ip,
                    ft.Text(":"),
                    settings_https_proxy_port,
                ]
            ),
            settings_https_proxy_prefix
            
        ],
        # alignment=ft.MainAxisAlignment.CENTER,
    )

    settings_time_out = ft.TextField(label="超时时间(s)",value=Config.TIME_OUT,width=300,height=50,border="underline")
    settings_network_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    setting_http_proxy,
                    setting_https_proxy,
                    settings_time_out
                ],
                spacing=15,
                # alignment=ft.MainAxisAlignment.CENTER,
                # horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=1000,
            padding=10,
        )
    )

    settings_spider_theme = ft.ListTile(
                            leading=ft.Icon(ft.icons.FILTER_ALT_OUTLINED),
                            title=ft.Text("主题识别的关键词：用于过滤主题无关的页面"),
                            trailing=ft.OutlinedButton(
                                "修改",
                                on_click=on_settings_spider_theme_click
                            )
                        )
    
    settings_spider_contact = ft.ListTile(
        leading=ft.Icon(ft.icons.CONTACT_PAGE_OUTLINED),
        title=ft.Text("联系方式识别的关键词：用于在主页中识别联系方式"),
        trailing=ft.OutlinedButton(
            "修改",
            on_click=on_settings_spider_contact_click
        )
    )
    settings_spider_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    settings_spider_theme,
                    settings_spider_contact
                ]
            )
        )
    )

    settings_spider_themes = List(Config.SCHEMA_KEYWORDS)
    settings_spider_theme_dialog_list_view = ft.Column()
    settings_spider_theme_dialog_input_field = ft.TextField(hint_text="插入关键词",height=40)
    settings_spider_theme_dialog_add_button = ft.IconButton(icon=ft.icons.ADD, on_click=on_settings_spider_theme_dialog_add_item)
    settings_spider_theme_dialog = ft.AlertDialog(
        title=ft.Text("编辑主题识别关键词"),
        content=ft.Column(
            [
                ft.Row([settings_spider_theme_dialog_input_field, settings_spider_theme_dialog_add_button],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                # ft.Column([settings_spider_theme_dialog_list_view],scroll=ft.ScrollMode.AUTO)
                ft.Container(
                    content=ft.Column(
                        [settings_spider_theme_dialog_list_view],
                        scroll=ft.ScrollMode.AUTO
                    ),
                    height=420
                )
            ],
            width=400,
            height=500,
            spacing=20
        ),
        actions=[
            ft.TextButton("确定", on_click=on_yes_settings_spider_theme_dialog),
            ft.TextButton("取消", on_click=on_no_settings_spider_theme_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: page.update()
    )

    settings_spider_contacts = List(Config.SCHEMA_KEYWORDS)
    settings_spider_contact_dialog_list_view = ft.Column()
    settings_spider_contact_dialog_input_field = ft.TextField(hint_text="插入关键词",height=40)
    settings_spider_contact_dialog_add_button = ft.IconButton(icon=ft.icons.ADD, on_click=on_settings_spider_contact_dialog_add_item)
    settings_spider_contact_dialog = ft.AlertDialog(
        title=ft.Text("编辑联系方式识别关键词"),
        content=ft.Column(
            [
                ft.Row([settings_spider_contact_dialog_input_field, settings_spider_contact_dialog_add_button],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                # ft.Column([settings_spider_theme_dialog_list_view],scroll=ft.ScrollMode.AUTO)
                ft.Container(
                    content=ft.Column(
                        [settings_spider_contact_dialog_list_view],
                        scroll=ft.ScrollMode.AUTO
                    ),
                    height=420
                )
            ],
            width=400,
            height=500,
            spacing=20
        ),
        actions=[
            ft.TextButton("确定", on_click=on_yes_settings_spider_contact_dialog),
            ft.TextButton("取消", on_click=on_no_settings_spider_contact_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: page.update()
    )

    ################################################################################
    """ 主页 """
    home_image = ft.Image(
        src="logo2.png",
        fit=ft.ImageFit.CONTAIN,
        width=500
    )
    home_res_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.WARNING),
                        title=ft.Text("免责声明", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "尊敬的用户：\n   感谢您使用本网络爬虫程序。在使用本程序之前，请仔细阅读以下免责声明：\n"+ \
                            "   1.我们不对您在使用本爬虫程序时可能遇到的任何问题或风险承担责任。您应自行承担使用本程序的风险和后果。\n"+ \
                            "   2.本爬虫程序仅供学习、研究或个人使用。未经许可，不得将本程序用于商业目的或其他非法用途。\n"+ \
                            "   3.在使用本爬虫程序时，您应尊重他人的知识产权和个人隐私，不得侵犯他人合法权益。\n"+ \
                            "   4.您不得将通过本爬虫程序获取的信息用于未经授权的目的，尤其是不得用于侵犯他人权益或违反法律法规的行为。\n"
                            "   5.使用该爬虫程序造成的一切后果，应由使用者自行承担。"
                        ),
                    ),
                ]
            ),
            width=900,
            padding=10,
        )
    )
    home_column = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("如果您喜欢我的项目，请给我一颗星", weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        content=ft.Image(
                            src="github-mark.svg",
                            fit=ft.ImageFit.CONTAIN,
                            width=24,
                            height=24
                        ),
                        on_click=on_github_click
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row([ft.Text("(或者在Issues中报告bug)",style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH,
                        decoration_thickness=1.5,
                    ),)],alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("欢迎使用EmailExtractor！"),
                        ft.Text("这是一个用于提取网站中电子邮件地址的软件。我会根据您提供的网站URL，提取出所有可能的电子邮件地址。"),
                        ft.Text("您可以在设置中自定义您需要过滤的网站主题和搜索联系方式的关键词。"),
                        ft.Text("另外，我向您提供了一个简单的数据库管理系统，您可以在这里查看和管理您提取到的电子邮件地址。"),
                    ],
                ),
                padding=40
            ),
            # ft.Divider(thickness=0,color=ft.colors.TRANSPARENT,height=10),
            home_res_card
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # 右侧内容区
    content_column = ft.Column(
        controls=[
            home_image,
            home_column
        ],
        # expand=True,
        width=1000,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    page.add(
        ft.Row(
            [
                ft.Column(
                    controls=[
                        left_nav,
                        theme_button,
                    ]
                ),
                ft.VerticalDivider(width=1),
                content_column
            ],
            expand=True
        )
    )

    
    

if __name__ == "__main__":
    
    ft.app(target=main)