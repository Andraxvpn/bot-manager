import telebot
import requests
import base64
import re
import logging
import time
from datetime import datetime, timedelta
import schedule
import threading

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Token bot Telegram dan GitHub
TELEGRAM_TOKEN = '7341627486:AAFd7TdIjxVdSx3lfkrhgAZpB2VMMU0WjuI'
GITHUB_TOKEN = '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'
GITHUB_URL = 'https://api.github.com/repos/Andraxvpn/Andrax-script/contents/izin'
VPN_FREE_URL = 'https://api.github.com/repos/Andraxvpn/Andrax-script/contents/VPN_FREE.txt'
PROMOSI_URL = 'https://api.github.com/repos/Andraxvpn/Andrax-script/contents/promosi.txt'

# Inisialisasi bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def is_valid_ip(ip):
    """Validasi format alamat IP."""
    pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return pattern.match(ip)

def fetch_current_content():
    """Ambil konten file dari GitHub."""
    try:
        response = requests.get(GITHUB_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        response.raise_for_status()  # Raise an error for bad responses
        file_info = response.json()

        if 'content' in file_info:
            decoded_content = base64.b64decode(file_info['content']).decode('utf-8')
            logging.info("Konten berhasil diambil dari GitHub.")
            return decoded_content, file_info['sha']
        else:
            logging.error("Konten tidak ditemukan dalam respons GitHub.")
            return None, None
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Gagal mengambil konten: {str(e)}")
        return None, None

def fetch_vpn_free_content():
    """Ambil konten file VPN FREE dari GitHub."""
    try:
        response = requests.get(VPN_FREE_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        response.raise_for_status()  # Raise an error for bad responses
        file_info = response.json()

        if 'content' in file_info:
            decoded_content = base64.b64decode(file_info['content']).decode('utf-8')
            logging.info("Konten VPN FREE berhasil diambil dari GitHub.")
            return decoded_content
        else:
            logging.error("Konten tidak ditemukan dalam respons GitHub.")
            return None
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        logging.error(f"Gagal mengambil konten: {str(e)}")
        return None

def fetch_promosi_content():
    """Ambil konten file promosi.txt dari GitHub."""
    try:
        response = requests.get(PROMOSI_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        response.raise_for_status()  # Raise an error for bad responses
        file_info = response.json()

        if 'content' in file_info:
            decoded_content = base64.b64decode(file_info['content']).decode('utf-8')
            logging.info("Konten promosi.txt berhasil diambil dari GitHub.")
            return decoded_content
        else:
            logging.error("Konten tidak ditemukan dalam respons GitHub.")
            return None
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        logging.error(f"Gagal mengambil konten: {str(e)}")
        return None

def update_github_content(new_content, sha):
    """Perbarui konten file di GitHub."""
    try:
        updated_content_base64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        update_response = requests.put(
            GITHUB_URL,
            json={
                'message': 'Memperbarui daftar IP',
                'content': updated_content_base64,
                'sha': sha
            },
            headers={'Authorization': f'token {GITHUB_TOKEN}'}
        )
        update_response.raise_for_status()  # Raise an error for bad responses
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return False
    except Exception as e:
        logging.error(f"Gagal memperbarui konten: {str(e)}")
        return False

def send_reminders():
    """Kirim pengingat untuk IP yang mendekati kedaluwarsa."""
    current_content, _ = fetch_current_content()
    if current_content:
        for line in current_content.splitlines():
            parts = line.split(' ### ')
            if len(parts) == 2:
                user_info, ip_info = parts
                name, expiration, ip_address = ip_info.split(' ')
                expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
                if expiration_date - datetime.now() < timedelta(days=7):
                    # Kirim notifikasi kepada pengguna
                    bot.send_message(user_info, f"⏰ **Pengingat:** IP {ip_address} akan kedaluwarsa pada {expiration}.")

def schedule_reminders():
    """Jadwalkan pengingat harian."""
    schedule.every().day.at("10:00").do(send_reminders)  # Ganti waktu sesuai kebutuhan

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("📋 DAFTAR IP", callback_data="IPVPS"))
    keyboard.add(telebot.types.InlineKeyboardButton("💻 SCRIPT VPS", callback_data="script_vps"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔐 VPN", callback_data="vpn"))

    bot.send_message(message.chat.id,
                     "👋 **Selamat datang di Bot Manajemen IP!**\n"
                     "Silakan pilih opsi di bawah:",
                     reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "IPVPS")
def send_welcome(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("➕ Tambah IP", callback_data="add_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📋 Lihat Daftar IP", callback_data="view_ip_list"))
    keyboard.add(telebot.types.InlineKeyboardButton("🗑️ Hapus IP", callback_data="delete_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📤 Ekspor IP", callback_data="export_ip"))
    keyboard.add(telebot.types.InlineKeyboardButton("📥 Impor IP", callback_data="import_ip"))
    keyboard.add(telebot.types.InlineKeyboardButton("ℹ️ Bantuan", callback_data="help"))

    bot.reply_to(call.message,
                 "📋 **Menu IP Manager!**\n"
                 "Kelola alamat IP Anda dengan mudah dan cepat.\n\n"
                 "Silakan pilih opsi di bawah:",
                 reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "script_vps")
def script_vps(call):
    bot.send_message(call.message.chat.id, 
                     "💻 **Menu SCRIPT VPS.**\n"
                     "Silakan kunjungi repositori kami di [GitHub](https://github.com/Andraxvpn/Andrax-script).",
                     parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "vpn")
def vpn(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("⭐ VPN PREMIUM", callback_data="vpn_premium"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔓 VPN FREE", callback_data="vpn_free"))
    bot.send_message(call.message.chat.id, "🔐 **Menu VPN.**", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "vpn_premium")
def vpn_premium(call):
    promosi_content = fetch_promosi_content()
    if promosi_content:
        bot.send_message(call.message.chat.id, f"⭐ **VPN PREMIUM**\n\n{promosi_content}", parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "❌ **Gagal mengambil konten promosi.**", parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "vpn_free")
def vpn_free(call):
    """Mengirimkan konten VPN FREE kepada pengguna."""
    vpn_free_content = fetch_vpn_free_content()
    if vpn_free_content:
        bot.send_message(call.message.chat.id, f"🔓 **VPN FREE**\n\n{vpn_free_content}", parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "❌ **Gagal mengambil konten VPN FREE.**", parse_mode='Markdown')

if __name__ == '__main__':
    reminder_thread = threading.Thread(target=schedule_reminders, daemon=True)
    reminder_thread.start()
    bot.polling()
