from telebot import TeleBot
from config import TOKEN, ADMINS_ID
from buttons import admin_keyboard, user_keyboard,category_keyboard, mahsulot_keyboard, category_delete,back_keyboard
from db import cursor,conn
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in ADMINS_ID:
        bot.send_message(message.chat.id, 'assalomu alaykum admin', reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, 'assalomu alaykum', reply_markup=user_keyboard())

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriyalar')
def go_categories(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Kategoriyalar bo'limiga xush kelibsiz!", reply_markup=category_keyboard())

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulotlar')
def go_products(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Mahsulotlar bo'limiga xush kelibsiz!", reply_markup=mahsulot_keyboard())
    else:
        bot.send_message(message.chat.id, "Mahsulotlar bo'limiga xush kelibsiz! \n\n kategoriyalarni tanlang:", reply_markup=category_keyboard())

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriyalar ro\'yxati')
def show_categories(message):
    cursor.execute("SELECT id, name FROM categories ORDER BY id DESC")
    categories = cursor.fetchall()
    if categories:
        response = "📁 Kategoriyalar ro'yxati:\n\n\n"
        for category in categories:
            response += f"ID: {category[0]}, Nomi: {category[1]}\n\n"
        bot.send_message(message.chat.id, response,reply_markup=back_keyboard())
    
    if not categories:
        bot.send_message(message.chat.id, "❌ Hozircha kategoriyalar mavjud emas.")

@bot.message_handler(func=lambda message: message.text == '📦 Mahsulotlar ro\'yxati')
def show_products(message):
    cursor.execute("""
        SELECT p.id, p.name, p.price, p.quantity, p.description, c.name 
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id
    """)
    products = cursor.fetchall()
    if message.from_user.id in ADMINS_ID:
        if products:
            response = "📦 Mahsulotlar ro'yxati:\n\n"
            for product in products:
                full_description = product[4] if product[4] else ""
                words = full_description.split()
                if len(words) > 15:
                    short_desc = " ".join(words[:15]) + "..."
                else:
                    short_desc = full_description
                    
                response += (f"🆔 ID: {product[0]}\n"
                            f"🛒 Nomi: {product[1]}\n"
                            f"💰 Narxi: {product[2]} so'm\n"
                            f"🔢 Soni: {product[3]}\n"
                            f"📝 Tavsifi: {short_desc}\n"
                            f"📂 Kategoriyasi: {product[5]}\n\n")
            
            bot.send_message(message.chat.id, response, reply_markup=back_keyboard())
        else:
            bot.send_message(message.chat.id, "❌ Hozircha mahsulotlar mavjud emas.")

@bot.message_handler(func=lambda message:message.text == '🔙orqaga')
def go_back(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulot qo\'shish')
def add_product(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Mahsulot qo'shish bo'limiga xush kelibsiz! Iltimos, mahsulot nomini kiriting:",reply_markup=back_keyboard())
        bot.register_next_step_handler(message, process_product_name)

def process_product_name(message):
    product_name = message.text
    if message.text != '🔙orqaga':
        bot.send_message(message.chat.id, "Mahsulot narxini kiriting:")
        bot.register_next_step_handler(message, process_product_price, product_name)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

def process_product_price(message, product_name):
    if message.text != '🔙orqaga':
        try:
            product_price = int(message.text)
            bot.send_message(message.chat.id, "Mahsulot sonini kiriting:")
            bot.register_next_step_handler(message, process_product_quantity, product_name, product_price)
        except ValueError:
            bot.send_message(message.chat.id, "Iltimos, narxni raqam sifatida kiriting.")
            bot.register_next_step_handler(message, process_product_price, product_name)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())    

def process_product_quantity(message, product_name, product_price):
    if message.text != '🔙orqaga':
        try:
            product_quantity = int(message.text)
            bot.send_message(message.chat.id, "Mahsulot tavsifini kiriting:")
            bot.register_next_step_handler(message, process_product_description, product_name, product_price, product_quantity)
        except ValueError:
            bot.send_message(message.chat.id, "Iltimos, sonni raqam sifatida kiriting.")
            bot.register_next_step_handler(message, process_product_quantity, product_name, product_price)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

def process_product_description(message, product_name, product_price, product_quantity):
    if message.text != '🔙orqaga':
        product_description = message.text
        bot.send_message(message.chat.id, "Iltimos, mahsulot rasmini yuboring (foto):")
        bot.register_next_step_handler(message, process_product_image, product_name, product_price, product_quantity, product_description)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

def process_product_image(message, product_name, product_price, product_quantity, product_description):
    if message.text == '🔙orqaga':
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())
        return

    if not message.photo:
        bot.send_message(message.chat.id, "Iltimos, rasm yuboring (rasm yuborish kerak).")
        bot.register_next_step_handler(message, process_product_image, product_name, product_price, product_quantity, product_description)
        return

    photo_file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, "Mahsulot kategoriyasini tanlang:", reply_markup=category_delete())
    bot.register_next_step_handler(message, process_product_category, product_name, product_price, product_quantity, product_description, photo_file_id)

def process_product_category(message, product_name, product_price, product_quantity, product_description, product_image):
    if message.text != '🔙orqaga':
        category_name = message.text
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        category = cursor.fetchone()
        if category:
            category_id = category[0]
            cursor.execute("INSERT INTO products (name, description, price, quantity, image, category_id) VALUES (?, ?, ?, ?, ?, ?)", (product_name, product_description, product_price, product_quantity, product_image, category_id))
            conn.commit()
            bot.send_message(message.chat.id, f"Mahsulot '{product_name}' muvaffaqiyatli qo'shildi!",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Kategoriyani topib bo'lmadi. Iltimos, kategoriyani to'g'ri tanlang.")
            bot.register_next_step_handler(message, process_product_category, product_name, product_price, product_quantity, product_description, product_image)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriya qo\'shish')
def add_category(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Kategoriya qo'shish bo'limiga xush kelibsiz! Iltimos, kategoriya nomini kiriting:",reply_markup=back_keyboard())
        bot.register_next_step_handler(message, process_category_name)

def process_category_name(message):
    if message.text != '🔙orqaga':
        category_name = message.text
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
        bot.send_message(message.chat.id, f"Kategoriya '{category_name}' muvaffaqiyatli qo'shildi!",reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriya o\'chirish')
def delete_category(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Kategoriya o'chirish bo'limiga xush kelibsiz! Iltimos, o'chirish uchun kategoriyani tanlang:", reply_markup=category_delete())
        bot.register_next_step_handler(message, process_category_deletion)

def process_category_deletion(message):
    if message.text != '🔙orqaga':
        category_name = message.text
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        category = cursor.fetchone()
        if category:
            category_id = category[0]
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"Kategoriya '{category_name}' muvaffaqiyatli o'chirildi!",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Kategoriyani topib bo'lmadi. Iltimos, kategoriyani to'g'ri tanlang.")
            bot.register_next_step_handler(message, process_category_deletion)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulot o\'chirish')
def delete_product(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Mahsulot o'chirish bo'limiga xush kelibsiz! Iltimos, o'chirish uchun mahsulotni tanlang:", reply_markup=product_delete())
        bot.register_next_step_handler(message, process_product_deletion)

def process_product_deletion(message):
    if message.text != '🔙orqaga':
        product_name = message.text
        cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
        product = cursor.fetchone()
        if product:
            product_id = product[0]
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"Mahsulot '{product_name}' muvaffaqiyatli o'chirildi!",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Mahsulotni topib bo'lmadi. Iltimos, mahsulotni to'g'ri tanlang.")
            bot.register_next_step_handler(message, process_product_deletion)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == 'malumot va aloqa ☎️')
def contact_info(message):
    bot.send_message(
        message.chat.id,
        '''📌 Malumot va aloqa:\n\nBoomstroy – O‘zbekistonda sifatli qurilish mollari savdosi bilan shug‘ullanuvchi do‘kon. Bizda Rossiya, Belarus, Xitoy va mahalliy ishlab chiqaruvchilarning ishonchli mahsulotlari mavjud.\n\n📍 Manzil: Bekobod tumani, Zafar shaharchasi \n📞 Telefon: +998 94 217 10 10 \n💬 Savollar uchun yozing yoki qo‘ng‘iroq qiling'''
    )

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulot o\'chirish')
def delete_product(message):
    if message.from_user.id in ADMINS_ID:
        bot.send_message(message.chat.id, "Mahsulot o'chirish bo'limiga xush kelibsiz! Iltimos, o'chirish uchun mahsulotni tanlang:", reply_markup=product_delete())
        bot.register_next_step_handler(message, process_product_deletion)

def process_product_deletion(message):
    if message.from_user.id not in ADMINS_ID:
        bot.send_message(message.chat.id, "Siz admin emassiz!")
        return
    if message.text != '🔙orqaga':
        product_name = message.text
        cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
        product = cursor.fetchone()
        if product:
            product_id = product[0]
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"Mahsulot '{product_name}' muvaffaqiyatli o'chirildi!",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Mahsulotni topib bo'lmadi. Iltimos, mahsulotni to'g'ri tanlang.")
            bot.register_next_step_handler(message, process_product_deletion)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())
if __name__ == "__main__":
    bot.infinity_polling()