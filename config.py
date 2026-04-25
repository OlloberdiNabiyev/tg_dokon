from db import conn
TOKEN = '8339250229:AAEzQmuyBfUxrYN5g2mufO7pVlVjtLkBKzI'
ADMINS_ID = [7746401400]
USER_ADMIN = 7176707054

def is_admin(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False

    cursor = conn.cursor()  # 🔥 YANGI cursor

    cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    return result is not None or user_id in ADMINS_ID