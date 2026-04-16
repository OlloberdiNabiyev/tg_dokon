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
    keyboard.add(KeyboardButton('📁 Kategoriya tahrirlash'))
    keyboard.add(KeyboardButton('📁 Kategoriyalar ro\'yxati'))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def mahsulot_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📦 Mahsulot qo\'shish'))
    keyboard.add(KeyboardButton('📦 Mahsulot o\'chirish'))
    keyboard.add(KeyboardButton('📦 Mahsulot tahrirlash'))
    keyboard.add(KeyboardButton('📦 Mahsulotlar ro\'yxati'))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def back_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard
def user_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('savatcha🛒'))
    keyboard.add(KeyboardButton('malumot va aloqa ☎️'))
    keyboard.add(KeyboardButton('kategoriyalar📂'))
    return keyboard
    
def category_inline_keyboard():    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("SELECT name FROM categories")
    products = cursor.fetchall()
    for product in products:
        keyboard.add(KeyboardButton(product[0]))
    return keyboard

