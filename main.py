
from telebot import TeleBot
from config import TOKEN, is_admin,USER_ADMIN
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from buttons import *
from db import cursor,conn
from regions import districts,regions
bot = TeleBot(TOKEN)
bot.user_data = {}

# func
def get_districts_by_region(region_name):
    region_id = None

    for r in regions:
        if r["name"] == region_name:
            region_id = r["id"]
            break

    if not region_id:
        return []

    return [d["name"] for d in districts if d["region_id"] == region_id]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_admin(user_id):
        bot.send_message(message.chat.id, f'assalomu alaykum {message.from_user.first_name} \nadmin panelga xush kelibsiz!', reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, f'assalomu alaykum {message.from_user.first_name} 👋 Xush kelibsiz!', reply_markup=user_keyboard())

@bot.message_handler(func=lambda message:message.text == 'malumot va aloqa ☎️')
def contact_info(message):
    bot.send_message(
        message.chat.id,
        '''📌 Malumot va aloqa:\n\nBoomstroy – O‘zbekistonda sifatli qurilish mollari savdosi bilan shug‘ullanuvchi do‘kon. Bizda Rossiya, Belarus, Xitoy va mahalliy ishlab chiqaruvchilarning ishonchli mahsulotlari mavjud.\n\n📍 Manzil: Bekobod tumani, Zafar shaharchasi \n📞 Telefon: +998 94 217 10 10 \n💬 Savollar uchun qo\'ng\'iroq qiling'''
    )

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriyalar')
def go_categories(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Kategoriyalar bo'limiga xush kelibsiz!", reply_markup=category_keyboard())

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulotlar')
def go_products(message):
    if is_admin(message.from_user.id):
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
    if is_admin(message.from_user.id):
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
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!🔙", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!🔙", reply_markup=user_keyboard())

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulot qo\'shish')
def add_product(message):
    if is_admin(message.from_user.id):
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
            bot.send_message(message.chat.id, f"Mahsulot '{product_name}' muvaffaqiyatli qo'shildi ✅",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Kategoriyani topib bo'lmadi. Iltimos, kategoriyani to'g'ri tanlang.")
            bot.register_next_step_handler(message, process_product_category, product_name, product_price, product_quantity, product_description, product_image)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriya qo\'shish')
def add_category(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "⭕️Kategoriya qo'shish bo'limiga xush kelibsiz! Iltimos, kategoriya nomini kiriting:",reply_markup=back_keyboard())
        bot.register_next_step_handler(message, process_category_name)

def process_category_name(message):
    if message.text != '🔙orqaga':
        category_name = message.text
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
        bot.send_message(message.chat.id, f"Kategoriya '{category_name}' muvaffaqiyatli qo'shildi✅",reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📁 Kategoriya o\'chirish')
def delete_category(message):
    if is_admin(message.from_user.id):
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
    if is_admin(message.from_user.id):
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
            bot.send_message(message.chat.id, f"Mahsulot '{product_name}' muvaffaqiyatli o'chirildi✅",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Mahsulotni topib bo'lmadi. Iltimos, mahsulotni to'g'ri tanlang ❌")
            bot.register_next_step_handler(message, process_product_deletion)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '📦 Mahsulot o\'chirish')
def delete_product(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Mahsulot o'chirish bo'limiga xush kelibsiz! Iltimos, o'chirish uchun mahsulotni tanlang:", reply_markup=product_delete())
        bot.register_next_step_handler(message, process_product_deletion)

def process_product_deletion(message):
    if not is_admin(message.from_user.id):
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
            bot.send_message(message.chat.id, f"Mahsulot '{product_name}' muvaffaqiyatli o'chirildi✅",reply_markup=admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Mahsulotni topib bo'lmadi. Iltimos, mahsulotni to'g'ri tanlang ❌")
            bot.register_next_step_handler(message, process_product_deletion)
    else:
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '👤 Adminlar')
def show_admins(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Adminlar ro'yxati:", reply_markup=Admins())

@bot.message_handler(func=lambda message: message.text == '👤 Adminlar ro\'yxati')
def show_admins_list(message):
    if not is_admin(message.from_user.id):
        return

    cursor.execute("SELECT user_id FROM admins")
    admins = cursor.fetchall()

    if not admins:
        bot.send_message(message.chat.id, "👤 Adminlar ro'yxati bo'sh.")
        return

    response = f"👤 Adminlar soni: {len(admins)} ta\n\n"
    response += "📋 Ro'yxat:\n\n"

    for i, admin in enumerate(admins, start=1):
        user_id = admin[0]

        try:
            chat = bot.get_chat(user_id)

            if chat.username:
                name = f"@{chat.username}"
            else:
                name = chat.first_name

        except:
            name = f"ID: {user_id}"

        response += f"{i}. {name}\n"

    bot.send_message(message.chat.id, response,reply_markup=admin_keyboard())
    
@bot.message_handler(func=lambda message:message.text == '👤 Admin qo\'shish')
def add_admin(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "👤Admin qo'shish bo'limiga xush kelibsiz! Iltimos, qo'shmoqchi bo'lgan adminning Telegram ID sini kiriting:", reply_markup=back_keyboard())
        bot.register_next_step_handler(message, process_add_admin)

def process_add_admin(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Siz admin emassiz!")
        return
    if message.text == '🔙orqaga':
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=admin_keyboard())
        return
    try:
        new_admin_id = int(message.text)
        try:
            chat = bot.get_chat(new_admin_id)

            if chat.username:
                name = f"@{chat.username}"
            else:
                name = chat.first_name

        except:
            bot.send_message(
                message.chat.id,
                "❌ Bu foydalanuvchi hali botga /start bosmagan!\n\nIltimos, undan botni ochib /start bosishini so‘rang."
            )
            return
        cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (new_admin_id,))
        conn.commit()

        bot.send_message(
            message.chat.id,
            f"✅ Admin {name} muvaffaqiyatli qo‘shildi!",
            reply_markup=admin_keyboard()
        )

    except ValueError:
        bot.send_message(message.chat.id, "❌ Iltimos, to‘g‘ri ID kiriting.",reply_markup=admin_keyboard())

@bot.message_handler(func=lambda message:message.text == '👤 Admin o\'chirish')
def delete_admin(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Admin o'chirish bo'limiga xush kelibsiz! Iltimos, o'chirish uchun adminni tanlang:", reply_markup=delete_admins())
        bot.register_next_step_handler(message, process_delete_admin)

def process_delete_admin(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Siz admin emassiz!")
        return

    if message.text == '🔙orqaga':
        return

    try:
        user_id = int(message.text.split('|')[-1].strip())

        cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()

        bot.send_message(
            message.chat.id,
            f"✅ Admin (ID: {user_id}) o‘chirildi!",
            reply_markup=admin_keyboard()
        )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Xatolik! Iltimos, tugmadan tanlang.")
        bot.register_next_step_handler(message, process_delete_admin)

@bot.message_handler(func=lambda message:message.text == 'Mahsulotlar 📦')
def view_categories(message):
    bot.send_message(message.chat.id, "📦 Mahsulotlar bo'limiga xush kelibsiz! \n\n kategoriyalarni tanlang:", reply_markup=category_keyboardss())
    bot.register_next_step_handler(message, view_products_by_category)

def view_products_by_category(message):
    category_name = message.text
    if category_name == '🔙 Orqaga':
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=user_keyboard())
        return
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category = cursor.fetchone()

    if category:
        category_id = category[0]
        cursor.execute("SELECT name FROM products WHERE category_id = ?", (category_id,))
        products = cursor.fetchall()
        if products:
            response = f"📂 {category_name} kategoriyasidagi mahsulotlar: "
            bot.send_message(message.chat.id, response, reply_markup=product_list())
            bot.register_next_step_handler(message, view_product_details, category_id)
        else:
            bot.send_message(message.chat.id, "❌ Bu kategoriyada mahsulotlar mavjud emas.", reply_markup=category_keyboardss())

def view_product_details(message, category_id):
    product_name = message.text

    cursor.execute("""
        SELECT id, name, price, quantity, description, image
        FROM products
        WHERE name = ? AND category_id = ?
    """, (product_name, category_id))

    product = cursor.fetchone()

    if product:
        caption = (
            f"🛒 {product[1]}\n"
            f"💰 Narxi: {product[2]} so'm\n"
            f"📦 Mavjud: {product[3]}\n"
            f"📝 {product[4]}"
        )

        bot.send_photo(
            message.chat.id,
            product[5],
            caption=caption,
            reply_markup=product_inline_keyboard(product[0], 1, product[2])
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    user_id = call.from_user.id

    cursor = conn.cursor()

    if data.startswith("plus_") or data.startswith("minus_"):
        action, product_id, count = data.split("_")
        product_id = int(product_id)
        count = int(count)

        cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        price = cursor.fetchone()[0]

        if action == "plus":
            count += 1
        elif action == "minus" and count > 1:
            count -= 1

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=product_inline_keyboard(product_id, count, price)
        )

    elif data.startswith("add_"):
        _, product_id, count = data.split("_")
        product_id = int(product_id)
        count = int(count)

        cursor.execute("""
            SELECT quantity FROM cart
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))

        item = cursor.fetchone()

        if item:
            new_count = item[0] + count
            cursor.execute("""
                UPDATE cart SET quantity = ?
                WHERE user_id = ? AND product_id = ?
            """, (new_count, user_id, product_id))
        else:
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (user_id, product_id, count))

        conn.commit()
        bot.answer_callback_query(call.id, "✅ Savatchaga qo‘shildi!", show_alert=True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(call.message.chat.id, "Mahsulot savatga qo‘shildi! 🛒\nAsosiy menyu:", reply_markup=user_keyboard())

    elif data == "clear_cart":
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()

        bot.edit_message_text(
            "🗑 Savatcha tozalandi",
            call.message.chat.id,
            call.message.message_id
        )

    elif data == "checkout":
        cursor.execute("""
            SELECT 1 FROM cart WHERE user_id = ?
        """, (user_id,))

        if not cursor.fetchone():
            bot.answer_callback_query(call.id, "❌ Savatcha bo‘sh")
            return

        bot.answer_callback_query(call.id)

        msg = bot.send_message(
            call.message.chat.id,
            "👤 Ismingizni kiriting:",
            reply_markup=back_keyboard()
        )

        bot.register_next_step_handler(msg, get_name)

    elif data == "confirm_order":
        data_user = bot.user_data.get(user_id)

        if not data_user:
            bot.answer_callback_query(call.id, "❌ Ma'lumot topilmadi")
            return

        name = data_user["name"]
        phone = data_user["phone"]
        address = data_user["address"]
        items = data_user["items"]
        total = data_user["total"]

        text = "🆕 YANGI BUYURTMA\n\n"
        text += f"👤 {name}\n📞 {phone}\n📍 {address}\n\n"

        for product_id, pname, price, qty in items:
            text += f"{pname} x{qty} = {price * qty} so'm\n"

            cursor.execute("""
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
            """, (qty, product_id))

        text += f"\n💰 Jami: {total} so'm"

        conn.commit()

        bot.send_message(USER_ADMIN, text)

        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()

        bot.send_message(
            call.message.chat.id,
            "✅ Buyurtma qabul qilindi!\n📞 Adminlar tez orada bog‘lanadi",
            reply_markup=user_keyboard()
        )

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
    elif data == "cancel_order":
        bot.send_message(call.message.chat.id, "❌ Buyurtma bekor qilindi",reply_markup=user_keyboard())

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

    elif data == "back_to_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "🏠 Bosh menyu")

@bot.message_handler(func=lambda message: message.text == "savatcha🛒")
def open_cart(message):
    view_cart(message)

def view_cart(message):
    user_id = message.from_user.id

    cursor.execute("""
        SELECT p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))

    items = cursor.fetchall()

    if not items:
        bot.send_message(message.chat.id, "🛒 Savatcha bo‘sh")
        return

    text = "🛒 Savatchangiz:\n\n"
    total = 0

    for name, price, qty in items:
        item_total = price * qty
        total += item_total

        text += f"📦 {name}\n"
        text += f"   {price} × {qty} = {item_total} so'm\n\n"

    text += f"💰 Jami: {total} so'm"

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=cart_inline_keyboard()
    )

def get_name(message):
    if message.text == '🔙orqaga':
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=user_keyboard())
        return

    name = message.text


    msg = bot.send_message(
        message.chat.id,
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard()
    )
    bot.register_next_step_handler(msg, get_phone, name)

def get_phone(message, name):
    if message.text == '⬅️ Orqaga':
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=user_keyboard())
        return
    
    if not message.contact:
        msg = bot.send_message(message.chat.id, "❌ Iltimos, tugma orqali raqamni yuboring!", reply_markup=phone_keyboard())
        bot.register_next_step_handler(msg, get_phone, name)
        return

    phone = message.contact.phone_number

    msg = bot.send_message(
        message.chat.id,
        "📍 Viloyatingizni tanlang:",
        reply_markup=region_keyboard()
    )

    bot.register_next_step_handler(msg, get_region, name, phone)

def get_region(message, name, phone):
    if message.text == "🔙 Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz!", reply_markup=user_keyboard())
        return

    region = message.text

    district_list = get_districts_by_region(region)

    if not district_list:
        msg = bot.send_message(message.chat.id, "❌ Tugmadan tanlang")
        return bot.register_next_step_handler(msg, get_region, name, phone)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    for d in district_list:
        markup.add(d)

    markup.add("⬅️ Viloyatga qaytish")

    msg = bot.send_message(
        message.chat.id,
        "🏙 Tumanni tanlang:",
        reply_markup=markup
    )

    bot.register_next_step_handler(msg, get_district, name, phone, region)

def get_district(message, name, phone, region):
    if message.text == "⬅️ Viloyatga qaytish":
        msg = bot.send_message(
            message.chat.id,
            "📍 Viloyatni tanlang:",
            reply_markup=region_keyboard()
        )
        bot.register_next_step_handler(msg, get_region, name, phone)
        return

    district = message.text
    user_id = message.from_user.id

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))

    items = cursor.fetchall()

    if not items:
        bot.send_message(message.chat.id, "❌ Savatcha bo‘sh")
        return

    total = sum(price * qty for _, _, price, qty in items)

    address = f"{region}, {district}"

    text = "🧾 BUYURTMANI TASDIQLANG:\n\n"
    text += f"👤 {name}\n📞 {phone}\n📍 {address}\n\n"

    for _, pname, price, qty in items:
        text += f"{pname} x{qty} = {price * qty} so'm\n"

    text += f"\n💰 Jami: {total} so'm"

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_order"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")
    )

    bot.user_data = getattr(bot, "user_data", {})
    bot.user_data[user_id] = {
        "name": name,
        "phone": phone,
        "address": address,
        "items": items,
        "total": total
    }

    bot.send_message(message.chat.id, text, reply_markup=markup)

if __name__ == "__main__":
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print("ERROR:", e)