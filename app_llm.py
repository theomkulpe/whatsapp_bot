import os
import gradio as gr
from openai import OpenAI
from pinecone import ServerlessSpec, Pinecone
import time
from langchain_openai import OpenAIEmbeddings
import numpy as np
import requests
from openai import OpenAI
import pandas as pd

os.environ['PPLX_API_KEY'] = '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'
os.environ["PINECONE_API_KEY"] = '5c305aea-24de-4e50-9f6f-43837781ee7c'
os.environ["OPENAI_API_KEY"] = "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"
os.environ["EMBEDDING_MODEL"] = "text-embedding-ada-002"
os.environ["PPLX_MODEL"] = "pplx-70b-online"
os.environ["LLM"] = "gpt-4-1106-preview"
os.environ["pinecone_index_name"] = 'gemini-chirag-paragraphs-euclidean'
os.environ['feedback_path'] = 'feedback.csv'


import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope =  ['https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\Om\Downloads\WhatsApp Bot\Google Cloud Deployment\client_secret.json',scope)
client = gspread.authorize(creds)
sheet = client.open('feedback').sheet1


client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
messages = [] 
messages2 = []
history1 = '' #Contains only AI and user message and does not contain prompt instructions designed by developer
history2 = ''

pplx_url = "https://api.perplexity.ai/chat/completions"
def pplxity(prompt):
    payload = {
        "model": os.environ["PPLX_MODEL"] ,
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {os.environ['PPLX_API_KEY']}"
    }
    response =  requests.post(pplx_url, json=payload, headers=headers)
    try:
      return response.json()['choices'][0]['message']['content']
    except:
      print('pplxity error')
      print(prompt)
      return ''

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

spec = ServerlessSpec(
    cloud="aws", region="us-west-2"
)

index_name = os.environ["pinecone_index_name"]
index = pc.Index(index_name)
# index.describe_index_stats()
embed_model = OpenAIEmbeddings(model=os.environ['EMBEDDING_MODEL'])

def RAG(prompt):
  embed = embed_model.embed_documents([prompt])
  op = index.query(
    vector=embed,
    top_k=3,
    include_metadata=True)
  
  op = op['matches']
  context = ''
  for result in op:
    if result['score'] > 0.8:
      context = context + "\n" + result['metadata']['text']

  if len(context) == 0:
    print('PINCONE DATA NOT USED')
  
  response = client.chat.completions.create(
  model="gpt-4-1106-preview",
  messages=[{"role":"system","content":"""You need to write a simple and precise web search query to get the information needed to answer the chat. Only give query in the answer."""}, #todo add example
    {"role":"user","content":history1}],
  temperature=0.9,
  max_tokens=64,
  top_p=1
  )
  pplxityPrompt = response.choices[0].message.content

  print("Searching : ",pplxityPrompt)
  webInfo = pplxity(pplxityPrompt)
  
  augmented_prompt = f"""Using the web information and contexts below, answer the query.
  realtime information:
  {webInfo}
  Contexts:
  {context}

  Query: {prompt}"""
  print("augmented_prompt:",augmented_prompt)
  return augmented_prompt

def ask(prompt,baselineModel = False):

  prompt = {"role": "user",
      "content":prompt}
  
  if baselineModel:
    messages2.append(prompt)
    
    response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=messages2,
    temperature=0.7,
    max_tokens=64,
    top_p=1
    )
    res = response.choices[0].message.content

    messages2.append( {"role": "assistant",
      "content":res})
  else:
    messages.append(prompt)
    response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=messages,
    temperature=0.7,
    max_tokens=128,
    top_p=1
    )
    res = response.choices[0].message.content

    messages.append( {"role": "assistant",
      "content":res})
    
  return res

def newChat():
    global history1,history2
    history1 = ''
    history2 = ''

    with open(r'C:\Users\Om\Downloads\WhatsApp Bot\Google Cloud Deployment\prePrompt.txt') as file:
        prePrompt = file.read().replace("\n","")
        
    prePrompt = {"role":"system",
                 "content":prePrompt}
    del messages[:]
    messages.append(prePrompt)

    del messages2[:]

    return '' , '', ''

def chat_with_llm(prompt,instructions):
  global history1,history2
  history1 += f'You : {prompt}\n'
  augmented_prompt = RAG(prompt)
  res =  ask(instructions+augmented_prompt)
  history1 += f'Chhirag-GPT : {res}\n'

  history2 += f'You : {prompt}\n'
  res2 = ask(instructions+prompt,baselineModel=True)
  history2 += f'GPT-4 : {res2}\n'
  return '',history1,history2

def submitFeedback(feedback, output1,output2):
  try:
    sheet.append_row([output1,output2,feedback])
  except:
    pass
  return ''

newChat()

'''
with  gr.Blocks() as iface:
  input=gr.Textbox(lines=2, placeholder="Type your question here...",label = "Input")
  instructions = gr.Textbox(lines=2, placeholder="Add permanent instructions if any...",label = "Input")
  btn1 = gr.Button(value="Ask")
  output1 = gr.Textbox(label="Chhirag-GPT Output")
  output2 = gr.Textbox(label="GPT-4 Output")
  btn1.click(chat_with_llm,inputs = [input,instructions],outputs=[input,output1,output2])
    
  btn2 = gr.Button(value="New Chat")
  btn2.click(newChat,outputs =[output1,output2])

  feedback=gr.Textbox(lines=2, placeholder="Type your Feedback here...",label = "Input")
  btn3 = gr.Button(value="SubmitFeedback")
  btn3.click(submitFeedback,inputs=[feedback,output1,output2],outputs = [feedback])
'''

# iface.launch()
