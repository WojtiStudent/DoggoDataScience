from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm
import re


if __name__ == '__main__':
    main_url = 'https://dogtime.com/dog-breeds/profiles'
    page = requests.get(main_url)
    vital_stats_names = ["Dog Breed Group", "Height", "Weight", "Life Span"]

    doggos_dict = {}
    doc = BeautifulSoup(page.content, 'html.parser')

    dogs_names_and_hrefs = doc.find_all('a', class_='list-item-title')
    for item in tqdm(dogs_names_and_hrefs, desc="Scraping dogs"):
        doggo_data = {'name': item.text, 'href': item.get('href')}

        sub_page_url = item.get('href')
        sub_page = requests.get(sub_page_url)
        sub_doc = BeautifulSoup(sub_page.content, 'html.parser')

        characteristics_divs = sub_doc.find_all('div', class_='breed-characteristics-ratings-wrapper')
        for div in characteristics_divs:
            general_feature_title_tag = div.find('h3')
            stars_tag = div.find('div', class_=re.compile("star star-."))
            stars_amount = stars_tag.get('class')[1][-1]
            doggo_data[general_feature_title_tag.text.upper().strip()] = stars_amount

            feature_divs = div.find_all('a', class_='js-list-item-trigger characteristic-stars')
            for feature_div in feature_divs:
                feature_title_tag = feature_div.find(class_="characteristic-title")
                stars_tag = feature_div.find(class_=re.compile("star star-."))
                stars_amount = stars_tag.get('class')[1][-1]
                doggo_data[feature_title_tag.text] = stars_amount

        vital_stats_divs = sub_doc.find_all('div', class_='vital-stat-box')
        for div in vital_stats_divs:
            try:
                vital_stat_name, vital_stat_value = div.text.split(':')
                doggo_data[vital_stat_name] = vital_stat_value
            except:
                pass

        doggos_dict[doggo_data['name']] = doggo_data

    df = pd.DataFrame.from_dict(doggos_dict, orient='index').reset_index(drop=True)
    df.to_csv('dogs_data.csv', index=False)

