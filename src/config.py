# config.py
import os

class Config:
    ENV = 'development'
    DEBUG = True if ENV == 'development' else False
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///traibinh_admin.db'  # Thay đổi URI tùy theo loại cơ sở dữ liệu bạn sử dụng
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SYSTEM_PATH = 'system'
    APPLICATION_FOLDER = 'application'

config = Config()
