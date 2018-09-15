from pyquery import PyQuery as pq

doc = pq(url="http://www.baidu.com")
a = doc("p")
print(a.siblings())
print(a.text())
a.find("a").remove()
print(a.text())