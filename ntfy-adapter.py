#!/usr/bin/env python3
import os
import sys
import logging
from aiohttp import web, ClientSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NTFY_BASE_URL = os.environ.get("NTFY_BASE_URL")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
NTFY_TOKEN = os.environ.get("NTFY_TOKEN")

LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", 8008))

routes = web.RouteTableDef()

@routes.post("/")
@routes.post("/message")
async def on_message(request):
    """
    Handle incoming POST requests and forward the message to ntfy.
    """
    try:
        content = await request.json()
        message = content.get("text", "")
        if not message:
            logger.error("No 'text' field in the request JSON.")
            return web.Response(status=400, text="Missing 'text' field in JSON.")
        
        # Extract the first line as the title
        title, _, body = message.partition('\n')
        formatted_message = message.replace("*", "- ")
        
        logger.info("Received message:\n%s", formatted_message)
        
        # Forward the alert to ntfy with title and message
        ntfy_resp = await send_ntfy_message(title.strip(), body.strip().replace("*", "- "))
        return web.Response(status=ntfy_resp.status)
    
    except Exception as e:
        logger.exception("Error processing message:")
        return web.Response(status=500, text=str(e))

async def send_ntfy_message(title: str, message: str):
    """
    Send a message to ntfy with the given title and message body.
    """
    headers = {
        "Authorization": f"Bearer {NTFY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Priority mapping based on keywords
    priority_keyword_mapping = {
        "error": 5,
    }
    priority = 3  # Default priority
    
    for keyword, value in priority_keyword_mapping.items():
        if keyword in message.lower():
            priority = value
            break
    
    data = {
        "topic": NTFY_TOPIC,
        "message": message,
        "title": title,
        "tags": ["warning" if priority == 5 else "information_source"],
        "priority": priority,
    }
    
    logger.debug("Sending data to ntfy: %s", data)
    
    async with ClientSession() as session:
        try:
            async with session.post(NTFY_BASE_URL, headers=headers, json=data) as resp:
                resp_text = await resp.text()
                logger.info("NTFY Response: %s, %s", resp.status, resp_text)
                return resp
        except Exception as e:
            logger.exception("Failed to send message to ntfy.")
            raise

def check_required_env_vars():
    """
    Ensure all required environment variables are set.
    """
    required_vars = ["NTFY_BASE_URL", "NTFY_TOPIC", "NTFY_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.critical("Missing required environment variables: %s", ', '.join(missing_vars))
        sys.exit(1)

def main():
    """
    Main entry point for the application.
    """
    check_required_env_vars()
    
    app = web.Application()
    app.add_routes(routes)
    
    logger.info("Starting server on %s:%d", LISTEN_HOST, LISTEN_PORT)
    web.run_app(app, host=LISTEN_HOST, port=LISTEN_PORT)

if __name__ == "__main__":
    main()