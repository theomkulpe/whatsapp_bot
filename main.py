# main.py

from utils import open_whatsapp, extract_messages_generate_responses_and_ask_approval, check_approval_and_send_responses
import time

GROUP_NAME = "Testing WhatsApp Bot"
USER_NAME = "Chirag Kedia"

def main():
    # Open WhatsApp Web and get the driver instance
    driver = open_whatsapp()
'''    
    # Wait for WhatsApp Web to load completely
    time.sleep(10)  # You might need to adjust the sleep time based on your internet speed

    try:
        # Extract messages, generate responses, and ask for approval
        messages_and_responses = extract_messages_generate_responses_and_ask_approval(driver, GROUP_NAME, USER_NAME)

        

        # Wait some time to give the user a chance to respond to the approval requests
        time.sleep(60)  # Adjust this based on how much time you want to give

        # Check for approvals and send responses to the group
        check_approval_and_send_responses(driver, GROUP_NAME, USER_NAME, messages_and_responses)
        
    except Exception as e:
        print(f"An error occurred during the execution: {e}")
    finally:
        # Close the driver
        driver.quit()
'''
if __name__ == '__main__':
    main()
