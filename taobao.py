import re
from taobaomongo import *
import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

broswer = webdriver.Chrome()
wait = WebDriverWait(broswer,10)

def search():
    try:
        broswer.get("http://www.taobao.com")
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#q"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button"))
        )
        input.send_keys('轻薄本')
        submit.click()
        submit_tiaomao = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,"#tabFilterMall"))
        )
        submit_tiaomao.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total"))
        )
        get_products()
        return total.text
    except TimeoutException:
        return search()

def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(page_number))
        )
        get_products()
    except TimeoutException:
        return next_page(page_number)

def get_products():
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-itemlist .items .item"))
    )
    html = broswer.page_source
    doc = pq(html)
    items = doc("#mainsrp-itemlist .items .item").items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text().replace('\n',''),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text().replace('\n',''),
            'shop': item.find('.shop').text(),
            'location': item.find('location').text()
        }
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_DB].insert(result):
            print('保存到MongoDB成功',result)
    except Exception:
            print('保存失败',result)

def main():
    try:
        total = search()
        total = int(re.compile("(\d+)").search(total).group(1))
        for i in range(2, total+1):
            next_page(i)
    except Exception:
        print("出现错误")
    finally:
        broswer.close()

if __name__ =='__main__':
    main()
