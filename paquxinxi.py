import requests
import re

html = requests.get("http://book.douban.com/").text
pattern = re.compile('<h4.*?title">(.*?)</h4>.*?author">(.*?)</span>.*?year">(.*?)</span>',re.S)
results = re.findall(pattern, html)
for result in results:
    name,author,time = result
    author = re.sub("\s","",author)
    name = re.sub("\s","",name)
    time = re.sub("\s","",time)
    print(name,author,time)
