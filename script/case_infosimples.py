# Imports
from bs4 import BeautifulSoup
import requests
import re
import json

def get_page_html():
    # Request
    url = 'https://storage.googleapis.com/infosimples-public/commercia/case/product.html'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    page = requests.get(url, headers=header).text
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def get_title(soup):
    title = soup.find('h2', id='product_title').get_text(strip=True)  
    return title


def get_brand(soup):
    brand = soup.find('div', class_='brand').get_text(strip=True) 
    return brand


def get_categories(soup):
    categories_list = soup.find('nav', class_='current-category').find_all('a')
    categories = [subcategories.get_text(strip=True) for subcategories in categories_list] 
    
    return categories


def get_description(soup):   
    description = soup.find('p', style=re.compile('text-align')).get_text(strip=True)
    description = re.sub('\n', repl='', string=description)  
    description = re.sub('\s+', repl=' ', string=description) 
    
    return description


def get_sku(soup):


    def get_name(soup): 
        name_list = soup.find_all('div', class_='sku-name')
        name = [name.get_text(strip=True) for name in name_list]   

        return name


    def get_current_price(soup):
        current_price = [] 
        current_price_search_tag = soup.find_all('div', class_='card-container')

        for current_price_tag in current_price_search_tag:
            if current_price_tag.find('div', class_='sku-current-price'):
                current_price.append(float(current_price_tag.find('div', class_='sku-current-price').get_text(strip=True).replace('$ ', '')))
            else:
                current_price.append(None)

        return current_price


    def get_old_price(soup):
        old_price = [] 
        old_price_search_tag =  soup.find_all('div', class_='card-container')

        for old_price_tag in old_price_search_tag:
            if old_price_tag.find('div', class_='sku-old-price'):
                old_price.append(float(old_price_tag.find('div', class_='sku-old-price').get_text(strip=True).replace('$ ', '')))
            else:
                old_price.append(None)
        return old_price


    def get_available(soup):
        available = []  
        available_search_tag = soup.find_all('meta', itemprop='availability')

        for index, text in enumerate(available_search_tag):    
            if re.search('NewCondition', str(text)):
                available_search_tag.pop(index)

        for available_tag in available_search_tag:
            available_tag.get('content')
            available_content = re.search('\/([A-Z])', available_tag.get('content')).group(1)

            if available_content == 'I':
                available.append(True)
            else:
                available.append(False)



        return available

    name = get_name(soup)
    current_price = get_current_price(soup)
    old_price = get_old_price(soup)
    available = get_available(soup)

    sku = {'name': name , 'current_price': current_price, 'old_price': old_price, 'available': available}

    return sku


def get_properties(soup):


    def get_product_properties(soup):
        product_properties_list = list(filter(None, soup.find('table', class_='pure-table pure-table-bordered').get_text().split('\n')))
        product_properties_label, product_properties_text, product_properties = ([], [], {})

        for index in range(len(product_properties_list)):
            if index % 2 == 0:
                product_properties_label.append(product_properties_list[index])


        for index in range(len((product_properties_list))):
            if index % 2 != 0:
                product_properties_text.append(product_properties_list[index])
                product_properties_text

        product_properties = dict(zip(product_properties_label, product_properties_text))        
        
        return product_properties


    def get_additional_properties(soup):        
        additional_properties_list = list(filter(None, soup.find_all('table', class_='pure-table pure-table-bordered')[1].get_text().split('\n')))
        additional_properties_label, additional_properties_text, additional_properties = ([], [], {})

        for index in range(len(additional_properties_list)):
            if index % 2 == 0:
                additional_properties_label.append(additional_properties_list[index])

        for index in range(len(additional_properties_list)):
            if index % 2 != 0:
                additional_properties_text.append(additional_properties_list[index])
                additional_properties_text

        additional_properties = dict(zip(additional_properties_label, additional_properties_text))


        additional_properties.pop('Property')
        additional_properties['Storage temperature'] = additional_properties['Storage temperature'].replace('Âº', '')

        return additional_properties

    product_properties = get_product_properties(soup)
    additional_properties = get_additional_properties(soup)

    properties = []
    properties.append(product_properties)
    properties.append(additional_properties)

    return properties


def get_reviews(soup):

    def get_name(soup):
        reviews_name_tag = soup.find_all('span', class_='review-username')
        name  = [name.get_text(strip=True).encode("iso-8859-1").decode('utf-8')  for name in reviews_name_tag]
        
        return name


    def get_date(soup):
        reviews_date_tag = soup.find_all('span', class_='review-date')
        date = [date.get_text(strip=True) for date in reviews_date_tag]
        
        return date


    def get_score(soup):
        # avaliacao (ler descrição do problema para entender a lógica)
        reviews_stars_tag = soup.find_all('span', class_='review-stars')
        review_stars_symbol = [stars.get_text().encode('iso-8859-1').decode("utf-8") for stars in reviews_stars_tag]
        positive_star = 'â\x98\x85'.encode('iso-8859-1').decode("utf-8")
        score = [star_symbol.count(positive_star) for star_symbol in review_stars_symbol]
        
        return score

    def get_text(soup):
        review_text_tag = soup.find_all('div', class_='review-box')
        text = [review.find('p').get_text(strip=True).encode("iso-8859-1").decode('utf-8') for review in review_text_tag]

        return text

    name = get_name(soup)
    date = get_date(soup)
    score= get_score(soup)
    text = get_text(soup)
    reviews = {'name': name, 'date': date, 'score': score, 'text': text}

    return reviews


def get_reviews_average_score(soup):
    average_score = soup.find('div', id='comments').find('h4').get_text(strip=True)
    reviews_average_score = float(re.search('(\d.+)\/', average_score).group(1))

    return reviews_average_score

def get_url(soup):
    link_tag = soup.find_all('link', itemprop='url')
    url = [link.get('href') for link in link_tag] 

    return url

def resposta_final(title, brand, categories, description, sku, properties, reviews, reviews_average_score, url):
    resposta_final = {
        'title': title,
        'brand': brand,
        'categories': categories,
        'description': description,
        'sku': sku,
        'properties': properties,
        'reviews': reviews,
        'reviews_average_score': reviews_average_score,
        'url': url
    }

    with open('json/produto.json', 'w') as arquivo_json:
        arquivo_json.write(json.dumps(resposta_final))

    return None