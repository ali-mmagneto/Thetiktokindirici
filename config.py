import os

class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
  
    ADMIN_ID =  os.environ.get("ADMIN_ID", 12345)
