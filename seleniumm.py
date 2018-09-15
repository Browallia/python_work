from selenium import webdriver
from selenium.webdriver.common.by import By
import time

broswer = webdriver.Chrome()
broswer.get("http://www.taobao.com")
input = broswer.find_element(By.ID,"q")
input.send_keys("面膜")
time.sleep(1)
input.clear()
input.send_keys("aj1")
button = broswer.find_element(By.CLASS_NAME,"btn-search")
button.click()