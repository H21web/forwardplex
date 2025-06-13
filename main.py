import os
import threading
from dotenv import load_dotenv
from telethon import TelegramClient, events
from http.server import HTTPServer, BaseHTTPRequestHandler

# Load environment variables
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME", "anon")

# Parse source channels as a comma-separated list of integers
source_channel_ids = [
    int(cid.strip()) for cid in os.getenv("FROM_CHANNEL_IDS").split(",")
]
target_channel_id = int(os.getenv("TO_CHANNEL_ID"))

# Health check HTTP server for Koyeb
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    server = HTTPServer(('', 8080), HealthHandler)
    server.serve_forever()

# Start health server in a separate thread
threading.Thread(target=run_health_server, daemon=True).start()

# Telegram client setup
client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=source_channel_ids))
async def handler(event):
    await client.forward_messages(target_channel_id, event.message)

client.start()
client.run_until_disconnected()
