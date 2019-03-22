import pprint
from googleapiclient.discovery import build
from country import Country
import urllib
from bs4 import BeautifulSoup
import requests
import webbrowser
import re
from pytrends.request import TrendReq

class Ranking:
    def __init__(self):
        self.LA_countries_and_codes = {"Argentina": "ar", "Bolivia" :"bo",
        "Brazil" : "br", "Chile" : "cl", "Colombia" : "co", "Costa Rica" : "cr",
        "Cuba": "cu", "Ecuador" : "ec", "El Salvador" : "sv",
        "Guatemala" : "gt", "Haiti": "ht", "Honduras" : "hn", "Mexico" : "mx",
        "Nicaragua" : "ni", "Panama" : "pa", "Paraguay" : "py", "Peru": "pe",
        "Dominican Republic" : "do", "Uruguay": "uy", "Venezuela": "ve"}

        self.countries = []
        self.__country_factory__()

    def __country_factory__(self):
        for i in self.LA_countries_and_codes.keys():
            self.countries.append(Country(i, self.LA_countries_and_codes[i]))
            self.__get_candidates__(self.countries[-1])

    def __get_candidates__(self, country):
        if type(country) is not Country:
            raise TypeError("__get_candidates__ expects a Country object as parameter")


        '''if country.name == "Brazil":
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

        self.__get__interest_over_time__("megafilmeshd", "pt_BR")


    def __get__interest_over_time__(self, term, lang):

        if type(term) is not str or type(lang) is not str:
            raise TypeError('Please, term and lang must to be strings')

        pytrends = TrendReq(hl=lang, tz=360, geo='')
        kw_list = [term]
        pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')
        print(pytrends.related_topics()[term]['title'])



rank = Ranking()
