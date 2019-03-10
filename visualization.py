from collections import defaultdict
from matplotlib.pylab import plt


def graphs_by_country(df, countries):

    by_country = {}
    for country in countries:
        by_age_dict = defaultdict(list)
        years_dict = defaultdict(list)
        country_df = df[df.country == country]
        for _, row in country_df.iterrows():
            by_age_dict[row['age'] + '_' + row['sex']].append(row['suicides_no'] / row['population'])
            years_dict[row['age'] + '_' + row['sex']].append(row['year'])
        if len(by_age_dict):
            by_country[country] = [by_age_dict, years_dict]

        else:
            print()
            # TODO: remove these countries

        for age in by_age_dict:
            plt.plot(years_dict[age], by_age_dict[age], label=age)
        plt.legend()
        plt.title(country)
        plt.show()