# IMPORTING LIBRARIES

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from app import ask
import regex as re


# FUNCTION TO OPEN WHATSAPP WEB

def open_whatsapp_web():
    options = Options()
    
    user_data_dir = r'C:\Users\Om\Downloads\Chrome Session Data_'

    options.add_argument(f'--user-data-dir={user_data_dir}')

    service = Service(executable_path='./chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://web.whatsapp.com")

    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id = "side"]')))

    except:
        print("Unable to open WhatsApp Web.")

    time.sleep(5)

    return driver


# FUNCTION TO CLICK SEARCH BUTTON IN WHATSAPP WEB

def click_search_button(driver):

    try: 
        search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-icon = "search"]'))
        )
        search_button.click()

    except:
        print("Unable to click Search Button.")


# FUNCTION TO GO TO WHATSAPP WEB HOME PAGE

def go_to_home_page(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    click_search_button(driver)


# FUNCTION TO CHECK UNREAD MESSAGES

def check_unread_messages(driver, chat_name):
    actions = ActionChains(driver)

    click_search_button(driver)

    time.sleep(0.5)

    actions.send_keys(chat_name).perform()

    time.sleep(1)

    try:
        # Wait and get the div with aria-label "Search results"
        search_results_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label = "Search results."]'))
        )

        # Within this div, check for any span tags with an aria-label containing "unread message"
        chat_unread_element = search_results_div.find_element(By.XPATH, './/span[contains(@aria-label, "unread message")]')
        unread_count = chat_unread_element.text
        unread_count = int(unread_count)

        return unread_count
    
    except:
        return 0
    

# FUNCTION TO EXTRACT UNREAD MESSAGES WITH MENTION

def extract_messages_with_mention(driver, chat_name, user_name):

    actions = ActionChains(driver)

    unread_count = check_unread_messages(driver, chat_name)

    # unread_count = 4

    unread_messages = []

    if unread_count:
        actions.send_keys(Keys.ENTER).perform()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id = "main"]'))
        )

        time.sleep(5)

        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "message-in")]'))
        )
        
        for message in messages[int(unread_count) * -1:]:
            message_text = message.find_element(By.CSS_SELECTOR, 'span.selectable-text').text

            if f"@{user_name}" in message_text:
                metadata = message.find_element(By.XPATH, './/div[contains(@class, "copyable-text")]').get_attribute('data-pre-plain-text')
                unread_messages.append((metadata, message_text),)

        go_to_home_page(driver)

    return unread_messages


# FUNCTION TO GENERATE RESPONSES TO EXTRACTED MESSAGES

def generate_responses_to_extracted_messages(extracted_messages):

    messages_and_responses = dict()

    # response_number = 1

    for i in extracted_messages:
        message = i[1]

        response = ask(message)
        messages_and_responses[i] = response

        # response_number += 1

    return messages_and_responses


# FUNCTION TO SEND APPROVAL REQUESTS TO THE USER
def send_approval_requests(driver, chat_name, messages_and_responses):
    actions = ActionChains(driver)

    click_search_button(driver)

    time.sleep(0.5)

    actions.send_keys(chat_name).perform()

    time.sleep(1)

    actions.send_keys(Keys.ENTER).perform()

    for message_data, response in messages_and_responses.items():

        approval_request = f'''{message_data[0]}
{message_data[1]}

Should I reply with:
{response}'''

        # Split the message by newline and type each part, then press SHIFT+ENTER
        for part in approval_request.split('\n'):
            actions.send_keys(part).perform()
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        
        # Finally, send the message by pressing ENTER
        actions.send_keys(Keys.ENTER).perform()

    go_to_home_page(driver)