# pip install bs4 requests pandas lxml
from bs4 import BeautifulSoup as BS
import requests
import pandas as pd


# creating 2 lists; 'links' contains links to the detailed pages of memes, 'names' contains names of memes
def get_links_and_names(soup):
    all_names = soup.find_all(attrs={'rel': 'bookmark'})
    links = []
    names = []
    for name in all_names:
        links.append(name['href'])
        names.append(name.text)
    return links, names


# creating a list of categories
def get_categories(soup):
    all_categories = soup.find_all(class_='bb-cat-links')
    categories = []
    for category in all_categories:
        raw_categories = []
        for raw_category in category.find_all(attrs={'rel': 'category tag'}):
            raw_categories.append(raw_category.text)
        categories.append(raw_categories)
    return categories


# creating 4 lists - years, origins, values and image urls
def get_years_origins_values_image(links):
    years = []
    origins = []
    values = []
    image_urls = []
    for link in links:
        add_info_page = requests.get(link)
        add_info_soup = BS(add_info_page.text, 'lxml')
        # year of meme
        year = add_info_soup.find(class_='entry-date published').text[:10]
        years.append(year)
        # value and origin of meme
        origin = ''
        value = ''
        sibling = add_info_soup.find_all('h2')[1].next_sibling
        while sibling and sibling.text != 'Значение':
            origin += sibling.text
            sibling = sibling.next_sibling
        sibling = add_info_soup.find_all('h2')[2].next_sibling
        while sibling and sibling.text != 'Галерея':
            value += sibling.text
            sibling = sibling.next_sibling
        origins.append(origin)
        values.append(value)
        # image of meme
        image_urls.append(add_info_soup.find_all('img')[4]['src'])
    return years, origins, values, image_urls


def main():
    result_df = pd.DataFrame()
    for page in range(3):
        url = f'https://memepedia.ru/memoteka/page/{page + 1}'
        s = requests.get(url)
        soup = BS(s.text, 'lxml')
        links, names = get_links_and_names(soup=soup)
        categories = get_categories(soup=soup)
        years, origins, values, image_urls = get_years_origins_values_image(links=links)
        table = pd.DataFrame({'Meme': names, 'Link': links, 'Origin': origins, 'Values': values, 'Full Date': years,
                              'Year': list(map(lambda x: x[-4:], years)), 'Categories': categories, 'Image': image_urls})
        print(f'Table №{page + 1}:\n{table}')
        result_df = pd.concat([result_df, table], axis=0)
    result_df.reset_index(inplace=True, drop=True)
    result_df.to_csv('output-data.csv')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    main()
