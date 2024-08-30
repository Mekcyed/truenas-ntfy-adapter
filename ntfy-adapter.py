#!/usr/bin/env python3
import os
import sys
from aiohttp import web
from aiohttp import ClientSession

NTFY_BASE_URL = os.environ.get("NTFY_BASE_URL")
# Topic for TrueNas messages    
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
NTFY_TOKEN = os.environ.get("NTFY_TOKEN")

LISTEN_HOST = os.environ.get("LISTEN_HOST", "127.0.0.1")
LISTEN_PORT = os.environ.get("LISTEN_PORT", 8008)


routes = web.RouteTableDef()

# Listen to post requests on / and /message
@routes.post("/")
@routes.post("/message")
async def on_message(request):
    content = await request.json()
    # The content of the alert message
    message = content["text"]
    print("===== Alert =====")
    print(message)

    # Forward the alert to ntfy
    ntfy_resp = await send_ntfy_message(message)

    # Return the ntfy status code to truenas
    return web.Response(status=ntfy_resp.status)

# Send an arbitrary alert to ntfy
async def send_ntfy_message(message):
    # URL parameters
    headers = {"Authorization": f"Bearer {NTFY_TOKEN}"}
    ntfy_url = f"{NTFY_BASE_URL}/{NTFY_TOPIC}"

    # Send the message to ntfy
    async with ClientSession() as session:
        async with session.post(ntfy_url, headers=headers, json=str(message)) as resp:
            print(f"NTFY Response: {resp.status}, {await resp.text()}")
            return resp


if __name__ == "__main__":
    missing_vars = [var for var in ["NTFY_BASE_URL", "NTFY_TOPIC", "NTFY_TOKEN"] if not os.environ.get(var)]
    
    if missing_vars:
        sys.exit(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Listen on given port
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=LISTEN_HOST, port=LISTEN_PORT)