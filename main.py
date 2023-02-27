from selenium import webdriver
import telebot
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import subprocess
import datetime
import threading


EXTENSION_PATH = 'C:/Users/aksma/AppData/Local/Google/Chrome/User Data/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/10.24.1_0.crx'
EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
chat_id = 0

def copy2clip(txt):
    cmd = 'echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)


def launchBrowser():
    opt = Options()
    opt.add_experimental_option("detach", True)
    opt.add_extension(EXTENSION_PATH)
    driver = webdriver.Chrome(options=opt)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(12)
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/ul/li[2]/button').click()
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div/button[1]').click()
    time.sleep(1)
    elem = driver.find_element(by=By.XPATH,
                               value='/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/div/div[3]/div[1]/div[1]/div/input')
    copy2clip('YOUR_SEED_PHRASE')
    elem.click()
    elem.send_keys(Keys.CONTROL + 'v')
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/button').click()
    time.sleep(1)
    elem = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[1]/label/input')
    elem.send_keys('YOUR_PASSWORD')
    elem = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[2]/label/input')
    elem.click()
    elem.send_keys('YOUR_PASSWORD')
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[3]/label/input').click()
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/button').click()
    time.sleep(5)
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/button').click()
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/button').click()
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div/div/div[2]/button').click()
    driver.get('https://blur.io/collection/minters-world')
    #time.sleep(1)
    driver.switch_to.window(driver.window_handles[1])
    driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
    #time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])
    #time.sleep(1)
    driver.find_element(by=By.XPATH, value='/html/body/div/div/main/div/button').click()
    driver.find_element(by=By.XPATH, value='/html/body/div/div[3]/div[3]/div[2]/div[2]/button[1]').click()
    driver.switch_to.window(driver.window_handles[1])
    #time.sleep(1)
    driver.refresh()
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div[3]/div[2]/button[2]').click()
    #time.sleep(1)
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    time.sleep(2)
    driver.refresh()
    time.sleep(2)
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div/div[3]/button[2]').click()
    time.sleep(3)
    return driver


def createResponseString(text):
    s = ''
    try:
        data = json.loads(text)
        first_3_prices = [level["price"] for level in data["priceLevels"][:3]]
        first_3_executable_sizes = [level["executableSize"] for level in data["priceLevels"][:3]]

        for i in range(0, len(first_3_prices)):
            s += str((i+1)) + " bid: " + first_3_prices[i] + "; depth: " + str(first_3_executable_sizes[i]) + ' bids \n'
    except Exception as e:
        s = "Collection not found"
    return s


def get_max_bid_and_depth(text):
    try:
        data = json.loads(text)
        first_bid = [level["price"] for level in data["priceLevels"][:1]]
        first_bid_depth = [level["executableSize"] for level in data["priceLevels"][:1]]
    except Exception as e:
        s = "Oops..."
        return s
    return first_bid, str(first_bid_depth)


def split_message(message, max_length=4096):
    parts = []
    while message:
        if len(message) <= max_length:
            parts.append(message)
            break
        else:
            part = message[:max_length]
            i = part.rfind(" ")
            if i == -1:
                i = len(part)
            parts.append(part[:i])
            message = message[i:]
    return parts


bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_API')
driver = launchBrowser()
collections = {}
with open("collections.json", "r") as file:
    collections = json.load(file)




#JSON and Update Part
def load_collections(): #loading the collections from JSON file
    global collections
    try:
        with open("collections.json", "r") as file:
            collections = json.load(file)
    except FileNotFoundError:
        collections = {}


def save_collections():
    with open("collections.json", "w") as file:
        json.dump(collections, file)


def update_collections(slug, max_bid, depth):
    collections[slug] = [max_bid, depth]
    save_collections()


def check_max_bids():
    while True:
        try:
            bot.send_message(chat_id, "Starting scaning")
            for slug in collections:
                url = "https://core-api.prod.blur.io/v1/collections/" + slug + "/executable-bids?filters=%7B%7D"
                driver.get(url)
                response = driver.find_element(by=By.XPATH, value='/html/body/pre').get_attribute('innerHTML')
                maxBid, depth = get_max_bid_and_depth(response)
                if maxBid != collections[slug][0]:
                    if maxBid < collections[slug][0]:
                        direction = 'fell down'
                    else:
                        direction = 'rose'
                    update_collections(slug, maxBid, depth)
                    bot.send_message(chat_id, f"Max bid for collection <code>{slug}</code> has {direction} to {maxBid}.", parse_mode='HTML')
                    bot.send_message(chat_id,
                                     '{\n "slug": "' + slug + '",\n"minProfitPercent": 0,\n"maxSpendEth":' + str(
                                         float(maxBid[0]) - 0.015) + ',' +
                                     '"maxBuy": 1,\n"minutes": 15,\n"Non-terminating Mode": 12,\n"Cancel Offers": "-", "minBlurBid": ' + str(float(maxBid[0])) + '}')

            bot.send_message(chat_id, "Scaning over")
            time.sleep(500)
        except Exception as e:
            print(e)


#Telegram Part
@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(message.chat.id, "Starting now")
    load_collections()


@bot.message_handler(commands=['my_collections'])
def show_collections(message):
    load_collections()
    global chat_id
    chat_id = message.chat.id
    if collections:
        response = f"Tracked collections: {len(collections)}\n"
        for slug in sorted(collections):
            response += f"- Collection: <code>{slug}</code>, bid: {collections[slug][0]}, depth: {collections[slug][1]} \n"
        parts = split_message(response)
        for part in parts:
            bot.send_message(chat_id=message.chat.id, text=part, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "No collections are being tracked")


@bot.message_handler(commands=['clear_all'])
def clear_all(message):
    global collections
    collections = {}
    save_collections()
    bot.send_message(message.chat.id, "All collections removed.")


@bot.message_handler(commands=['add'])
def add_collection(message):
    load_collections()
    global chat_id
    chat_id = message.chat.id
    text = message.text.split()
    if len(text) == 2:
        try:
            slug = text[1]
            url = "https://core-api.prod.blur.io/v1/collections/" + slug + "/executable-bids?filters=%7B%7D"
            driver.get(url)
            response = driver.find_element(by=By.XPATH, value='/html/body/pre').get_attribute('innerHTML')
            maxBid, depth = get_max_bid_and_depth(response)
            update_collections(slug, maxBid, depth)
            save_collections()
            bot.send_message(message.chat.id,
            "Collection added: " + slug + " with max bid " + str(maxBid) + " and depth " + str(
            depth))
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occured: {e}. Probably the collection slug not found")
    else:
        bot.send_message(message.chat.id, "Incorrect format. Use /add {slug}")


@bot.message_handler(commands=['remove'])
def remove_collection(message):
    load_collections()
    global chat_id
    chat_id = message.chat.id
    text = message.text.split()
    if len(text) == 2:
        try:
            slug = text[1]
            if slug in collections:
                collections.pop(slug)
                save_collections()
                bot.send_message(message.chat.id, f"Collection '{slug}' removed.")
            else:
                bot.send_message(message.chat.id, f"Collection '{slug}' not found.")
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occured: {e}")
    else:
        bot.send_message(message.chat.id, "Incorrect format. Use /remove {slug}")


notification_thread = threading.Thread(target=check_max_bids)
notification_thread.start()

bot.polling()
