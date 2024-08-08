from datetime import datetime


class Config:

    # System
    TODAY = datetime.now().strftime("%Y-%m-%d")
    CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    CACHE_PATH = f"./html/"

    # Network
    HTTP_HEAD = 'http://'
    HTTPS_HEAD = 'https://'

    HTTP_PROXY = "http://127.0.0.1:7890"
    HTTPS_PROXY = "http://127.0.0.1:7890"
    PROXIES = {
        "http": HTTP_PROXY,
        "https": HTTPS_PROXY,
    }

    TIME_OUT = 10

    # Database
    COLUMNS = [
        'id INTEGER PRIMARY KEY', 
        'url TEXT NOT NULL', 
        'email_1 TEXT', 
        'email_2 TEXT', 
        'last_access_time TEXT', 
        'html TEXT',
        'emails TEXT'
    ]
    DATABASE_PATH = f"./db/urls.db"


    # Program
    EMPTY = ''
    CONTACT_KEYWORDS = [
        'Contact', # 英语
        'Contacto', # 西班牙语
        'Contact Us', # 英语
        'Contactez-nous', # 法语
        'Kontakt', # 德语
        'Contatto', # 意大利语
        'Контакт', # 俄语
        'контакт', # 俄语
        '联系', # 日语
        'コンタクト', # 日语
        '連絡', # 日语
        '연락', # 韩语
        'الاتصال' # 阿拉伯语
    ]
    
    IMAGE_TYPE = (".jpeg", ".jpg", ".exif", ".tif", ".tiff", ".gif", ".bmp", ".png", ".ppm",
			".pgm", ".pbm", ".pnm", ".webp", ".hdr", ".heif", ".bat", ".bpg", ".cgm", ".svg")
    EMAIL_RE = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}'