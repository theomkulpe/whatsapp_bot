from utils import open_whatsapp_web, click_search_button, clear_search_box, go_to_home_page, search_chat, check_unread_messages, open_chat, extract_messages_with_mention_new, generate_responses_for_new_messages, send_approval_requests, conscious_conversations_new, send_approved_responses
import json

GROUP_NAME = "Testing WhatsApp Bot"
USER_NAME = "Chhirag Kedia"
FILE_NAME = 'test_list.json'
CONDITION = False

if __name__ == "__main__":
    driver = open_whatsapp_web()
    search_chat(driver, GROUP_NAME)
    group_unread_count = check_unread_messages(driver)

    if group_unread_count:
        open_chat(driver)
        new_messages_list = extract_messages_with_mention_new(driver, group_unread_count, USER_NAME, FILE_NAME)
        go_to_home_page(driver)

    else:
        click_search_button(driver)
        with open(FILE_NAME, 'r') as file:
            new_messages_list = json.load(file)

    search_chat(driver, USER_NAME)
    user_unread_count = check_unread_messages(driver)
    # user_unread_count = 3

    if user_unread_count or (CONDITION and (len(new_messages_list) > 1)):
        open_chat(driver)
        message_and_approved_response = conscious_conversations_new(driver, user_unread_count, CONDITION, new_messages_list, FILE_NAME)
        go_to_home_page(driver)

    else:
        message_and_approved_response = {}
        clear_search_box(driver)

    if message_and_approved_response:
        search_chat(driver, GROUP_NAME)
        open_chat(driver)
        send_approved_responses(driver, message_and_approved_response)
        go_to_home_page(driver)

    driver.quit() 

    print("Success!")