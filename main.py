import numpy as np
import pandas as pd
import copy
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
import csv
from Observation import *
from visualization import *
from preprocessing import *

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


if __name__ == "__main__":

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
    if visualize:
        graphs_all_country(df)
        graphs_by_country(df, 'France', 'male')

    # ----------------------OBTAINING SUICIDE INFORMATION---------------------------------

    WC_suicide_dict = {}

    for country in WC_countries:
        suicide_dict_country = {}
        for year in WC_years:
            """check if the database holds at lease 4 of the required years (including the WC one)"""
            if check_years(df, year, country):
                """create Observation object"""
                suicide_dict_country[year] = Observation(df, country, year)
            else:
                suicide_dict_country[year] = 'no_info'
        WC_suicide_dict[country] = suicide_dict_country
    print()

    # -------------------------------------------------------
    """Test case """
    # country = 'Germany'
    # year = '1994'
    #
    # """check if this information exists"""
    # if df[(df.year == int(year)-2) & (df.country == country)].__len__():
    #     """create Observation object"""
    #     WC_suicide_dict[country + year] = Observation(df, country, year)
    # else:
    #     WC_suicide_dict[country + year] = 'no_info'
    #
    # WC_suicide_dict[country + year].get_suicide_num(int(year), ['15-24 years', '25-34 years'])
    # WC_suicide_dict[country + year].get_population(int(year), ['15-24 years'])
    # -------------------------------------------------------

"""
Treatments:
    1) WC year
    2) WC year + country participates
    3) WC year + country host
    4) WC year + country in finals
"""
