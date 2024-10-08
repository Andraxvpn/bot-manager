import os
from flask import Flask, render_template, request, redirect, jsonify
import subprocess

app = Flask(__name__)

# Folder untuk menyimpan file bot dan log
BOT_FILES_DIR = 'bot_files'
BOT_LOGS_DIR = 'bot_logs'

# Simpan daftar bot
bots = []

# Halaman Utama
@app.route('/')
def index():
    return render_template('index.html', bots=bots)

# API untuk mengupload bot
@app.route('/upload_bot', methods=['POST'])
def upload_bot():
    bot_name = request.form['bot_name']
    bot_file = request.files['bot_file']
    dependencies = request.form['dependencies']

    # Simpan file bot
    bot_file_path = os.path.join(BOT_FILES_DIR, bot_file.filename)
    bot_file.save(bot_file_path)

    # Tambahkan ke daftar bot
    bot_id = len(bots) + 1
    bots.append({
        'id': bot_id,
        'name': bot_name,
        'file_path': bot_file_path,
        'dependencies': dependencies,
        'status': 'Stopped'
    })

    return redirect('/')

# API untuk menjalankan bot
@app.route('/run_bot/<int:bot_id>', methods=['POST'])
def run_bot(bot_id):
    # Logika untuk menjalankan bot
    for bot in bots:
        if bot['id'] == bot_id:
            bot['status'] = 'Running'
            # Menjalankan bot menggunakan subprocess
            log_file_path = os.path.join(BOT_LOGS_DIR, f'bot_{bot_id}_log.txt')
            with open(log_file_path, 'w') as log_file:
                subprocess.Popen(['python', bot['file_path']], stdout=log_file, stderr=log_file)
            return jsonify({'message': f'Bot {bot_id} is running'})

# API untuk menghentikan bot
@app.route('/stop_bot/<int:bot_id>', methods=['POST'])
def stop_bot(bot_id):
    # Logika untuk menghentikan bot
    for bot in bots:
        if bot['id'] == bot_id:
            bot['status'] = 'Stopped'
            # Logika untuk menghentikan proses bot harus ditambahkan di sini
            return jsonify({'message': f'Bot {bot_id} is stopped'})

# API untuk melihat log bot
@app.route('/view_logs/<int:bot_id>', methods=['GET'])
def view_logs(bot_id):
    # Logika untuk mengambil log bot
    log_file_path =
  
