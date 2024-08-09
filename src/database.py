import sqlite3
from datetime import datetime
import pandas as pd
import logging
import re

from src.config import Config

Logger = logging.getLogger("logger_all")

Config = Config()

# SQLite保留关键字列表
Reserved_keywords = set([
    'ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS',
    'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN', 'BY', 'CASCADE',
    'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT', 'CONFLICT', 'CONSTRAINT',
    'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE',
    'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DROP',
    'EACH', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL',
    'FOR', 'FOREIGN', 'FROM', 'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE',
    'IN', 'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT', 'INTO',
    'IS', 'ISNULL', 'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'NATURAL', 'NO',
    'NOT', 'NOTNULL', 'NULL', 'OF', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER', 'PLAN', 'PRAGMA',
    'PRIMARY', 'QUERY', 'RAISE', 'RECURSIVE', 'REFERENCES', 'REGEXP', 'REINDEX', 'RELEASE',
    'RENAME', 'REPLACE', 'RESTRICT', 'RIGHT', 'ROLLBACK', 'ROW', 'SAVEPOINT', 'SELECT', 'SET',
    'TABLE', 'TEMP', 'TEMPORARY', 'THEN', 'TO', 'TRANSACTION', 'TRIGGER', 'UNION', 'UNIQUE',
    'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE', 'WITH', 'WITHOUT'
])

class Database:
    def __init__(self, db_name):
        self.name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    @property
    def _get_name(self):
        return self.name

    def create_table(self, table_name : str, columns : list):
        '''
        创建表，如果表已存在则删除
        :param table_name: 表名
        :param columns: 列名
        :return: None
        '''
        delete_query = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(delete_query)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, table_name : str, data : dict):
        '''
        插入数据
        :param table_name: 表名
        :param data: 数据
        :return: None
        '''
        keys = ', '.join(data.keys())
        values = ', '.join([f"'{v}'" for v in data.values()]) # 将字典的值转换为字符串
        query = f"INSERT INTO {table_name} ({keys}) VALUES ({values})"
        self.cursor.execute(query)
        self.conn.commit()

    def close(self):
        '''
        关闭数据库连接
        :return: None
        '''
        self.conn.close()
        # self.cursor.close()
        # Logger.info("数据库连接已关闭")

    def select_data(self, table_name : str, condition : str = None):
        '''
        查询数据
        :param table_name: 表名
        :param condition: 条件
        :return: 查询结果
        '''
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def select_data_by_name(self, table_name : str, column_name : str ,condition : str = None):
        '''
        查询数据
        :param table_name: 表名
        :param column_name: 列名
        :param condition: 条件
        :return: 查询结果
        '''
        query = f"SELECT {column_name} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        # print(query)
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def update_data(self, table_name : str, data : dict, condition : str):
        '''
        更新数据
        :param table_name: 表名
        :param data: 数据
        :param condition: 条件
        :return: None
        '''
        set_str = ', '.join([f"{k} = '{v}'" for k, v in data.items(
        )])  # 将字典的键值对转换为字符串
        query = f"UPDATE {table_name} SET {set_str} WHERE {condition}"
        # print(query)
        self.cursor.execute(query)
        self.conn.commit()

    # def update_data_by_name(self, table_name : str, column_name : str, data : str, condition : str):

    def delete_data(self, table_name : str, condition : str):
        '''
        删除数据
        :param table_name: 表名
        :param condition: 条件
        :return: None
        '''
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query)
        self.conn.commit()

    def table_exists(self, table_name : str):
        '''
        判断表是否存在
        :param table_name: 表名
        :return: True or False
        '''
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self.cursor.execute(query)
        return self.cursor.fetchone() is not None
    

    def init_from_excel(self, excel_file : str):
        '''
        以下是创建初始数据库表的代码，我们根据一个excel表格文件来初始化urls数据库
        该数据库中预期包含多个表，每个表代表一个月份，表中的数据包括序号主键，url，邮箱1，邮箱2，最后访问时间和html

        该初始化用excel表格的要求如下：
        1. 你可以随意命名excel表格文件，表名将根据excel文件名自动生成
        2. 如果有多个sheet，则所有sheet都应符合该要求，且所有数据将会被插入到同一个表中
        3. 每个sheet的第一行为表头，包含网址，邮箱1，邮箱2，最后访问时间和html
            （名称可变，但要求顺序符合，网址为必填项，其余为选填项）
        4. 每个sheet的数据从第二行开始
        5. 每行数据为一条记录，包含url，邮箱1，邮箱2，最后访问时间和html
        6. 每个单元格的数据为字符串类型
        '''
        
        def validate_name(name : str):
            # 移除字符串中的空格
            name = name.replace(' ', '_')
            # 移除字符串中的非法字符
            name = re.sub(r'[\s!@#$%^&*(){}[\]:;.,<>?|`~-—。，’“”‘’]', '_', name)

            # 如果名称是保留关键字，则添加前缀
            if name.upper() in Reserved_keywords:
                name = f"tbl_{name}"

            # 截断过长的名称
            max_length = 255
            if len(name) > max_length:
                name = name[:max_length]
            
            return name


        try: 
            # 读取excel文件
            excel_data = pd.ExcelFile(excel_file)
            Logger.info(f"成功读取excel文件{excel_file}")

        except Exception as e:
            # print(f"Error: {e}")
            Logger.error(f"Error: {e}")
            return
        
        # 创建表
        table_name = validate_name(excel_file.split('/')[-1].split('.')[0])

        # 如果表已存在,则在表名后添加序号
        if self.table_exists(table_name):
            Logger.info(f"表{table_name}已存在，正在创建新表")
            table_name = f"{table_name}_{len(self.select_data('sqlite_master'))}"
            Logger.info(f"新表名为{table_name}")

        # Config.COLUMNS = ['id INTEGER PRIMARY KEY', 'url TEXT NOT NULL', 'email_1 TEXT', 'email_2 TEXT', 'last_access_time TEXT', 'html TEXT','emails TEXT']
        self.create_table(table_name, Config.COLUMNS)

        # 遍历每个sheet
        for sheet_name in excel_data.sheet_names:

            # 获取当前sheet的数据
            df = excel_data.parse(sheet_name)
            data = df.values.tolist()

            for row in data:

                 # 修正数据格式
                for i in range(len(Config.COLUMNS)-1):
                    if i < len(row) and pd.isna(row[i]):
                        row[i] = ''
                    else:
                        row.append('')

                # 构造插入数据
                insert_data = dict(zip([col.split(' ')[0] for col in Config.COLUMNS[1:]], row))

                self.insert_data(table_name, insert_data)
        
        Logger.info(f"数据库初始化完成，表名为{table_name}")

        return table_name

    
if __name__ == '__main__':
    db = Database('../db/urls.db')
    db.init_from_excel(excel_file="../example/test.xlsx")

