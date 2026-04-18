from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db import cursor

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📦 Mahsulotlar'))
    keyboard.add(KeyboardButton('📁 Kategoriyalar'))
    return keyboard

def category_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📁 Kategoriya qo\'shish'))
    keyboard.add(KeyboardButton('📁 Kategoriya o\'chirish'))
    keyboard.add(KeyboardButton('📁 Kategoriyalar ro\'yxati'))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def mahsulot_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📦 Mahsulot qo\'shish'))
    keyboard.add(KeyboardButton('📦 Mahsulot o\'chirish'))
    keyboard.add(KeyboardButton('📦 Mahsulotlar ro\'yxati'))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def back_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def user_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = KeyboardButton('📦 Mahsulotlar')
    btn2 = KeyboardButton('savatcha🛒')
    btn3 = KeyboardButton('malumot va aloqa ☎️')
    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    return keyboard
    
def category_delete():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("SELECT name FROM categories")
    products = cursor.fetchall()
    for product in products:
        keyboard.add(KeyboardButton(product[0]))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

