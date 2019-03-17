"""create class for our observations"""
from utilities import *


class Observation:
    def __init__(self, df, country, year):
        self.country = country
        self.wc_year = year
        year_range = PARAMETERS['Year_Range']
        self.years = list(range(year - year_range, year + year_range + 1))
        """get information per year"""
        info = [df[(df['year'] == x) & (df['country'] == self.country)] for x in self.years]
        self.info_per_year = dict(zip(self.years, info))
        self.suicide_avg, self.wc_year_ratio, self.ate = self.get_suicide_diff()
        self.paticipated = self.info_per_year[year].participant.values[0]
        self.finalist = self.info_per_year[year].in_finals.values[0]
        self.won = self.info_per_year[year].won.values[0]

    def get_suicide_diff(self):
        """get difference between WC year to other years"""
        avg_years = [x for x in self.info_per_year if self.info_per_year[x].__len__()]
        avg_years.remove(self.wc_year)
        suicide_ratio_list = [sum(self.info_per_year[year].suicide_ratio) for year in avg_years]
        avg = np.mean(suicide_ratio_list)
        # std = np.std(suicide_ratio_list)
        wc_ratio = sum(self.info_per_year[self.wc_year].suicide_ratio)
        eff = (wc_ratio - avg) #/ (1 + std)
        return avg, wc_ratio, eff


def check_years(df, year, country):
    """check if the database holds the required info"""
    if not df[(df.year == year) & (df.country == country)].__len__():
        return False
    count = 0
    if PARAMETERS['Year_Range'] == 1:
        for i in range(-1, 2):
            if df[(df.year == year + i) & (df.country == country)].__len__():
                count += 1
        if count == 3:
            return True
    else:
        for i in range(-2, 3):
            if df[(df.year == year + i) & (df.country == country)].__len__():
                count += 1
        if count >= 4:
            return True


def get_observations(df):
    countries = PARAMETERS['countries']
    all_suicide_dict = {}
    new_countries = list(countries)
    for country in countries:
        instances = len(WC_years)
        suicide_dict_country = {}
        for year in WC_years:
            """check if the database holds at lease 4 of the required years (including the WC one)"""
            if check_years(df, year, country):
                """create Observation object"""
                suicide_dict_country[year] = Observation(df, country, year)
            else:
                suicide_dict_country[year] = 'no_info'
                instances -= 1

        """check if there is enough observations for this country"""
        # #TODO decide if this is enough
        # if instances >= 4:
        all_suicide_dict[country] = suicide_dict_country
        # else:
        #     new_countries.remove(country)
    return all_suicide_dict #, set(new_countries)
