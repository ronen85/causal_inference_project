"""create class for our observations"""
from utilities import *

class Observation:
    def __init__(self, df, country, year, age=None, sex=None):
        self.country = country
        self.wc_year = year
        self.years = list(range(year - 2, year + 3))

        """get information per year"""
        info = [df[(df['year'] == x) & (df['country'] == self.country)] for x in self.years]
        self.info_per_year = dict(zip(self.years, info))
        self.suicide_avg, self.wc_year_ratio, self.suicide_diff_percentage = self.get_suicide_diff(age, sex)

        self.paticipated = self.info_per_year[year].participant.values[0]
        self.finalist = self.info_per_year[year].in_finals.values[0]
        self.won = self.info_per_year[year].won.values[0]


    def get_suicide_ratio(self, year, age=None, sex=None):
        assert year in self.years, "Desired year is not in Observation Years"
        info = self.info_per_year[year]
        if age:
            info = info[info.age == age]
        if sex:
            info = info[info.sex == sex]
        return sum(list(info.suicide_ratio))

    def get_suicide_diff(self, age=None, sex=None):
        """get difference between WC year to other years"""
        avg_years = [x for x in self.info_per_year if self.info_per_year[x].__len__()]
        avg_years.remove(self.wc_year)
        avg = sum([self.get_suicide_ratio(year, age, sex) for year in avg_years])/len(avg_years)
        wc_ratio = self.get_suicide_ratio(self.wc_year, age, sex)
        return avg, wc_ratio, ((avg - wc_ratio)/avg)*100


def check_years(df, year, country):
    """check if the database holds the required info"""
    if not df[(df.year == year) & (df.country == country)].__len__():
        return False
    # if not sum(df[(df.year == int(year)) & (df.country == country)].population):
    #     return False
    # if not sum(df[(df.year == int(year)) & (df.country == country)].suicides_no):
    #     return False

    count = 0
    for i in range(-2, 3):
        if df[(df.year == year + i) & (df.country == country)].__len__():
            count += 1
    if count >= 4:
        return True


def get_observations(df, countries, age=None, sex=None):
    all_suicide_dict = {}
    new_countries = list(countries)
    for country in countries:
        instances = len(WC_years)
        suicide_dict_country = {}
        for year in WC_years:
            """check if the database holds at lease 4 of the required years (including the WC one)"""
            if check_years(df, year, country):
                """create Observation object"""
                suicide_dict_country[year] = Observation(df, country, year, age, sex)
            else:
                suicide_dict_country[year] = 'no_info'
                instances -= 1

        """check if there is enough observations for this country"""
        if instances >= 4:
            all_suicide_dict[country] = suicide_dict_country
        else:
            new_countries.remove(country)
    return all_suicide_dict, set(new_countries)
