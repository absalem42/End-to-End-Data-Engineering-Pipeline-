import requests
from bs4 import BeautifulSoup as Bf


url = 'https://42abudhabi.ae/curriculum/'

page = requests.get(url)

# if(page.status_code == 200):
#     print(page.content)

ob = Bf(page.text, 'html.parser')

# print(ob)

output = ob.find('div', class_='num')

print(output)