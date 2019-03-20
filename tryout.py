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

def remove_nan_from_df(dataframe, inplace = True):
    # removes nan values
    dataframe = dataframe.loc[(~np.isnan(dataframe.suicides_no)) & (~np.isnan(dataframe.population))]
    return dataframe

def check_num_of_records(dataframe, country_name, year):
    num_records = dataframe.loc[(dataframe.country == country_name) & (dataframe.year == year)].index.size
    return num_records == 12

if __name__ == '__main__':
    make_new_df = True
    compute_ate_for_year = False
    compute_ate_for_one_country = False

    if make_new_df:
        df = load_dataframe()
        # raw_df = pd.read_csv('./data/WHO.csv', header=0)

    """compute ate for the wc in year X"""
    if compute_ate_for_year:
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
                df_ate.drop(df_ate.loc[df_ate.country == c].index, inplace=True)
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
        figure(0)
        plt.title("Change in Suicide Rates in %s"%wc_year)
        plt.ylabel('ATE = Y1 - Y0')
        plt.xlabel('Countries')
        barlist = plt.bar(range(len(ate_dict)), list(a[0] for a in ate_dict.values()), align='center')
        for i in range(len(ate_dict)):
            if list(ate_dict.keys())[i] in WC_participants_by_year[wc_year]:
                barlist[i].set_color('r')
        plt.xticks(range(len(ate_dict)), list(ate_dict.keys()), rotation='vertical')
        plt.show()

    """compute ate for one country"""
    if compute_ate_for_one_country:
        country = "France"
        df_ate = df.loc[df.country == country]
        # remove nan values
        df_ate = remove_nan_from_df(df_ate)
        # remove wc years with missing data
        ys = []
        for y in WC_years:
            check = [check_num_of_records(df_ate,country,a) for a in range(y-1,y+2)]
            if not(False in check):
                ys.append(y)
        # compute ate
        ate_dict = {}
        for y in ys:
            ate_dict[y] = get_ate(df_ate,country,y)
        # plot it
        plt.figure(1)
        plt.title("Change in Suicide Rates in %s" % country)
        plt.ylabel('ATE = Y1 - Y0')
        plt.xlabel('Years')
        barlist = plt.bar(range(len(ate_dict)), ate_dict.values(), align='center')
        for i in range(len(ate_dict)):
            if country in WC_participants_by_year[list(ate_dict.keys())[i]]:
                barlist[i].set_color('r')
        plt.xticks(range(len(ate_dict)), list(ate_dict.keys()), rotation='vertical')
        plt.show()

    """compute ate for participants"""
    rel_years = []
    for y in WC_years:
        rel_years += [y-1,y,y+1]
    df_ate = df.loc[df.year.isin(rel_years)]
    # remove nan values
    df_ate = remove_nan_from_df(df_ate)
    # remove small countries
    min_population = 5 * 10 ** 6
    cs = list(df_ate.country.unique())
    country_size_dict = {}
    for c in cs:
        country_size_dict[c] = np.sum(df_ate.loc[(df_ate.country == c) &
                                                 (df_ate.year.unique()[0] == df_ate.year)].population)
        if country_size_dict[c] < min_population:
            print('%s is too small, we dropped it' % (c,))
            df_ate.drop(df_ate.loc[(df_ate.country == c)].index, inplace=True)
    ate_dict = {}
    for y in WC_years:
        participants = WC_participants_by_year[y]
        participants_with_data = [a for a in participants if (a in list(df_ate.loc[df_ate.year == y].country.unique()))]
        ate_list = []
        for p in participants_with_data:
            ate = get_ate(df_ate,p,y)
            if not(np.isnan(ate)):
                ate_list.append(ate)
        ate_dict[y] = np.average(ate_list)
        print('test')



    # df_ate = pd.DataFrame(columns=df.columns)
    # row_year = wc_year
    # row_country = 'participants_in_%s'%wc_year
    # row_sex = None
    # row_age = None
    # row_suicide_no =






    print('tez')
    # df_ate = df_ate.loc[(~np.isnan(df_ate.suicides_no))]
    # df_ate = df_ate.loc[(~np.isnan(df_ate.population))]
    # print('test')
    #