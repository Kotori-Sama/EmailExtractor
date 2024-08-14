import json
from datetime import datetime
import os

class Config:
    # 单例模式
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        
        try :
            with open('./src/config.json', 'r', encoding='utf-8') as file:
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

        # if not os.path.exists(self.CACHE_PATH):
        #     os.makedirs(self.CACHE_PATH)
