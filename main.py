from utils import open_whatsapp_web, click_search_button, go_to_home_page, search_chat, check_unread_messages, open_chat, extract_messages_with_mention, generate_responses_for_new_messages, send_approval_requests, conscious_conversations, send_approved_responses

GROUP_NAME = "Test"
USER_NAME = "Pops"

if __name__ == "__main__":
    driver = open_whatsapp_web()
    search_chat(driver, GROUP_NAME)
    group_unread_count = check_unread_messages(driver)

    if group_unread_count:
        open_chat(driver)
        new_messages = extract_messages_with_mention(driver, group_unread_count, USER_NAME)
        go_to_home_page(driver)

        # print("new_messages:\n")
        for item in new_messages:
            print(item)

        if new_messages:
            new_messages_and_responses = generate_responses_for_new_messages(new_messages)

            # print("\nnew_messages_and_responses:\n")
            # for key, value in new_messages_and_responses.items():
                # print(f'{key}: {value}'.encode('cp1252', errors='ignore').decode('cp1252'))


    else:
        new_messages = []
        click_search_button(driver)

    search_chat(driver, USER_NAME)
    user_unread_count = check_unread_messages(driver)

    if new_messages or user_unread_count:
        open_chat(driver)

        if user_unread_count:
            messages_and_approved_responses = conscious_conversations(driver, user_unread_count)

            # print("\nmessages_and_approved_responses:\n")
            # for key, value in messages_and_approved_responses.items():
                # print(f'{key}: {value}'.encode('cp1252', errors='ignore').decode('cp1252'))

        else:
            messages_and_approved_responses = {}


        if new_messages:
            send_approval_requests(driver, new_messages_and_responses)

        go_to_home_page(driver)

    else:
        messages_and_approved_responses = {}
        click_search_button(driver)

    if messages_and_approved_responses:
        search_chat(driver, GROUP_NAME)
        open_chat(driver)
        send_approved_responses(driver, messages_and_approved_responses)
        go_to_home_page(driver)

    driver.quit()

    print("Success!")