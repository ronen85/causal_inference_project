import numpy as np
import pandas as pd
import copy
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
import csv
import requests

import lxml.html as lh
from Observation import *
from visualization import *
from preprocessing import *

ids = ["200827384", "034749473"]
visualize = False

WC_years = ['1982', '1986', '1990', '1994', '1998', '2002', '2006', '2010', '2014']
WC_hosts = ["Spain", "Mexico", "Italy", "United States", "France", "Japan", "Germany", "South Africa", "Brazil"]
WC_finals = {
    1982: ['Italy', 'Germany', 'Poland', 'France'],
    1986: ['Argentina', 'Germany', 'France', 'Belgium'],
    1990: ['Germany', 'Argentina', 'Italy', 'England'],
    1994: ['Brazil', 'Italy', 'Sweden', 'Bulgaria'],
    1998: ['Brazil', 'France', 'Netherlands', 'Croatia'],
    2002: ['Germany', 'Brazil', 'South Korea', 'Turkey'],
    2006: ['Italy', 'France', 'Germany', 'Portugal'],
    2010: ['Netherlands', 'Spain', 'Uruguay', 'Germany'],
    2014: ['Germany', 'Argentina', 'Brazil', 'Netherlands'],
}
WC_dict = zip(WC_years, WC_hosts)


def get_participants_from_web():
    url = 'https://en.wikipedia.org/wiki/All-time_table_of_the_FIFA_World_Cup'
    page = requests.get(url)
    doc = lh.fromstring(page.content)
    tr_elements = doc.xpath('//tr')
    flag = False
    participants = []
    for j in range(3, 82):
        # T is our j'th row
        T = tr_elements[j]
        # Iterate through each element of the row
        for t in T.iterchildren():
            if flag:
                data = t.text_content()[1:-1]
                if '[' in data:
                    data = data[:data.find("[")]
                participants.append(data)
                flag = False
                break
            flag = True
    return set(participants)



if __name__ == "__main__":

    """get all countries that participated in WC"""
    WC_participants = get_participants_from_web()

    """Read the Data"""
    df = pd.read_csv('./data/WHO.csv', header=0)

    """Dataframes by country"""
    df["country"] = df["country"].astype('category')
    who_countries = set(df["country"])
    countries = who_countries.intersection(WC_participants)
    """add countries that were removed due to different spelling between the lists"""
    added_by_hand = {'Switzerland', 'United States of America', 'Russian Federation', 'Iran (Islamic Rep of)',
            'Republic of Korea'}
    countries = countries.union(added_by_hand)

    # ----------------------PREPROCESSING---------------------------------
    """Preprocessing: remove NaN and years where country has 0 population"""

    #TODO: for now-> remove these rows
    """question: how to deal with rows where there is no:
        1) population
        2) suicide number
        3) both
    and how this affects the neighboring years?"""
    clean_nan(df)
    clean_zeros(df)

    # ----------------------FEATURE MODIFICATION---------------------------------
    df['suicide_ratio'] = (df.suicides_no / df.population) * 10000
    new_df = df.drop(columns=['population', 'suicides_no'])
    new_df['is_WC_year'] = df.year.isin(WC_years)
    # new_df['is_host'] = (new_df['is_WC_year']) & (new_df['country'])
    # new_df['is_host'] = new_df['is_WC_year'].apply(lambda x: x.is_integer())
    new_df['is_host'] = False
    for year,host in WC_dict:
        idx = new_df[(new_df.year == int(year)) & (new_df.country == host)].index.values
        if len(idx):
            new_df.loc[idx[0]:idx[-1], :].is_host = True

    # ----------------------SPLITTING DATAFRAMES---------------------------------
    df_male = df[df.sex == 'male']
    df_female = df[df.sex == 'female']

    age_groups = set(df["age"])
    df_male_by_age = {}
    df_female_by_age = {}
    for age in age_groups:
        df_male_by_age[age] = df_male[df_male.age == age]
        df_female_by_age[age] = df_female[df_female.age == age]
    print()

    # ----------------------OBTAINING COUNTRY GRAPHS---------------------------------

    if visualize:
        graphs_by_country(df, countries)



    # ----------------------OBTAINING SUICIDE INFORMATION---------------------------------
    # WC_suicide_dict = {}
    #
    # for year in WC_years:
    #     for country in countries:
    #         """check if the database holds at lease 4 of the required years (including the WC one)"""
    #         if check_years(df, year, country):
    #             """create Observation object"""
    #             WC_suicide_dict[country + year] = Observation(df, country, year)
    #         else:
    #             WC_suicide_dict[country + year] = 'no_info'
    # print()

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
