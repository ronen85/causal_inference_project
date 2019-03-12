"""create class for our observations"""


class Observation:
    def __init__(self, df, country, year):
        self.country = country
        self.wc_year = year
        self.years = list(range(year - 2, year + 3))

        """get information per year"""
        info = [df[(df['year'] == x) & (df['country'] == self.country)] for x in self.years]
        self.info_per_year = dict(zip(self.years, info))
        self.suicide_avg, self.wc_year_ratio, self.suicide_diff_percentage = self.get_suicide_diff()

    def get_suicide_ratio(self, year, age=None, sex=None):
        assert year in self.years, "Desired year is not in Observation Years"
        info = self.info_per_year[year]
        if age:
            info = info[info.age.isin(age)]
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


