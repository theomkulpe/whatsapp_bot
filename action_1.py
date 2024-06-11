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


# SETTING CONSTANTS

GROUP_NAME = "Testing WhatsApp Bot"
USER_NAME = "Chirag Kedia"


# OPENING CHROME

options = Options()
user_data_dir = r'C:\Users\Om\Downloads\Chrome Session Data_'
options.add_argument(f'--user-data-dir={user_data_dir}')
options.add_experimental_option("detach", True)
service = Service(executable_path='./chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)
actions = ActionChains(driver)


# OPENING WHATSAPP WEB

driver.get("https://web.whatsapp.com")

time.sleep(20)

# CHECKING IF THERE ARE ANY UNREAD MESSAGES

actions.send_keys(Keys.ESCAPE).perform()    

search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
search_icon.click()

actions.send_keys(GROUP_NAME).perform()

time.sleep(1)

chat = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f"//span[@title='{GROUP_NAME}']"))
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
    print(f"No unread messages found for '{GROUP_NAME}'.")
    has_unread, unread_count = False, None


# EXTRACTING UNREAD MESSAGES WITH MENTION (IF ANY)

if has_unread:

    try:
        # Open the chat by clicking on the search result
        '''chat = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//span[@title='{group_name}']"))
        )
        chat.click()'''

        actions.send_keys(Keys.ENTER).perform()

        # Wait a bit for the chat to open and messages to load
        time.sleep(2)

        # Find all message bubbles in the chat
        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "message-in")]'))
        )
        
        # Extract text from each unread message
        unread_messages = []
        for message in messages[int(unread_count) * -1:]:
            try:
                    message_text = message.find_element(By.CSS_SELECTOR, 'span.selectable-text').text

                    if f"@{USER_NAME}" in message_text:
                        metadata = message.find_element(By.XPATH, './/div[contains(@class, "copyable-text")]').get_attribute('data-pre-plain-text')
                        unread_messages.append((metadata, message_text),)

            except Exception as e:
                print(f"Error reading message: {e}")
                continue

        actions.send_keys(Keys.ESCAPE).perform()    

        search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
        search_icon.click()
    
    except Exception as e:
        print(f"An error occurred while extracting unread messages: {e}")

        actions.send_keys(Keys.ESCAPE).perform()    

        search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
        search_icon.click()


# GENERATING RESPONSES TO EXTRACTED MESSAGES

if unread_messages:
    messages_and_responses = dict()

    response_number = 1

    for i in unread_messages:
        message = i[1]

        response = "Test response " + str(response_number)
        messages_and_responses[i] = response

        response_number += 1

    with open('messages_and_responses.pkl', 'wb') as file:
        pickle.dump(messages_and_responses, file)


# SENDING RESPONSE APPROVAL REQUESTS TO THE USER

if messages_and_responses:
    with open('messages_and_responses.pkl', 'rb') as file:
        messages_and_responses = pickle.load(file)

    actions.send_keys(Keys.ESCAPE).perform()    

    search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
    search_icon.click()

    actions.send_keys("User 1").perform()   ##################################

    time.sleep(1)

    actions.send_keys(Keys.ENTER).perform()

    # search_box = search_for_chat(user_name)

    try:

        '''chat = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, '_ao3e') and contains(@class, 'x1iyjqo2')]/span[@class='matched-text _ao3e' and text()='User 1']"))
        )   

        chat.click()

                            


        message_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )

        # Create an ActionChains object to send keys
        
        actions.move_to_element(message_box)'''

        for message_data, response in messages_and_responses.items():

        

            approval_request = f'''{message_data[0]}
{message_data[1]}

Should I reply with:
{response}'''

            

            # Split the message by newline and type each part, then press SHIFT+ENTER
            for part in approval_request.split('\n'):
                actions.send_keys(part)
                actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
        
            # Finally, send the message by pressing ENTER
            actions.send_keys(Keys.ENTER)
            actions.perform()

    except Exception as e:
        print(f"An error occurred while sending approval: {e}")

    actions.send_keys(Keys.ESCAPE).perform()

    search_icon = driver.find_element(By.XPATH, '//span[@data-icon="search"]')
    search_icon.click()
