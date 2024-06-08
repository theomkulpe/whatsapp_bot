from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def open_whatsapp_web():
  options = Options()
  options.binary_location = '/home/writetodeepaksharma/chrome-linux64/chrome'
  service = Service('/home/writetodeepaksharma/chrome-linux64/chromedriver'
  driver = webdriver.Chrome(services = service, options = options)
  driver.get("https://web.whatsapp.com")
  return driver
