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
import pickle


# OPENING A CHROME WINDOW

options = Options()

user_data_dir = r'C:\Users\Om\Downloads\Chrome Session Data_'

options.add_argument(f'--user-data-dir={user_data_dir}')

service = Service(executable_path='./chromedriver.exe')

driver = webdriver.Chrome(service=service, options=options)

actions = ActionChains(driver)


# SETTING CONSTANTS

GROUP_NAME = "Testing WhatsApp Bot"
USER_NAME = "Chirag Kedia"


# OPENING WHATSAPP WEB

driver.get("https://web.whatsapp.com")

time.sleep(20)


# CHECKING IF THERE ARE ANY UNREAD MESSAGES

actions.send_keys(Keys.ESCAPE).perform()    

search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
search_icon.click()

actions.send_keys("User 1").perform()

time.sleep(1)

chat = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f"//span[@title='User 1']"))
)

try:        
    # Navigate to the parent element to find the unread message count
    chat_element = chat.find_element(By.XPATH, "./ancestor::div[contains(@class, '_ak8l')]")
    
    # Within this chat element, attempt to find the unread message indicator
    unread_indicator = chat_element.find_element(By.XPATH, ".//span[contains(@aria-label, 'unread message')]")
    unread_count = unread_indicator.text
    unread_count = int(unread_count)
    
    has_unread, unread_count = True, unread_count

except Exception as e:
    print(f"No unread messages found for '{USER_NAME}'.")
    has_unread, unread_count = False, None


# CHECKING USER'S APPROVAL

if has_unread:

    messages_and_approved_responses = {}

    actions.send_keys(Keys.ENTER).perform()

    # Select the last 'n' messages
    messages = driver.find_elements(By.CSS_SELECTOR, "div.message-in")[-1 * unread_count:]
    
    # Loop through the selected messages
    for message in messages:
        # Check if the message text contains "yes"
        if 'yes' in message.text.lower():
            try:
                # Locate the quoted message and extract its text
                quoted_message = message.find_element(By.CSS_SELECTOR, ".quoted-mention")
                quoted_message_text = quoted_message.text
                quoted_message_text_parts = quoted_message_text.split('\n')
                metadata = quoted_message_text_parts[0]
                message_text = quoted_message_text_parts[1]
                response = quoted_message_text_parts[4]
                messages_and_approved_responses[(metadata, message_text)] = response

            except Exception as e:
                print("Quoted message not found in this message.")
        else:
            print("Message does not contain 'yes'.")

                
    actions.send_keys(Keys.ESCAPE).perform()    

    search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
    search_icon.click()


# SENDING RESPONSE TO THE GROUP

if messages_and_approved_responses: 

    search_icon.click()   
    actions.send_keys(GROUP_NAME).perform()

    time.sleep(1)

    actions.send_keys(Keys.ENTER).perform()
    messages = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "message-in")]'))
    )

    for (metadata, message_text), response in messages_and_approved_responses.items():
        for message in messages:
            if (metadata == message.find_element(By.XPATH, './/div[contains(@class, "copyable-text")]').get_attribute('data-pre-plain-text')) and (message_text == message.find_element(By.CSS_SELECTOR, 'span.selectable-text').text):
                    message_text_element = message.find_element(By.CSS_SELECTOR, 'span.selectable-text')

                    actions.move_to_element(message_text_element).perform()
                    time.sleep(1)  # Small delay to ensure menu button appears

                    # Click on the menu button to open the message options
                    menu_button = message.find_element(By.XPATH, './/span[@data-icon="down-context"]')
                    menu_button.click()

                    # Wait and click the 'Reply' button in the context menu
                    reply_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Reply"]'))
                    )
                    reply_button.click()

                    # Wait for the reply input box to be active and enter the reply text
                    reply_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    reply_input.send_keys(response + Keys.ENTER)

                    break

