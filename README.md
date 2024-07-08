This program extracts new messages (where the user has been mentioned) from the group, generates responses to each of these messages using the LLM and then sends these message-response pairs to the user (via WhatsApp DM) for approval. The user can give his feedback to make the responses better in the chat and finally approve the responses. Once a response is approved, the program replies to the corresponding message on the group with this response.

You will need the following files to run this program: **client_secret.json**, **prePrompt.txt**, **app.py**, **chromedriver.exe**, **utils.py** and **main.py**.
The first three files can be downloaded from the HuggingFace space (https://huggingface.co/spaces/GotMeAI/Chhirag-GPT). The latter three files are present in this repository. Note that you may need to download the appropriate ChromeDriver (chromedriver.exe) from https://developer.chrome.com/docs/chromedriver/downloads.

Save all the six files on your machine and ensure that all the paths are rightly declared in the files.

All the required functions have been declared in 'utils.py'. The LLM is accessed using 'ask()' function. This function is declared in 'app.py' and is called in 'utils.py' as follows:  
*from app import ask  
response = ask("This is the prompt.")  
print(response)*  

Install the necessary packages using 'requirements.txt'.

You can run 'main.py' to run the WhatsApp Bot. Note that you must set **CONDITION = True** (in 'main.py') when you are running the program for the first time. You can set **CONDITION = False** for the following runs.
