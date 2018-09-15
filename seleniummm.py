from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

broswer = webdriver.Chrome()
try:
    broswer.get("http://www.baidu.com")
    input = broswer.find_element_by_id("kw")
    input.send_keys("Python")
    input.send_keys(Keys.ENTER)
    wait = WebDriverWait(broswer,10)
    wait.until(EC.presence_of_element_located((By.ID,"content_left")))
    print(broswer.current_url)
    print(broswer.get_cookies())
    print(broswer.page_source)
finally:
    broswer.close()