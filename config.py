import os

class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
  
    APP_ID = int(os.environ.get("ADMIN_ID", 12345))
