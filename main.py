from utils import open_whatsapp_web, check_unread_messages, extract_messages_with_mention, generate_responses_to_extracted_messages, send_approval_requests

GROUP_NAME = "Test"
USER_NAME = "Pops"

if __name__ == "__main__":

    driver = open_whatsapp_web()

    extracted_messages = extract_messages_with_mention(driver, GROUP_NAME, USER_NAME)

    if extracted_messages:
        messages_and_responses = generate_responses_to_extracted_messages(extracted_messages)

        send_approval_requests(driver, USER_NAME, messages_and_responses)

    else:
        driver.quit()