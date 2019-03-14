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
    return dataframe[dataframe.country.isin(relevant_countries)], relevant_countries


def feature_modification(original_df):
    original_df['suicide_ratio'] = (original_df.suicides_no / original_df.population) * 10000
    new_df = original_df.drop(columns=['population', 'suicides_no'])
    new_df['is_WC_year'] = original_df.year.isin(WC_years)
    new_df['is_host'] = False
    new_df['in_finals'] = False
    new_df['participant'] = False
    new_df['won'] = False
    for y, host in WC_dict:
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
    df_m = original_df[original_df.sex == 'male']
    df_f = original_df[original_df.sex == 'female']
    age_groups = set(original_df["age"])
    df_m_by_age = {}
    df_f_by_age = {}
    for age in age_groups:
        df_m_by_age[age] = df_m[df_m.age == age]
        df_f_by_age[age] = df_f[df_f.age == age]

    return df_m, df_f, df_m_by_age, df_f_by_age


def get_effect(group, countries, suicide_dict):
    eff_list = []
    for year in WC_years:
        for country in group[year]:
            if country not in countries or suicide_dict[country][year] == 'no_info':
                continue
            eff_list.append(suicide_dict[country][year].effect)
    return sum(eff_list) / len(eff_list)


if __name__ == "__main__":

    # ----------------------LOAD DATA---------------------------------
    df, WC_countries = load_dataframe()
    # ----------------------PREPROCESSING---------------------------------
    """Preprocessing: remove NaN and years where country has 0 population"""
    clean_nan(df)
    clean_zeros(df)
    # ----------------------FEATURE MODIFICATION---------------------------------
    """adding/removing features to dataframe"""
    df = feature_modification(df)
    # ----------------------SPLITTING DATAFRAMES---------------------------------
    """creating new dataframes by features"""
    df_male, df_female, df_male_by_age, df_female_by_age = split_dataframe(df)

    # ----------------------OBTAINING COUNTRY GRAPHS---------------------------------
    """visualization of data"""
    if PARAMETERS['Visualize']:
        graphs_all_country(df, WC_countries)
        graphs_by_country(df, 'France', 'male')

    # ----------------------OBTAINING SUICIDE INFORMATION---------------------------------
    """obtaining Observation objects per country and WC year"""
    WC_suicide_dict, WC_countries = get_observations(df, WC_countries, sex=None, age=None)

    # ----------------------TESTS---------------------------------
    """
    To test:
        1) suicide statistics for all countries (global effect)
        2) suicide statistics for all participating countries (participation effect)
        3) suicide statistics for all finalist countries (finalist effect)
        4) suicide statistics for all winning countries (winning effect)
        5) split countries into groups with significant positive or negative effect 
    """

    """TEST (1) + TEST (5) - global effect & significant effect"""
    global_country_eff = []
    sig_positive_eff = []
    sig_negative_eff = []
    for country in WC_suicide_dict:
        yearly_eff = [WC_suicide_dict[country][x].effect for x in
                      WC_suicide_dict[country] if WC_suicide_dict[country][x] != 'no_info']
        avg_eff = sum(yearly_eff)/len(yearly_eff)
        global_country_eff.append(avg_eff)

        """splitting to significant effect countries""" #TODO define avg_eff better
        if avg_eff > 2:
            sig_positive_eff.append([country, avg_eff])
        elif avg_eff < -2:
            sig_negative_eff.append([country, avg_eff])
    global_avg_eff = np.mean(global_country_eff)

    """TEST (2) - participation effect"""
    participant_avg_eff = get_effect(WC_participants_by_year, WC_countries, WC_suicide_dict)

    """TEST (3) - finalist effect"""
    finalists_avg_eff = get_effect(WC_finals, WC_countries, WC_suicide_dict)

    """TEST (4) - winner effect"""
    winner_avg_eff = get_effect(WC_winners, WC_countries, WC_suicide_dict)

    for country, avg_eff in sig_positive_eff:
        print()

    # ----------------------MORE GRAPHS---------------------------------




    print()