import json
from datetime import datetime
import os

class AppConfig:
    # 单例模式
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        
        try :
            with open('./assets/config.json', 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                for key, value in config_data.items():
                    setattr(self, key, value)
        except Exception as e:
            with open('./config.json', 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                for key, value in config_data.items():
                    setattr(self, key, value)
        
        self.TODAY = datetime.now().strftime("%Y-%m-%d")
        self.CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.IMAGE_TYPE = tuple(self.IMAGE_TYPE)

        if not os.path.exists(self.CACHE_PATH):
            os.makedirs(self.CACHE_PATH)
        if not os.path.exists(self.LOG_PATH):
            os.makedirs(self.LOG_PATH)
        if not os.path.exists(self.DATABASE_PATH_FLORDER):
            os.makedirs(self.DATABASE_PATH_FLORDER)
        if not os.path.exists(self.EXPORT_PATH):
            os.makedirs(self.EXPORT_PATH)
    
    def write_config(self):
        with open('./assets/config.json', 'w', encoding='utf-8') as file:
            json.dump(self.__dict__, file, indent=4, ensure_ascii=False)

    def reload_config(self):
        self.load_config()


