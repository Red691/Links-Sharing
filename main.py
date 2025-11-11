from bot import Bot
Bot().run()

from flask import Flask
import threading, time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running on Choreo!"

def run_web():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_web).start()

print("Bot is running on Choreo...")

while True:
    time.sleep(3600)
