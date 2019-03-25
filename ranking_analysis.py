__author__ = 'rsoares.eduardo@gmail.com (Eduardo R. Soares)'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import operator
from sklearn import preprocessing
from data_preparation import Data_Preparation

class Ranking:
    def __init__(self):
        try:
            self.df_site_access_statistics = pd.read_excel('sites_access_statistics.xlsx')
            self.df_interest_over_time = pd.read_excel('sites_interest_over_time.xlsx')

        except FileNotFoundError:
            dp = Data_Preparation()
            dp.__prepare_data__()

        self.__access_statistics_analysis__('monthly_visits_in_milions', False)
        self.__access_statistics_analysis__('average_visit_time', False)
        self.__access_statistics_analysis__('average_visited_pages', False)
        self.__access_statistics_analysis__('bounce_rate', True)
        self.__time_interest_over_time_analysis__()
        self.__correlation_analysis__()
        self.__final_ranking__()

    def __access_statistics_analysis__(self, field, ascending=False):
        if not isinstance(field, str):
            raise('''field must to be a string''')
        if not isinstance(ascending, bool):
            raise('''ascending must to have bool type''')

        x = np.arange(0, 20, 1)
        self.df_site_access_statistics = self.df_site_access_statistics.sort_values(
        by=[field], ascending=ascending)

        y = self.df_site_access_statistics[field].head(20)
        plt.bar(x, y)
        plt.xticks(x, self.df_site_access_statistics['site_name'].head(20), fontsize = 10, rotation=90)
        plt.title(field + ' by sites')
        plt.show()
        print(self.df_site_access_statistics['site_name'].head(20))

    def __time_interest_over_time_analysis__(self):
        site_dict = {}
        site_name = self.df_interest_over_time['site_name'].unique()
        window_size = 4
        for site in site_name:
            interest_of_a_site = list(self.df_interest_over_time.loc[
            self.df_interest_over_time['site_name'] == site]['interest_percentage'])

            site_dict[site] = self.__calculate_average_growth_rate__(interest_of_a_site, 4)

        sorted_site_average_growth_rate = sorted(site_dict.items(), key=operator.itemgetter(1), reverse=True)
        list_sites = sorted_site_average_growth_rate[:20]
        y = []
        x_ticks = []
        for s in list_sites:
            x_ticks.append(s[0])
            y.append(s[1])
        x = np.arange(0, len(x_ticks), 1)
        min_value = min(y)

        y = y + abs(min_value) # shift the range of values to be greater or equal to 0

        plt.bar(x, y)
        plt.xticks(x, x_ticks, fontsize = 10, rotation=90)
        plt.title('Average Interest Windowded-Growth Rate')
        plt.show()



    def __calculate_average_growth_rate__(self, interest_of_a_site,  window_size):
        if not isinstance(interest_of_a_site, list):
            raise TypeError('''TypeError: interest_of_a_site must to be a list''')

        if not isinstance(window_size, int):
            raise TypeError('''TypeError: window_size must to have int type''')

        average_growth_list = []
        # calculate the difference between the point i and i-1 inside a sliding window
        # with size equals to window_size
        for j in range(1, len(interest_of_a_site), window_size):
            growth_rate_in_window = 0
            for i in range(j, window_size):
                #  int(interest_of_a_site[i]) - int(interest_of_a_site[i-1]) is the increasing
                # rate of the point i in relation to the i - 1
                growth_rate_in_window += int(interest_of_a_site[i]) - int(interest_of_a_site[i-1])

            average_growth_list.append(growth_rate_in_window)

        # returns the average of the increasing rate of sliding windows in time series
        return np.mean(average_growth_list)

    def __correlation_analysis__(self):

        list_columns = self.df_site_access_statistics.columns[3:]

        # scale columns values to improve the visualization
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(self.df_site_access_statistics.iloc[:, 3:])
        df_aux = pd.DataFrame(x_scaled, columns=list_columns)

        # plot the correlation graphic between all access site features
        for i in range(len(list_columns)):
            for j in range(i + 1 , len(list_columns)):
                p = df_aux[list_columns[i]].corr(df_aux[list_columns[j]])
                print(list_columns[i] + " X " + list_columns[j], "Correlation: " +  str(p))

                plt.scatter(df_aux[list_columns[i]],
                df_aux[list_columns[j]])

                plt.xlabel(list_columns[i])
                plt.ylabel(list_columns[j])

                plt.show()

    def __final_ranking__(self):
        top_20 = {}
        site_names = list(self.df_site_access_statistics['site_name'])
        y = []
        x_ticks = []
        for s in site_names:
            monthly_visits_in_milions = float(self.df_site_access_statistics.loc[
            self.df_site_access_statistics['site_name'] == s]['monthly_visits_in_milions'])
            bounce_rate = float(self.df_site_access_statistics.loc[
            self.df_site_access_statistics['site_name'] == s]['bounce_rate'])
            growth_rate_list = list(self.df_interest_over_time.loc[
            self.df_interest_over_time['site_name'] == s]['interest_percentage'])

            growth_rate = self.__calculate_average_growth_rate__(growth_rate_list, 4)
            top_20[s] = [monthly_visits_in_milions, bounce_rate, growth_rate]


        # sorts the list by the sum of monthly_visits_in_milions + average_visited_pages + growth_rate_list
        sorted_top20 = sorted(top_20.items(), key=lambda x: (float(x[1][0]) +
        float(x[1][2])) / float(x[1][1]), reverse=True)


        for top in sorted_top20[:20]:
            x_ticks.append(top[0])

            monthly_visits_in_milions = float(top[1][0])
            bounce_rate = float(top[1][1])
            growth_rate = float(top[1][2])

            # sums monthly_visits_in_milions + bounce_rate + growth_rate_list
            score = (monthly_visits_in_milions + growth_rate) / bounce_rate


            y.append(score)

            print("Site :" + str(top[0]))
            print("Monthly Visits :" + str(monthly_visits_in_milions))
            print("Bounce Rate :" + str(bounce_rate))
            print("Growth Rate  :" + str(growth_rate))
            print('-------------------------------------------------------')

        x = np.arange(0, 20, 1)
        plt.bar(x, y)
        plt.xticks(x, x_ticks, fontsize = 10, rotation=90)
        plt.ylabel("Score")
        plt.title('20 top piracy sites of LatAm')
        plt.show()








r = Ranking()
