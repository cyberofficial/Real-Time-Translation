"""
Discord webhook integration module for message forwarding.

This module provides functionality to send messages to Discord channels through
webhooks. It handles message chunking for long texts and implements rate limit
handling to ensure reliable message delivery.
"""

import requests
import json

def send_to_discord_webhook(webhook_url, text):
    """
    Send a message to a Discord channel through a webhook.

    Handles long messages by automatically chunking them into smaller pieces
    to comply with Discord's message length limits. Also includes basic rate
    limit detection and error handling.

    Args:
        webhook_url (str): The Discord webhook URL to send messages to
        text (str): The message text to send

    Note:
        - Messages longer than 1800 characters are automatically split into chunks
        - Prints warning messages for rate limits and failed deliveries
        - Discord's rate limits are detected via 429 status code responses

    Example:
        send_to_discord_webhook("https://discord.com/api/webhooks/...", "Hello World!")
    """
    data = {
        "content": text
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        if len(text) > 1800:
            for i in range(0, len(text), 1800):
                data["content"] = text[i:i+1800]
                response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
                if response.status_code == 429:
                    print("Discord webhook is being rate limited.")
        else:
            response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
            if response.status_code == 429:
                print("Discord webhook is being rate limited.")
    except:
        print("Failed to send message to Discord webhook.")
        pass

print("Discord Module Loaded")