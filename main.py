from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
from threading import Thread
import socket

app = Flask(__name__)

@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message.html')
def message():
    return render_template('message.html')

@app.route('/message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        try:
            username = request.form.get('username', 'Аноним')
            message = request.form.get('message', '')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            with open('storage/data.json', 'r+') as file:
                data = json.load(file)
                data[timestamp] = {
                    "username": username,
                    "message": message
                }
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()

            return redirect(url_for('index'))
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")
            return render_template('error.html'), 500

    return render_template('error.html'), 405

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', error_message='Method not allowed.'), 405

def socket_server():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            message_data = json.loads(data.decode('utf-8'))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            with open('storage/data.json', 'r+') as file:
                data = json.load(file)
                data[timestamp] = {
                    "username": message_data.get('username', 'Аноним'),
                    "message": message_data.get('message', '')
                }
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка обработки сообщения: {e}")

if __name__ == '__main__':
    socket_thread = Thread(target=socket_server)
    socket_thread.start()

    app.run(port=3000)