"""create class for our observations"""


class Observation:
    def __init__(self, df, country, year):
        self.country = country
        self.WC_year = year
        self.years = list(range(int(year) - 2, int(year) + 3))

        """get information per year"""
        info = [df[(df['year'] == x) & (df['country'] == self.country)] for x in self.years]
        self.info_per_year = dict(zip(self.years, info))

        self.suicide_ratio_per_year, self.suicide_diff = self.get_suicide_diff()

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

    def get_suicide_diff(self, age=None, sex=None):
        """get difference between WC year to other years"""
        suicide_ratio_per_year = {}
        for year in self.info_per_year:
            population = self.get_population(year, age, sex)
            suicide_num = self.get_suicide_num(year, age, sex)
            if population and suicide_num:
                try:  # requires preprocessing of WHO database
                    suicide_ratio_per_year[year] = suicide_num/population
                except:
                    print()

        wc_ratio = suicide_ratio_per_year[int(self.WC_year)]
        ratio_list = [suicide_ratio_per_year[x] for x in suicide_ratio_per_year if x != self.WC_year]
        avg = sum(ratio_list)/len(ratio_list)

        return suicide_ratio_per_year, avg-wc_ratio


