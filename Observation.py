"""create class for our observations"""


class Observation:
    def __init__(self, df, country, year):
        self.country = country
        self.WC_year = year
        self.years = list(range(int(year) - 2, int(year) + 3))

        """get information per year"""
        info = [df[(df['year'] == x) & (df['country'] == self.country)] for x in self.years]
        self.info_per_year = dict(zip(self.years, info))

    def get_suicide_num(self, year, age=None, sex=None):
        assert year in self.years, "Desired year is not in Observation Years"
        info = self.info_per_year[year]
        if age:
            info = info[info.age.isin(age)]
        if sex:
            info = info[info.sex == sex]
        return sum(list(info.suicides_no))

    def get_population(self, year, age=None, sex=None):
        assert year in self.years, "Desired year is not in Observation Years"
        info = self.info_per_year[year]
        if age:
            info = info[info.age.isin(age)]
        if sex:
            info = info[info.sex == sex]
        return sum(list(info.population))


