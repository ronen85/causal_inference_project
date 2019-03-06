import numpy as np
import pandas as pd
import copy
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
import csv

ids = ["200827384", "034749473"]


def PropensityScore(df):
    """Calculate the propensity score"""
    features = df.drop(["Y", 'T'], axis=1)
    propensity = LogisticRegression()
    propensity = propensity.fit(features, df['T'])
    pscore = propensity.predict_proba(features)[:, 1]
    df_with_ps = copy.deepcopy(df)
    df_with_ps["PS"] = pscore
    return df_with_ps


def IPW(df):
    """calculated as shown in the article"""

    """first fraction in the equation"""
    Y_Treated = (df.loc[df['T'] == 1])['Y'].values
    Sigma_bot1 = len(Y_Treated)
    Sigma_top1 = sum(Y_Treated)
    first_fraction = Sigma_top1/Sigma_bot1

    """second fraction in the equation"""
    Control = df.loc[df['T'] == 0]
    Y_Control = (df.loc[df['T'] == 0])['Y'].values
    eX_div_by_1minuseX = Control['PS']/(1 - Control['PS'])
    Sigma_bot2 = sum(eX_div_by_1minuseX)
    Sigma_top2 = sum(Y_Control * eX_div_by_1minuseX)
    second_fraction = Sigma_top2 / Sigma_bot2

    """The equation"""
    equation = first_fraction - second_fraction
    return equation


def S_Learner(df):

    """splitting to labels and features"""
    features, labels = df.drop('Y', axis=1).values, df['Y'].values

    """Training linear regression model on all data"""
    regr_model = linear_model.LinearRegression().fit(features, labels)

    """splitting to only T=1 features (w/o 'Y')"""
    T1_df = (df.loc[df['T'] == 1]).drop('Y', axis=1)
    T1_features = T1_df.values
    """creating T=0 from the treated"""
    T0_df = copy.deepcopy(T1_df)
    T0_df['T'] = 0
    T0_features = T0_df.values
    """Creating the Tao function"""
    Tao = regr_model.predict(T1_features) - regr_model.predict(T0_features)

    return round(sum(Tao) / len(Tao), 3)


def T_Learner(df):

    """splitting to T=0 and T=1"""
    Treated = (df.loc[df['T'] == 1]).drop('T', axis=1)
    Control = (df.loc[df['T'] == 0]).drop('T', axis=1)

    """splitting to labels vs features"""
    Treated_features, Treated_lbl = Treated.drop('Y', axis=1).values, Treated['Y'].values
    Control_features, Control_lbl = Control.drop('Y', axis=1).values, Control['Y'].values

    """Training linear regression model"""
    regr_T = linear_model.LinearRegression().fit(Treated_features, Treated_lbl)
    regr_C = linear_model.LinearRegression().fit(Control_features, Control_lbl)

    """Creating the Tao function"""
    Tao_T = regr_T.predict(Treated_features) - regr_C.predict(Treated_features)

    return round(sum(Tao_T) / len(Tao_T), 3)


def matching(data, m):

    Y_c = data.loc[data['T'] == 0]['Y'].values
    Y_t = data.loc[data['T'] == 1]['Y'].values
    X_c = data.loc[data['T'] == 0].drop(['Y', 'T'], axis=1).values
    X_t = data.loc[data['T'] == 1].drop(['Y', 'T'], axis=1).values

    matches_t = [match(X_i, X_c, m) for X_i in X_t]
    Yhat_t = np.array([Y_c[idx].mean() for idx in matches_t])
    ITT_t = Y_t - Yhat_t
    return ITT_t.mean()


def norm(X_i, X_m):
    dX = X_m - X_i
    return (dX ** 2).sum(1)


def smallestm(d, m):
    # Finds indices of the smallest m numbers in an array. Tied values are
    # included as well, so number of returned indices can be greater than m.

    # partition around (m+1)th order stat
    par_idx = np.argpartition(d, m)
    return par_idx[:m]


def match(X_i, X_m, m):
    d = norm(X_i, X_m)

    return smallestm(d, m)



if __name__ == "__main__":
    """Read the Data"""
    # removed the index column that started at 1 instead of 0
    df1 = pd.read_csv('data1.csv', header=0).drop('Unnamed: 0', axis=1)
    df2 = pd.read_csv('data2.csv', header=0).drop('Unnamed: 0', axis=1)
    data_frames = [df1, df2]

    # -----------------PRE-PROCESSING---------------------
    set_list = []
    """pre-processing: splitting into categorical and numerical"""
    str_categorical_features = []
    num_categorical_features = []
    for feat in df1.drop(['Y','T'], axis=1):
        """if the feature is categorical"""
        if isinstance(df1[feat].values[0], str):
            str_categorical_features += [feat]
        # TODO defined limit to be 10 for categorical, no specific reason #set len for feature
        elif len(set(df1[feat].values)) < 10:
            num_categorical_features += [feat]

    #     set_list.append(len(set(df1[feat].values)))
    # set_list.sort()

    categorical_featurs = str_categorical_features + num_categorical_features

    """pre-processing: turning categorical to one hot"""
    new_data_frames = []
    for data_frame in data_frames:
        df_new = copy.deepcopy(data_frame)
        df_cat = pd.DataFrame()
        for f in categorical_featurs:
            df_new[f] = copy.copy(df_new[f]).astype("category")
            dummies = pd.get_dummies(df_new[f], prefix=f)
            df_new.drop(columns=f, inplace=True)
            df_cat = pd.concat([df_cat, dummies], axis=1)
        df_new = pd.concat([df_new, df_cat], axis=1)
        new_data_frames.append(df_new)

    # -----------------PROPENSITY SCORE-------------------
    df1_with_PS = PropensityScore(new_data_frames[0])
    df2_with_PS = PropensityScore(new_data_frames[1])

    # -----------------EVALUATING ATT---------------------
    """Matching"""
    ATT_Matching1 = round(matching(new_data_frames[0], 3), 3)
    ATT_Matching2 = round(matching(new_data_frames[1], 3), 3)
    print('Matching for DF1: %f' % ATT_Matching1)
    print('Matching for DF2: %f' % ATT_Matching2)

    """T-Learner"""
    ATT_T_Learner1 = round(T_Learner(new_data_frames[0]), 3)
    ATT_T_Learner2 = round(T_Learner(new_data_frames[1]), 3)
    print('T Learner for DF1: %f' % ATT_T_Learner1)
    print('T Learner for DF2: %f' % ATT_T_Learner2)

    """S-Learner"""
    ATT_S_Learner1 = round(S_Learner(new_data_frames[0]), 3)
    ATT_S_Learner2 = round(S_Learner(new_data_frames[1]), 3)
    print('S Learner for DF1: %f' % ATT_S_Learner1)
    print('S Learner for DF2: %f' % ATT_S_Learner2)

    """IPW"""
    ATT_IPW1 = round(IPW(df1_with_PS), 3)
    ATT_IPW2 = round(IPW(df2_with_PS), 3)
    print('IPW for DF1: %f' % ATT_IPW1)
    print('IPW for DF2: %f' % ATT_IPW2)

    """CHOSEN METHOD"""
    ATT_Chosen1 = round((ATT_IPW1 + ATT_S_Learner1 + ATT_T_Learner1 + ATT_Matching1)/4, 3)
    ATT_Chosen2 = round((ATT_IPW2 + ATT_S_Learner2 + ATT_T_Learner2 + ATT_Matching2)/4, 3)

    """write results to file"""
    data1 = df1_with_PS['PS'].values
    data2 = df2_with_PS['PS'].values
    list1 = ['data1']
    list2 = ['data2']
    for i in range(len(data1)):
        list1.append(data1[i])
        list2.append(data2[i])
    with open('models_propensity.csv', mode='w',  newline='') as att_file:
        file_writer = csv.writer(att_file, delimiter=',')
        file_writer.writerow(list1)
        file_writer.writerow(list2)

    with open('ATT_results.csv', mode='w',  newline='') as att_file:
        file_writer = csv.writer(att_file, delimiter=',')
        file_writer.writerow(['type', 'data1', 'data2'])
        file_writer.writerow([1, ATT_IPW1, ATT_IPW2])
        file_writer.writerow([2, ATT_S_Learner1, ATT_S_Learner2])
        file_writer.writerow([3, ATT_T_Learner1, ATT_T_Learner2])
        file_writer.writerow([4, ATT_Matching1, ATT_Matching2])
        file_writer.writerow([5, ATT_Chosen1, ATT_Chosen2])

    print()
