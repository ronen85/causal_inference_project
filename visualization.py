from collections import defaultdict
from matplotlib.pylab import plt
from matplotlib import pyplot as mp
from utilities import *


def graphs_all_country(df):
    countries = PARAMETERS['countries']

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


def graphs_by_country(df, country, sex=None, age=None):
    by_age_dict = defaultdict(list)
    years_dict = defaultdict(list)
    country_df = df[df.country == country]
    if sex:
        country_df = country_df[country_df.sex == sex]
    if age:
        country_df = country_df[country_df.age == age]
    for _, row in country_df.iterrows():
        by_age_dict[row['age'] + '_' + row['sex']].append(row['suicide_ratio'])
        years_dict[row['age'] + '_' + row['sex']].append(row['year'])

    for age in by_age_dict:
        plt.plot(years_dict[age], by_age_dict[age], label=age)

    for year in WC_years:
        plt.axvline(x=year, color='k', linestyle='--')
    plt.legend()
    plt.title(country)
    plt.show()


def world_graph(suicide_dict, cntryz, sex, age):
    eff_mean_list = []
    for year in WC_years:
        eff_list = []
        for c in cntryz:
            if suicide_dict[c][year] != 'no_info':
                eff_list.append(suicide_dict[c][year].effect)
        eff_mean_list.append(np.mean(eff_list))

    plt.figure()
    plt.plot(WC_years, eff_mean_list)
    for year in WC_years:
        plt.axvline(x=year, color='k', linestyle='--')
    plt.legend()
    plt.title('Global, sex='+sex+' , age='+age)
    # plt.show()
    mp.savefig('./graphs/world/'+sex+'_'+age+'.pdf')


def graph_eff_by_country(countries, suicide_dict, sex, age):
    c_list = []
    countrys = []
    for country in countries:
        yearly_eff = [suicide_dict[country][x].effect for x in
                      suicide_dict[country] if suicide_dict[country][x] != 'no_info']
        countrys.append(country)
        c_list.append(np.mean(yearly_eff))

    plt.figure()
    index = list(range(len(countrys)))
    plt.bar(index, c_list, align='center', alpha=0.5)
    plt.xlabel('Country')
    plt.ylabel('Effect')
    plt.xticks(index, countrys, rotation='vertical')
    plt.title('Effect per Country, sex=' + sex + ' , age=' + age)
    plt.axhline(y=1, color='k', linestyle='--')
    plt.axhline(y=-1, color='k', linestyle='--')
    # plt.show()
    mp.savefig('./graphs/by_country/' + sex + '_' + age + '.pdf')


def bar_graph(category, age_grp, sex, x, y, year=None):

    plt.figure()
    if year:
        plt.title("Change in Suicide Rates per Country in %s; %s ages %s" % (year, sex, age_grp))
    else:
        plt.title("Change in Suicide Rates in %s Countries; %s ages %s" % (category, sex, age_grp))
    plt.ylabel('ATE = Y1 - Y0')
    plt.xlabel('Years')
    plt.bar(range(len(x)), x, align='center')
    plt.xticks(range(len(x)), y, rotation='vertical')
    name = category + sex + age_grp + '.png'
    # plt.show()
    plt.tight_layout()
    plt.savefig('./graphs/' + category + '/' + sex + '/' + name.replace(' ',''))
