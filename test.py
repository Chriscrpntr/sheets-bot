from urllib.request import urlopen
import xmltodict
import pprint
from thefuzz import fuzz
from thefuzz import process

file = urlopen('https://sheets.wiki/sitemap.xml')
data = file.read()
file.close()

data = xmltodict.parse(data)['urlset']['url']
for i in range(len(data)):
    data[i] = data[i]['loc'].replace('https://sheets.wiki/', '')

def search(query):
    query = query.lower()
    result = process.extractOne(query, data)
    return 'https://sheets.wiki/' + result[0]

if __name__ == '__main__':
    print(search('page-vlookup'))
