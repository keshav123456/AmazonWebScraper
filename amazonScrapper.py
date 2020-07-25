from selectorlib import Extractor
import requests
import re
from scraper_api import ScraperAPIClient
client = ScraperAPIClient('2d89a521927f970e0da6706727596da1')

from time import sleep
# Create an Extractor by reading from the YAML file
e1 = Extractor.from_yaml_file('searchConfig.yml')
e2 = Extractor.from_yaml_file('pageConfig.yml')

a = []
url_str = input("Enter the product category you want to search for: ")
url = []
limit = input("Enter the number of results you want to search for: ")
limit = int(limit)
# Hacky fix
words = url_str.split()
var = len(words)

if var == 1:
    url = "https://www.amazon.co.uk/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0]

if var == 2:
    url = "https://www.amazon.co.uk/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0] + "+" + words[1]

elif var == 3:
    url = "https://www.amazon.co.uk/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0] + "+" + words[
        1] + "+" + words[2]

# Add header
headers = {
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.amazon.co.uk/',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

oldr = requests.get(url, headers=headers)
# r = client.get(url=url)

x = e1.extract(oldr.text)

seperator = ","
# Csv writing setup
filename = url_str + ".csv"
f = open(filename, "w", encoding='utf-8')
csvheaders = "position, name, price, sponsored, number of reviews, rating, asin, rankings, producer, url \n"
f.write(csvheaders)

data = x
if data:
    counter = 0
    sponsorCounter = 0
    for product in data['products']:
        if counter + sponsorCounter < limit:
            product['search_url'] = url
            if product['sponsored'] != None:
                product['sponsored'] = "Yes"
                sponsorCounter = sponsorCounter + 1
                product['position'] = "sponsor : " + str(sponsorCounter)
            else:
                product['sponsored'] = "No"
                counter = counter + 1
                product['position'] = "normal : " + str(counter)
            if product['rating'] != None:
                product['rating'] = product['rating'].replace("out of 5 stars", "")
            for (field, value) in product.items():
                if product[field] == None:
                    product[field] = ""
                product[field] = product[field].replace(",", "")
            # second round of information extraction based on product page

            url2 = "https://www.amazon.co.uk" + product['url']
            product['url'] = url2
            oldr2 = requests.get(url2, headers=headers)
            # r2 = client.get(url=url2)
            y = e2.extract(oldr2.text)
            print(y)
            if y:
                for (field, value) in y.items():
                    if value is not None:
                        value = value.replace(",", "")
                        if field == 'producer':
                            value = value
                        if field == 'asin':
                            index = value.find("ASIN")
                            if index != -1:
                                start = index + 5
                                end = index + 16
                                value = value[start:end]
                            else:
                                value = ""
                        if field == "rankings":
                            value = re.sub("[{].*?[}]", "", value)
                            value = re.sub("[(].*?[)]", "", value)
                            value = re.sub("\.zg_hrsr_item", "", value)
                            value = re.sub("\.zg_hrsr_rank", "", value)
                            value = re.sub("\.zg_hrsr", "", value)
                            value = re.sub("Amazon Best Sellers Rank:", "", value)
                            value = ' '.join(value.split())
                        product[field] = value
                    else:
                        product[field] = ""

            f.write(product['position'] + seperator +
                    product['title'] + seperator +
                    product['price'] + seperator +
                    product['sponsored'] + seperator +
                    product['reviews'] + seperator +
                    product['rating'] + seperator +
                    product['asin'] + seperator +
                    product['rankings'] + seperator +
                    product['producer'] + seperator +
                    product['url'] + "\n")

f.close()
