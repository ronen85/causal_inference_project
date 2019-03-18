import pandas as pd
import copy
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
import csv
from Observation import *
from visualization import *
from preprocessing import *
from utilities import *

ids = ["200827384", "034749473"]


def load_dataframe():
    """load the dataframe """

    """Read the Data"""
    dataframe = pd.read_csv('./data/WHO.csv', header=0)
    """Dataframes by country"""
    dataframe["country"] = dataframe["country"].astype('category')
    who_countries = set(dataframe["country"])
    countries = who_countries.intersection(WC_participants)
    """add countries that were removed due to different spelling between the lists"""
    added_by_hand = {'Switzerland', 'United States of America', 'Russian Federation', 'Iran (Islamic Rep of)',
                     'Republic of Korea'}
    relevant_countries = countries.union(added_by_hand)
    dataframe = dataframe[dataframe.country.isin(relevant_countries)]

    """keep only relevant years"""
    relevant_years = []
    for y in WC_years:
        relevant_years.append(y-1)
        relevant_years.append(y)
        relevant_years.append(y+1)

    df_ate = dataframe.loc[dataframe.year.isin(relevant_years)]

    min_population = 5 * 10 ** 6
    cs = list(df_ate.country.unique())
    country_size_dict = {}
    for c in cs:
        for y in range(1980,2016):
            info = df_ate.loc[(df_ate.country == c) & (df_ate.year == y)]
            if info.__len__():
                country_size_dict[c] = np.sum(info.population)
                # country_size = np.sum(df_ate.loc[(df_ate.country == c) &
                #                                  (df_ate.year.unique()[0] == df_ate.year)].population)
                if country_size_dict[c] < min_population:
                    df_ate.drop(df_ate.loc[df_ate.country == c].index, inplace=True)
                    relevant_countries.remove(c)

    return df_ate, relevant_countries


def feature_modification(original_df):
    original_df['suicide_ratio'] = (original_df.suicides_no / original_df.population) * 100000
    new_df = original_df.drop(columns=['population', 'suicides_no'])
    new_df['is_WC_year'] = original_df.year.isin(WC_years)
    new_df['is_host'] = False
    new_df['in_finals'] = False
    new_df['participant'] = False
    new_df['won'] = False
    for y, host in WC_dict.items():
        idx1 = new_df[(new_df.year == y) & (new_df.country == host)].index.values
        if len(idx1):
            for i in idx1:
                new_df.at[i, 'is_host'] = True
        idx2 = new_df[(new_df.year == y) & (new_df.country.isin(WC_finals[y]))].index.values
        if len(idx2):
            for i in idx2:
                new_df.at[i, 'in_finals'] = True
        idx3 = new_df[(new_df.year == y) & (new_df.country.isin(WC_participants_by_year[y]))].index.values
        if len(idx3):
            for i in idx3:
                new_df.at[i, 'participant'] = True
        idx4 = new_df[(new_df.year == y) & (new_df.country == WC_winners[y])].index.values
        if len(idx4):
            for i in idx4:
                new_df.at[i, 'won'] = True
    return new_df


def split_dataframe(original_df):
    """split df by: male, female and by age"""
    age_groups = ['15-24 years', '25-34 years', '35-54 years', '55-74 years']
    df_m = original_df[(original_df.sex == 'male') & (original_df.age.isin(age_groups))]
    df_f = original_df[(original_df.sex == 'female') & (original_df.age.isin(age_groups))]
    df_m_by_age = {}
    df_f_by_age = {}
    for age in age_groups:
        df_m_by_age[age] = df_m[df_m.age == age]
        df_f_by_age[age] = df_f[df_f.age == age]

    df_a = {
        'Male': df_m_by_age,
        'Female': df_f_by_age
    }
    return df_a, df_m, df_f, df_m_by_age, df_f_by_age


def get_effect(group, countries, suicide_dict):
    eff_list = []
    for year in WC_years:
        for country in group[year]:
            if country not in countries or suicide_dict[country][year] == 'no_info':
                continue
            eff_list.append(suicide_dict[country][year].effect)
    return np.mean(eff_list)


if __name__ == "__main__":

    # ----------------------LOAD DATA---------------------------------
    df, PARAMETERS['countries'] = load_dataframe()
    # ----------------------PREPROCESSING---------------------------------
    """Preprocessing: remove NaN and years where country has 0 population"""
    clean_nan(df)
    clean_zeros(df)
    # ----------------------FEATURE MODIFICATION---------------------------------
    """adding/removing features to dataframe"""
    df = feature_modification(df)
    # ----------------------SPLITTING DATAFRAMES---------------------------------
    """creating new dataframes by features"""
    df_all, df_male, df_female, df_male_by_age, df_female_by_age = split_dataframe(df)

    # ----------------------OBTAINING SUICIDE INFORMATION---------------------------------
    """get graphs of ate per year for participants"""
    WC_suicide_dict_m = get_observations(df_male)
    WC_suicide_dict_f = get_observations(df_female)
    M_participant_ate, F_participant_ate = [], []
    for year in WC_years:
        count = []
        for country in WC_participants_by_year[year]:
            if country in WC_suicide_dict_m:
                if WC_suicide_dict_m[country][year] != 'no_info':
                    count.append(WC_suicide_dict_m[country][year].ate)
        M_participant_ate.append(np.mean(count))
        count = []
        for country in WC_participants_by_year[year]:
            if country in WC_suicide_dict_f:
                if WC_suicide_dict_f[country][year] != 'no_info':
                    count.append(WC_suicide_dict_f[country][year].ate)
        F_participant_ate.append(np.mean(count))

    bar_graph('Participating', 'All', 'Male', M_participant_ate, WC_years)
    bar_graph('Participating', 'All', 'Female', F_participant_ate, WC_years)

    # """get graphs of ate per Country in specific year"""
    # for age_grp in df_male_by_age:
    #     for sex in df_all:
    #         WC_suicide_dict = get_observations(df_all[sex][age_grp])
    #         for year in WC_years:
    #             """Global"""
    #             count, country_list = [], []
    #             for country in PARAMETERS['countries']:
    #                 if country in WC_suicide_dict:
    #                     if WC_suicide_dict[country][year] != 'no_info':
    #                         count.append(WC_suicide_dict[country][year].ate)
    #                         country_list.append(country)
    #
    #             bar_graph('Global', age_grp, sex, count, country_list, year)
    #
    # """get graphs of ate per year for participants/finalists/winners by gender and age group"""
    # for age_grp in df_male_by_age:
    #     for sex in df_all:
    #         WC_suicide_dict = get_observations(df_all[sex][age_grp])
    #         participant_ate, finalist_ate, winner_ate, hosts_ate = [], [], [], []
    #         for year in WC_years:
    #             """participants"""
    #             count = []
    #             for country in WC_participants_by_year[year]:
    #                 if country in WC_suicide_dict:
    #                     if WC_suicide_dict[country][year] != 'no_info':
    #                         count.append(WC_suicide_dict[country][year].ate)
    #             participant_ate.append(np.mean(count))
    #             """finalists"""
    #             count = []
    #             for country in WC_finals[year]:
    #                 if country in WC_suicide_dict:
    #                     if WC_suicide_dict[country][year] != 'no_info':
    #                         count.append(WC_suicide_dict[country][year].ate)
    #             finalist_ate.append(np.mean(count))
    #             """winners"""
    #             count = []
    #             for country in WC_winners[year]:
    #                 if country in WC_suicide_dict:
    #                     if WC_suicide_dict[country][year] != 'no_info':
    #                         count.append(WC_suicide_dict[country][year].ate)
    #             winner_ate.append(np.mean(count))
    #             """Hosts"""
    #             count = []
    #             country = WC_dict[year]
    #             if country in WC_suicide_dict:
    #                 if WC_suicide_dict[country][year] != 'no_info':
    #                     count.append(WC_suicide_dict[country][year].ate)
    #             hosts_ate.append(np.mean(count))
    #
    #         bar_graph('Participating', age_grp, sex, participant_ate, WC_years)
    #         bar_graph('Finalist', age_grp, sex, finalist_ate, WC_years)
    #         bar_graph('Winning', age_grp, sex, winner_ate, WC_years)
    #         bar_graph('Hosting', age_grp, sex, hosts_ate, WC_years)

    # """get graphs of ate for specific Country for all years"""
    # country = "Brazil"
    # for age_grp in df_male_by_age:
    #     for sex in df_all:
    #         WC_suicide_dict = get_observations(df_all[sex][age_grp][df_all[sex][age_grp].country == 'Brazil'])
    #         count = []
    #         for year in WC_years:
    #             if country in WC_suicide_dict:
    #                 if WC_suicide_dict[country][year] != 'no_info':
    #                     count.append(WC_suicide_dict[country][year].ate)
    #
    #         bar_graph('Country', age_grp, sex, count, WC_years, None, country)
    print()
