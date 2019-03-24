import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import operator

class Ranking:
    def __init__(self):
        try:
            self.df_site_access_statistics = pd.read_excel('sites_access_statistics.xlsx')
            self.df_interest_over_time = pd.read_excel('sites_interest_over_time.xlsx')

            self.__access_statistics_analysis__('monthly_visits_in_milions', False)
            self.__access_statistics_analysis__('average_visit_time', False)
            self.__access_statistics_analysis__('average_visited_pages', False)
            self.__access_statistics_analysis__('bounce_rate', True)
            self.__time_interest_over_time_analysis__()
        except FileNotFoundError:
            print('not found')

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
        print(xtickself.df_site_access_statistics['site_name'].head(20))
        
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

        y = y - min_value # shift the range of values to be greater or equal to 0
        print(x_ticks)
        plt.bar(x, y)
        plt.xticks(x, x_ticks, fontsize = 10, rotation=90)
        plt.title('Average Interest Windowded-Growth Rate')
        plt.show()



    def __calculate_average_growth_rate__(self, interest_of_a_site,  window_size):
        average_growth_list = []
        for j in range(1, len(interest_of_a_site), window_size):
            growth_rate_in_window = 0
            for i in range(j, window_size):
                growth_rate_in_window += int(interest_of_a_site[i]) - int(interest_of_a_site[i-1])

            average_growth_list.append(growth_rate_in_window)

        return np.mean(average_growth_list)



r = Ranking()
