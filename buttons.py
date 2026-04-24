from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db import cursor
from bot import bot

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📦 Mahsulotlar'))
    keyboard.add(KeyboardButton('📁 Kategoriyalar'))
    keyboard.add(KeyboardButton('👤 Adminlar'))
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
    btn1 = KeyboardButton('Mahsulotlar 📦')
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

def product_delete():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("""
        SELECT p.name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
    """)
    products = cursor.fetchall()
    for product in products:
        keyboard.add(KeyboardButton(product[0]))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def Admins():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('👤 Adminlar ro\'yxati')
    btn2 = KeyboardButton('👤 Admin qo\'shish')
    btn3 = KeyboardButton('👤 Admin o\'chirish')
    btn4 = KeyboardButton('🔙orqaga')
    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)
    return keyboard

def delete_admins():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("SELECT user_id FROM admins")
    admins = cursor.fetchall()

    for admin in admins:
        try:
            chat = bot.get_chat(admin[0])
            name = chat.first_name
            username = f"@{chat.username}" if chat.username else ""
        except:
            name = "Unknown"
            username = ""

        keyboard.add(KeyboardButton(f"{name} {username} | {admin[0]}"))

    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard


def category_list():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("SELECT name FROM categories")
    categories = cursor.fetchall()
    for category in categories:
        keyboard.add(KeyboardButton(category[0]))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard


def category_keyboardss():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("SELECT name FROM categories")
    categories = cursor.fetchall()
    for category in categories:
        keyboard.add(KeyboardButton(category[0]))
    keyboard.add(KeyboardButton('🔙 Orqaga'))
    return keyboard

def product_list():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cursor.execute("""
        SELECT p.name, c.name
        FROM products p
        JOIN categories c ON p.category_id = c.id
    """)
    products = cursor.fetchall()
    for product in products:
        keyboard.add(KeyboardButton(product[0]))
    keyboard.add(KeyboardButton('🔙orqaga'))
    return keyboard

def product_inline_keyboard(product_id, count, price):
    total_price = count * price

    markup = InlineKeyboardMarkup(row_width=3)

    markup.row(
        InlineKeyboardButton("➖", callback_data=f"minus_{product_id}_{count}"),
        InlineKeyboardButton(f"{count}", callback_data="count"),
        InlineKeyboardButton("➕", callback_data=f"plus_{product_id}_{count}")
    )

    markup.row(
        InlineKeyboardButton(f"💰 {total_price} so'm", callback_data="total")
    )

    markup.row(
        InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data=f"add_{product_id}_{count}")
    )

    return markup

def cart_inline_keyboard():
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton("❌ Savatni tozalash", callback_data="clear_cart")
    )

    markup.row(
        InlineKeyboardButton("🛍 Buyurtma berish", callback_data="checkout")
    )

    markup.row(
        InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")
    )

    return markup