# IMPORTING LIBRARIES

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from app import ask
import regex as re
import time
import json


# FUNCTION TO OPEN WHATSAPP WEB

def open_whatsapp_web():
    options = Options()    
    user_data_dir = r'C:\Users\Om\Downloads\Chrome Session Data_'
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_experimental_option("detach", True)
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


# FUNCTION TO CLEAR SEARCH BOX

def clear_search_box(driver):

    try: 
        clear_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-icon = "x-alt"]'))
        )
        clear_button.click()
        time.sleep(1)

    except:
        pass


# FUNCTION TO GO TO WHATSAPP WEB HOME PAGE

def go_to_home_page(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    clear_search_box(driver)
    time.sleep(1)


# FUNCTION TO SEARCH FOR A PARTICULAR CHAT

def search_chat(driver, chat_name):
    actions = ActionChains(driver)
    click_search_button(driver)
    time.sleep(1)
    # actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('/').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
    time.sleep(1)
    actions.send_keys(chat_name).perform()
    time.sleep(3)


# FUNCTION TO CHECK UNREAD MESSAGES

def check_unread_messages(driver):
    try:
        # Wait and get the div with aria-label "Search results"
        search_results_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label = "Search results."]'))
        )

        time.sleep(1)

        # Within this div, check for any span tags with an aria-label containing "unread message"
        chat_unread_element = search_results_div.find_element(By.XPATH, './/span[contains(@aria-label, "unread message")]')
        unread_count = chat_unread_element.text
        unread_count = int(unread_count)

        return unread_count
    
    except:
        return 0


# FUNCTION TO OPEN CHAT

def open_chat(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(5)


# FUNCTION TO EXTRACT UNREAD MESSAGES WITH MENTION

def extract_messages_with_mention(driver, unread_count, user_name):

    actions = ActionChains(driver)

    new_messages = []

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id = "main"]'))
    )

    time.sleep(1)

    messages = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
    )

    while len(messages) < unread_count:
        actions.send_keys(Keys.PAGE_UP)

        time.sleep(1)
        
        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
        )
    
    for message in messages[int(unread_count) * -1:]:
        message_text = message.find_element(By.CSS_SELECTOR, 'span.selectable-text').text

        if f"@{user_name}" in message_text:
            metadata = message.find_element(By.XPATH, './/div[contains(@class, "copyable-text")]').get_attribute('data-pre-plain-text')
            new_messages.append((metadata, message_text),)

    return new_messages


# FUNCTION TO GENERATE RESPONSES TO EXTRACTED MESSAGES

def generate_responses_for_new_messages(new_messages):

    new_messages_and_responses = dict()

    for i in new_messages:
        message = i[1]
        response = ask(message)
        new_messages_and_responses[i] = response

    return new_messages_and_responses


# FUNCTION TO SEND APPROVAL REQUESTS TO THE USER

def send_approval_requests(driver, new_messages_and_responses):

    actions = ActionChains(driver)

    for message_data, response in new_messages_and_responses.items():
        approval_request = f'''*{message_data[0].strip()}*
{message_data[1]}

*Should I reply with:*
{response}'''

        # Split the message by newline and type each part, then press SHIFT+ENTER
        for part in approval_request.split('\n'):
            actions.send_keys(part).perform()
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        
        # Finally, send the message by pressing ENTER
        actions.send_keys(Keys.ENTER).perform()
        message_break = '------------------------------'
        actions.send_keys(message_break + Keys.ENTER).perform()

        time.sleep(1)


# CONSCIOUS CONVERSATIONS

def conscious_conversations(driver, unread_count):

    actions = ActionChains(driver)

    messages_and_approved_responses = dict()

    messages = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
    )

    while len(messages) < unread_count:
        actions.send_keys(Keys.PAGE_UP)

        time.sleep(1)
        
        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
        )

    # message_number = 0
    for message in messages[-1 * unread_count:]:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message)
        time.sleep(1)

        text_element = message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]')
        feedback = text_element.text  # Get the text of the element

        quoted_message_element = message.find_element(By.XPATH, './/span[contains(@class, "quoted-mention")]')
        quoted_message_text = quoted_message_element.text  # Get the text of the quoted message
        quoted_message_text_parts = quoted_message_text.split('\n')
        metadata = quoted_message_text_parts[0]
        older_prompt = quoted_message_text_parts[1]
        older_response = quoted_message_text_parts[4]

        prompt = f'''This task involves re-evaluating a previous response based on new feedback to determine the appropriate course of action.

You were previously given the following prompt:
{older_prompt}
Let's refer to this as ORIGINAL_PROMPT.

Based on ORIGINAL_PROMPT, you generated the following response:
{older_response}
We will call this ORIGINAL_RESPONSE.

Now, consider the following user feedback on ORIGINAL_RESPONSE:
{feedback}
We will refer to this as FEEDBACK.

Based on FEEDBACK, you must decide whether to affirm the ORIGINAL_RESPONSE or generate a revised response:
1. If FEEDBACK contains expressions of approval such as "Yes", "Alright", "Fine", "Sure", "Okay", "Okay, go ahead", "This is fine", "That's perfect", "Exactly right", "Just what I was looking for", "That works for me", "I agree", "That’s correct", "You've got it" or "That’s spot on", simply output "YES".
2. If FEEDBACK suggests changes, revisions, or dissatisfaction, craft a new response to ORIGINAL_PROMPT incorporating the user's suggestions and preferences noted in FEEDBACK.

Your output should either be "YES" (to confirm that no changes are needed) or a new, revised response to ORIGINAL_PROMPT based on FEEDBACK.'''
      
        new_response = ask(prompt)

        if new_response != "YES":

            approval_request = f'''*{metadata[0].strip()}*
{older_prompt}

*Should I reply with:*
{new_response}'''
            
            actions.move_to_element(message).perform()
            time.sleep(1)  # Small delay to ensure menu button appears
            
            # Click on the menu button to open the message options
            menu_button = message.find_element(By.CSS_SELECTOR, 'span[data-icon = "down-context"]') # (By.XPATH, './/span[@data-icon="down-context"]')
            menu_button.click()
            time.sleep(1)

            # Wait and click the 'Reply' button in the context menu
            actions.send_keys(Keys.DOWN).perform()
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(1)

            # Split the message by newline and type each part, then press SHIFT+ENTER
            for part in approval_request.split('\n'):
                actions.send_keys(part).perform()
                actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        
            # Finally, send the message by pressing ENTER
            actions.send_keys(Keys.ENTER).perform()
            message_break = '------------------------------'
            actions.send_keys(message_break + Keys.ENTER).perform()

            time.sleep(1)

        else:
            quoted_message_element = message.find_element(By.XPATH, './/span[contains(@class, "quoted-mention")]')
            quoted_message_text = quoted_message_element.text  # Get the text of the quoted message
            quoted_message_text_parts = quoted_message_text.split('\n')
            metadata = quoted_message_text_parts[0]
            message_text = quoted_message_text_parts[1]
            response = quoted_message_text_parts[4]
            messages_and_approved_responses[(metadata, message_text)] = response 

            time.sleep(1)

    return messages_and_approved_responses


# FUNCTION TO SEND APPROVED RESPONSES TO THE GROUP

def send_approved_responses(driver, messages_and_approved_responses):
     
    actions = ActionChains(driver)

    for ((approved_message_metadata, approved_message_text), approved_response) in messages_and_approved_responses.items():

        xpath = f"//div[contains(@class, 'message-in') and .//span[contains(., '{approved_message_text}')]]"

# and @data-pre-plain-text = '{approved_message_metadata}'

        max_attempts = 20

        attempts = 0
        while attempts < max_attempts:
            try:
                # Try to find the element using XPath
                message = driver.find_element(By.XPATH, xpath)
        
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message)
                time.sleep(1)

                actions.move_to_element(message).perform()
                time.sleep(1)  # Small delay to ensure menu button appears

                # Click on the menu button to open the message options
                menu_button = message.find_element(By.CSS_SELECTOR, 'span[data-icon = "down-context"]') # (By.XPATH, './/span[@data-icon="down-context"]')
                menu_button.click()
                time.sleep(1)

                # Wait and click the 'Reply' button in the context menu
                actions.send_keys(Keys.DOWN).perform()
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(1)

                actions.send_keys(approved_response + Keys.ENTER).perform()

                time.sleep(1)
                break

                # return element  # Return the element if found
            except NoSuchElementException:
                actions.send_keys(Keys.PAGE_UP).perform()
                time.sleep(1)  # Wait a bit for the page to load new content (adjust timing as necessary)
                attempts += 1


####################################################

def extract_messages_with_mention_new(driver, unread_count, user_name, file_name):

    actions = ActionChains(driver)

    new_messages = []

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id = "main"]'))
    )

    time.sleep(1)

    messages = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
    )

    while len(messages) < unread_count:
        actions.send_keys(Keys.PAGE_UP)

        time.sleep(1)
        
        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
        )
    
    for message in messages[int(unread_count) * -1:]:
        message_text = message.find_element(By.CSS_SELECTOR, 'span.selectable-text').text

        if f"@{user_name}" in message_text:
            metadata = message.find_element(By.XPATH, './/div[contains(@class, "copyable-text")]').get_attribute('data-pre-plain-text')
            metadata = metadata.strip()
            new_messages.append((metadata, message_text),)

    with open(file_name, 'r') as file:
        loaded_list = json.load(file)

    # Add new messages to the list
    updated_new_messages_list = loaded_list + new_messages

    # Save the updated list back to the file
    with open(file_name, 'w') as file:
        json.dump(updated_new_messages_list, file)

    return updated_new_messages_list


def send_approval_requests_new(driver, new_messages_list):

    actions = ActionChains(driver)

    message_data = new_messages_list[1]
    timestamp = message_data[0]
    message_text = message_data[1]

    response = ask(message_text)

    approval_request = f'''*{timestamp}*
{message_text}

*Should I reply with:*
{response}'''
    
    for part in approval_request.split('\n'):
        actions.send_keys(part).perform()
        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
    
    # Finally, send the message by pressing ENTER
    actions.send_keys(Keys.ENTER).perform()

    time.sleep(1)


def conscious_conversations_new(driver, unread_count, condition, new_messages_list, file_name):

    message_and_approved_response = dict()

    if condition:

        send_approval_requests_new(driver, new_messages_list)

        time.sleep(1)

    else:
    
        actions = ActionChains(driver)

        current_approval_message = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-out")))[-1]

        '''while not current_approval_message:
            actions.send_keys(Keys.PAGE_UP)

            time.sleep(1)
            
            current_approval_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.message-out"))
            )'''

        text_element = current_approval_message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]')
        current_approval_message_text = text_element.text

        current_approval_message_text_parts = current_approval_message_text.split('\n')
        metadata = current_approval_message_text_parts[0]
        older_prompt = current_approval_message_text_parts[1]
        older_response = current_approval_message_text_parts[4]

        message_and_approved_response = dict()

        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
        )

        while len(messages) < unread_count:
            actions.send_keys(Keys.PAGE_UP)

            time.sleep(1)
            
            messages = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.message-in"))
            )

        feedback = ""
        for message in messages[-1 * unread_count:]:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message)
            time.sleep(1)

            text_element = message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]')
            message_text = text_element.text  # Get the text of the element
            feedback += message_text
            feedback += ' '

            '''quoted_message_element = message.find_element(By.XPATH, './/span[contains(@class, "quoted-mention")]')
            quoted_message_text = quoted_message_element.text  # Get the text of the quoted message
            quoted_message_text_parts = quoted_message_text.split('\n')
            metadata = quoted_message_text_parts[0]
            older_prompt = quoted_message_text_parts[1]
            older_response = quoted_message_text_parts[4]'''

        prompt = f'''This task involves evaluating a previous response based on new feedback to determine the appropriate course of action.

You were previously given the following prompt:
{older_prompt}
Let's refer to this as ORIGINAL_PROMPT.

Based on ORIGINAL_PROMPT, you generated the following response:
{older_response}
We will call this ORIGINAL_RESPONSE.

Now, consider the following user feedback on ORIGINAL_RESPONSE:
{feedback}
We will refer to this as FEEDBACK.

Based on FEEDBACK, you must decide whether to affirm the ORIGINAL_RESPONSE or generate a revised response:
1. If FEEDBACK contains expressions of approval such as "Yes", "Alright", "Fine", "Sure", "Okay", "Okay, go ahead", "This is fine", "That's perfect", "Exactly right", "Just what I was looking for", "That works for me", "I agree", "That’s correct", "You've got it" or "That’s spot on", simply output "YES".
2. If FEEDBACK suggests changes, revisions, or dissatisfaction, craft a new response to ORIGINAL_PROMPT incorporating the user's suggestions and preferences noted in FEEDBACK.

Your output should either be "YES" (to confirm that no changes are needed) or a new, revised response to ORIGINAL_PROMPT based on FEEDBACK.'''
        
        new_response = ask(prompt)

        if new_response != "YES":

            approval_request = f'''*{metadata}*
{older_prompt}

*Should I reply with:*
{new_response}'''

            # Split the message by newline and type each part, then press SHIFT+ENTER
            for part in approval_request.split('\n'):
                actions.send_keys(part).perform()
                actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        
            # Finally, send the message by pressing ENTER
            actions.send_keys(Keys.ENTER).perform()

            time.sleep(1)

        else:
            message_and_approved_response[(metadata, older_prompt)] = older_response

            new_messages_list.pop(1)

            with open(file_name, 'w') as file:
                json.dump(new_messages_list, file)

            if len(new_messages_list) > 1:
                send_approval_requests_new(driver, new_messages_list)

            time.sleep(1)

    return message_and_approved_response