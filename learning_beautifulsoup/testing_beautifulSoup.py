import requests
from bs4 import BeautifulSoup as Bf


url = 'https://www.scrapethissite.com/pages/forms/'

page = requests.get(url)

# if(page.status_code == 200):
#     print(page.content)

ob = Bf(page.text, 'html')

print(ob)