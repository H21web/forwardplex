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

# Dynamic support for single or multiple channel IDs
from_channel_ids_env = os.getenv("FROM_CHANNEL_IDS")
if not from_channel_ids_env:
    raise ValueError("FROM_CHANNEL_IDS environment variable is not set.")

# Split and parse, support both single and multiple channels
channel_id_strs = [cid.strip() for cid in from_channel_ids_env.split(",") if cid.strip()]
if not channel_id_strs:
    raise ValueError("No valid channel IDs found in FROM_CHANNEL_IDS.")

# If only one channel, use int; if multiple, use list of ints
if len(channel_id_strs) == 1:
    source_channel_ids = int(channel_id_strs[0])
else:
    source_channel_ids = [int(cid) for cid in channel_id_strs]

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
