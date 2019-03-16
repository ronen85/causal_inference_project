import pandas as pd
import copy
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
import csv
from Observation import *
from visualization import *
from preprocessing import *
from utilities import *
from main import *

def load_dataframe():
    """load the dataframe """

    """Read the Data"""
    dataframe = pd.read_csv('./data/WHO.csv', header=0)
    """Dataframes by country"""
    dataframe["country"] = dataframe["country"].astype('category')
    # who_countries = set(dataframe["country"])
    # countries = who_countries.intersection(WC_participants)
    """add countries that were removed due to different spelling between the lists"""
    # added_by_hand = {'Switzerland', 'United States of America', 'Russian Federation', 'Iran (Islamic Rep of)',
    #                  'Republic of Korea'}
    # relevant_countries = countries.union(added_by_hand)
    # return dataframe[dataframe.country.isin(relevant_countries)], relevant_countries
    return dataframe

def get_sr(df, country_name, year):
    rel_df = df.loc[(df.country == country_name) & (df.year == year)]
    sr = np.sum(rel_df.suicides_no)/np.sum(rel_df.population) * 10**5
    if np.isnan(sr):
        print("problem in %s %f"%(country_name,year))
    return sr

def get_nsr(df, country_name, year):
    s0 = get_sr(df, country_name, year - 1)
    s1 = get_sr(df, country_name, year)
    s2 = get_sr(df, country_name, year + 1)
    nsr = (s1 - 0.5*(s2 + s0))/(1 + np.var([s0,s1,s2]))
    return nsr

def get_ate(df, country_name, year):
    """
    ATE = Y1 - Y0
    Y1 = suicide rate in country (for 100K people)
    Y0 = estimated suicide rate.
    We estimate Y0 to be the average sr in the neighboring years.
    :param df:
    :param country_name:
    :param year:
    :return:
    """
    Y1 = get_sr(df,country_name,year)
    Y0 = 0.5*(get_sr(df,country_name,year-1) +
              get_sr(df,country_name,year+1))
    ATE = Y1 - Y0
    return ATE

if __name__ == '__main__':
    make_new_df = True

    if make_new_df:
        df = load_dataframe()
        # raw_df = pd.read_csv('./data/WHO.csv', header=0)

    """compute ate for the wc in year X"""
    wc_year = 2010
    # take only relevant years
    df_ate = df.loc[df.year.isin([wc_year - 1, wc_year, wc_year + 1])]
    # remove nan values
    df_ate = df_ate.loc[(~np.isnan(df_ate.suicides_no))]
    df_ate = df_ate.loc[(~np.isnan(df_ate.population))]
    # remove countries with missing data
    cs = df_ate.country.unique()
    l = list(range(wc_year - 1, wc_year + 2))
    for c in cs:
        if np.sum(tuple((df_ate.country == c) & (df_ate.year.isin(l)))) != 36:
            print('Missing data in %s in years around %s'%(c,wc_year))
            df_ate.drop(df_ate.loc[df.country == c].index, inplace=True)
    # remove small countries
    min_population = 5*10**6
    cs = list(df_ate.country.unique())
    country_size_dict = {}
    for c in cs:
        country_size_dict[c] = np.sum(df_ate.loc[(df_ate.country == c) &
                                         (df_ate.year.unique()[0] == df_ate.year)].population)
        # country_size = np.sum(df_ate.loc[(df_ate.country == c) &
        #                                  (df_ate.year.unique()[0] == df_ate.year)].population)
        if country_size_dict[c] < min_population:
            print('%s is too small, we dropped it'%(c,))
            df_ate.drop(df_ate.loc[df.country == c].index, inplace=True)
            df_ate.drop(df_ate.loc[(df_ate.country == c)].index, inplace=True)
    # remove zeros
    cs = list(df_ate.country.unique())
    ys = list(df_ate.year.unique())
    for c in cs:
        for y in ys:
            sum_of_suicide = np.sum(df_ate.loc[(df_ate.country == c) & (df_ate.year == y)].suicides_no)
            if sum_of_suicide == 0:
                # print('in %s in the year %d the number of suicides is zero'%(c,y))
                df_ate.drop(df_ate.loc[(df_ate.country == c) & (df_ate.year == y)].index, inplace=True)
    # collect data
    ate_dict = {}
    cs = list(df_ate.country.unique())
    for c in cs:
        ate_dict[c] = (get_ate(df_ate,c,wc_year), country_size_dict[c])
    # compute ate
    naive_ate = np.average(tuple(a[0] for a in tuple(ate_dict.values()))) # average ate without considering population
    average_ate = np.sum(tuple(a[0]*a[1] for a in tuple(ate_dict.values())))/\
                  np.sum(tuple(a[1] for a in tuple(ate_dict.values()))) # average ate considering the population
    # compute ate for participants only
    cs = [k for k in ate_dict.keys() if k in WC_participants_by_year[wc_year]]
    parts_ate_dict = {}
    for c in cs:
        parts_ate_dict[c] = ate_dict[c]
    parts_naive_ate = np.average(tuple(a[0] for a in tuple(parts_ate_dict.values())))  # average ate without considering population
    parts_average_ate = np.sum(tuple(a[0] * a[1] for a in tuple(parts_ate_dict.values()))) / \
                  np.sum(tuple(a[1] for a in tuple(parts_ate_dict.values())))  # average ate considering the population

    # plot it
    plt.title("Change in Suicide Rates in 2010")
    plt.ylabel('ATE = Y1 - Y0')
    plt.xlabel('Carrier')
    barlist = plt.bar(range(len(ate_dict)), list(a[0] for a in ate_dict.values()), align='center')
    for i in range(len(ate_dict)):
        if list(ate_dict.keys())[i] in WC_participants_by_year[wc_year]:
            barlist[i].set_color('r')
    plt.xticks(range(len(ate_dict)), list(ate_dict.keys()), rotation='vertical')
    plt.show()
    print('test')

