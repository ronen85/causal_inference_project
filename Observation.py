"""create class for our observations"""


class Observation:
    def __init__(self, df, country, year):
        self.country = country
        self.WC_year = year
        self.years = list(range(int(year) - 2, int(year) + 3))

        """get information per year"""
        info = [df[(df['year'] == x) & (df['country'] == self.country)] for x in self.years]
        self.info_per_year = dict(zip(self.years, info))
