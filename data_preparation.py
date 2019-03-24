import pprint
from googleapiclient.discovery import build
import urllib
from bs4 import BeautifulSoup
import requests
import webbrowser
import re
from pytrends.request import TrendReq
import pandas as pd
from Site import Site


class Data_Preparation:
    def __init__(self):
        self.LA_countries_and_codes = {"Argentina": "ar", "Bolivia" :"bo",
        "Brazil" : "br", "Chile" : "cl", "Colombia" : "co", "Costa Rica" : "cr",
        "Cuba": "cu", "Dominican Republic" : "do",  "Ecuador" : "ec", "El Salvador" : "sv",
        "Guatemala" : "gt", "Haiti": "ht", "Honduras" : "hn", "Mexico" : "mx",
        "Nicaragua" : "ni", "Panama" : "pa", "Paraguay" : "py", "Peru": "pe",
         "Uruguay": "uy", "Venezuela": "ve"}


        self.__country_factory__()

    def __country_factory__(self):


        self.__filter_sites__()

    '''
    def __get_candidates__(self, country):
        if type(country) is not Country:
            raise TypeError("__get_candidates__ expects a Country object as parameter")

        if country.name == "Brazil":
            lr = "lan_pt"
            queries = ['séries e filmes torrent gratis', 'séries e filmes online gratis']
        else:
            lr = "lan_es"
            queries = ['peliculas y series online gratis', 'peliculas y series torrent gratis']


        query = urllib.parse.quote_plus(query)

        url = 'https://google.com/search?start=1&lr='+lr+'&gl='+country.code+'&q=' + query
        proxyDict = {
              "http"  : "177.69.122.180:8080"
            }
        response = requests.get(url, proxies=proxyDict)

        soup = BeautifulSoup(response.text, 'lxml')
        print(soup)
        for g in soup.find_all(class_='g'):
            print(g.text)
            print('-----')'''

    def __is_a_url__(self, url):
        if not isinstance(url, str):
            raise TypeError('url must to be a string')

        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, "http://www.example.com") is not None

    def __get_the_site_name_from_URL(self, url):
        if not self.__is_a_url__(url):
            raise TypeError("Typerror: url must have URL format")

    def __filter_sites__(self):
        df = self.__load_candidate_file__()

        # remove the duplicate sites
        df = df.drop_duplicates(subset='Top Sites on Google', keep="last")

        filtered_site_list = []

        for index, row in df.iterrows():

            a = row['Top Sites on Google'].split(".")
            if a[0].split('//')[1] == 'www':
                site_name = a[1]
            else:
                site_name = a[0].split("//")[1]

            if row['Country'] == 'Brazil':
                lang = 'pt-BR'
            else:
                lang ='es'

            self.__filter_by_related_topics__(site_name, row['Top Sites on Google'], lang, filtered_site_list)

        self.__create_xlsx_files__(filtered_site_list=filtered_site_list)

    def __create_xlsx_files__(self, filtered_site_list):

        if all(not isinstance(n, Site) for n in filtered_site_list):
            raise TypeError("TypeError: filtered_site_list must to be a list of Site objects")

        # create the dataframe that will contain the access statistics
        df_filtered_sites_access_statistics = pd.DataFrame(columns=['site_name', 'lang', 'site_url',
        'monthly_visits_in_milions', 'average_visit_time', 'average_visited_pages', 'bounce_rate'])

        # create the DF that will contain the interest infornation about the sites
        df_filtered_sites_interest_over_time = pd.DataFrame(columns=['site_name', 'date', 'interest_percentage'])

        # Create the XLSX files that will con
        for s in filtered_site_list:
            df_filtered_sites_access_statistics = df_filtered_sites_access_statistics.append({'site_name': s.name,
            'lang': s.lang, 'site_url': s.url}, ignore_index=True)

            df_google_trends = self.__get_interest_over_time__(s.name, s.lang)

            for index, row in df_google_trends.iterrows():
                df_filtered_sites_interest_over_time = df_filtered_sites_interest_over_time.append({'site_name' : s.name,
                 'date' : index, 'interest_percentage': row[s.name]}, ignore_index=True)

        df_filtered_sites_access_statistics = df_filtered_sites_access_statistics.drop_duplicates(subset='site_name', keep="last")

        # save the files that will contain the data about the filtered sites
        df_filtered_sites_interest_over_time.to_excel('sites_interest_over_time.xlsx')
        df_filtered_sites_access_statistics.to_excel("sites_access_statistics.xlsx")

    def __load_candidate_file__(self):
        df = pd.read_excel("initial_candidates.xlsx")
        return df

    def __check_if_is_piracy_related__(self, related_topics):
        if type(related_topics) is not list or all(not isinstance(n, str) for n in related_topics):
            raise TypeError("TypeError: related_topics must to be a list of strings")

        # categories of interested that were empirically defined
        categories_of_interest = ['torrent', 'download', 'upload',
            'television series', 'film', 'movie', 'subtitle']

        # verify if at least one category of interest is substring of a
        # related topic
        for c in categories_of_interest:
            for r in related_topics:
                if c in r:
                    return True
        return False


    def __filter_by_related_topics__(self, term, url, lang, filtered_site_list):
        if type(term) is not str or type(lang) is not str or type(filtered_site_list) is not list:
            raise TypeError('''TypeError: Please, term and lang must to be strings,
                and name_list must to be a list''')


        pytrends = TrendReq(hl=lang, tz=360, geo='')
        kw_list = [term]
        pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')

        # get the related topics to the search term (site name)
        related_topics = pytrends.related_topics()[term]
        if related_topics is not None:
            related_t = list(related_topics['title'])
            related_t = [t.lower() for t in related_t]
            # checks if the related topics are piracy related
            if self.__check_if_is_piracy_related__(related_topics=related_t):
                filtered_site_list.append(Site(term, url, lang))


    def __get_interest_over_time__(self, site_name, lang):
        if type(site_name) is not str or type(lang) is not str:
            raise TypeError('''TypeError: Please, site_name and lang must to be a strings''')

        pytrends = TrendReq(hl=lang, tz=360, geo='')
        kw_list = [site_name]
        pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')
        # returns a dataframe with the relative interest of a site over time
        return pytrends.interest_over_time()


rank = Data_Preparation()
