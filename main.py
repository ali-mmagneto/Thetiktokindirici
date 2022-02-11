import os, configparser, requests
import sqlite3
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tiktok_downloader import snaptik
from Config import Config
else:
    from config import Config

config = configparser.ConfigParser()
admin_id = Config.ADMIN_ID
TOKEN = '{Config.BOT_TOKEN}'

with sqlite3.connect('database.db') as con:
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM users')
    except:
        cur.execute('CREATE TABLE users(user_id INT)')
    try:
        cur.execute('SELECT * FROM stats')
    except:
        cur.execute('CREATE TABLE stats(download_count INT)')
        cur.execute('INSERT INTO stats VALUES(0)')
if con:
    con.commit()
    con.close()

def new_user(user_id):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        user = cur.execute(f'SELECT * FROM users WHERE user_id={user_id}').fetchall()
        if len(user) == 0:
            cur.execute(f'INSERT INTO users VALUES({user_id})')
            con.commit()
        else:
            pass
    if con:
        con.close()

def get_users_count():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        result = cur.execute('SELECT * FROM users').fetchall()
    if con:
        con.close()
    return result

def get_users():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        result = []
        for user in cur.execute('SELECT * FROM users').fetchall():
            result.append(user[0])
    if con:
        con.close()
    return result

def add_new_download():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        new = int(cur.execute('SELECT * FROM stats').fetchone()[0])+1
        cur.execute(f'UPDATE stats SET download_count={new}')
        con.commit()
    if con:
        con.close()

def get_downloads():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        result = int(cur.execute('SELECT * FROM stats').fetchone()[0])
    if con:
        con.close()
    return result

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def download_video(video_url, name):
    r = requests.get(video_url, allow_redirects=True)
    content_type = r.headers.get('content-type')
    if content_type == 'video/mp4':
        open(f'./videos/video{name}.mp4', 'wb').write(r.content)
    else:
        pass


if not os.path.exists('videos'):
    os.makedirs('videos')

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    new_user(message.chat.id)
    await bot.send_message(chat_id=message.chat.id,
                           text="""Merhaba\n\nSana TikToktan logosuz video indirmen için yardım edicem.\nSadece bana videonun bağlantısını gönder.\n\nMade By: @mmagneto""",
                           parse_mode="HTML",
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup( [ [InlineKeyboardButton('Sahip', url=f"https://t.me/mmagneto"),
                                                                                       InlineKeyboardButton('Kaynak Kod 😉', url='https://github.com/ali-mmagneto/Thetiktokindirici') ] ]  ) ) 
@dp.message_handler(commands='send')
async def command_letter(message):
    if str(message.chat.id) in admin_id:
        await bot.send_message(message.chat.id, f"*Bülten başladı \nBot, bülten tamamlandığında sizi bilgilendirecektir*", parse_mode='Markdown')
        receive_users, block_users = 0, 0
        text = message.text.split()
        if len(text) > 1:
            try:
                lst = get_users()
                cache = ''
                for string in text[1::]:
                    cache += string+' '
                for user in lst:
                    await bot.send_message(user, cache)
                    receive_users += 1
            except:
                 block_users += 1
        await bot.send_message(message.chat.id, f"*Haber bülteni tamamlandı *\n"
                                                              f"bir ileti aldı: *{receive_users}*\n"
                                                              f"Engellenen bot: *{block_users}*", parse_mode='Markdown')

@dp.message_handler(commands='help')
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Bağlantıyı TikTok videosundan kopyalayın ve bana gönderin.')


@dp.message_handler(commands=['stats'])
async def statistika_command(message: types.Message):
    if str(message.chat.id) in admin_id:
        sk = get_downloads()
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Kullanıcı sayısı : {len(get_users_count())} \nToplam istek sayısı: {sk}')
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Yöneticiler için')

@dp.message_handler(commands=['send'])
async def statistika_command(message: types.Message):
    if str(message.chat.id) in admin_id:
        sk = get_downloads()
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Kullanıcı sayısı: {len(get_users_count())} \nİstek Sayısı: {sk}')
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Yöneticiler için')


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    new_user(message.chat.id)
    if message.text.startswith('https://www.tiktok.com'):
        await bot.send_message(chat_id=message.chat.id, text='Bekle İndiriyom...')
        video_url = message.text
        try:
            snaptik(video_url).get_media()[0].download(f"./videos/result_{message.from_user.id}.mp4")
            path = f'./videos/result_{message.from_user.id}.mp4'
            add_new_download()
            await bot.delete_message(message.chat.id, message.message_id)
            with open(f'./videos/result_{message.from_user.id}.mp4', 'rb') as file:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=file.read(),
                    caption='@TikTokVideoDownRobot ile indirildi.',
                    reply_markup=InlineKeyboardMarkup( [ [InlineKeyboardButton('Destek Ol Yada Olma', url=f"https://t.me/mmagneto3") ] ]  ) 
                )
            os.remove(path)
        except Exception as e:
            print(e)
            await bot.send_message(chat_id=message.chat.id,
                                   text='İndirme hatası, yanlış bağlantı, video silinmiş veya bulamadım.')
    elif message.text.startswith('https://vm.tiktok.com') or message.text.startswith('http://vm.tiktok.com'):
        await bot.send_message(chat_id=message.chat.id, text='Bekle İndiriyom...')
        video_url = message.text
        try:
            add_new_download()
            snaptik(video_url).get_media()[0].download(f"./videos/result_{message.from_user.id}.mp4")
            path = f'./videos/result_{message.from_user.id}.mp4'
            with open(f'./videos/result_{message.from_user.id}.mp4', 'rb') as file:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=file.read(),
                    caption='@TikTokVideoDownRobot ile indirildi.', 
                    reply_markup=InlineKeyboardMarkup( [ [InlineKeyboardButton('Destek Ol Yada Olma', url=f"https://t.me/mmagneto3") ] ]  ) 
                )
            await bot.delete_message(message.chat.id, message.message_id + 1)
            os.remove(path)
        except Exception as e:
            print(e)
            await bot.send_message(chat_id=message.chat.id,
                                   text='İndirme hatası, yanlış bağlantı, video silinmiş veya bulamadım.')
    else:
        await bot.send_message(chat_id=message.chat.id, text='Ne Diyon aq bir Tiktok videosu bağlantısı at.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
