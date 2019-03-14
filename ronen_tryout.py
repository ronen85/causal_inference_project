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

if __name__ == '__main__':
    make_new_df = True

    if make_new_df:
        df, WC_countries = load_dataframe()
        # raw_df = pd.read_csv('./data/WHO.csv', header=0)

    """Read the Data"""
    df = pd.read_csv('./data/ronen_df.csv', header=0)
    print('test')

