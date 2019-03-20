

def clean_nan(df):
    df.dropna(subset=['population', 'suicides_no'], inplace=True)
    return


def clean_zeros(df):
    # (df.country == 'Albania') & (df.year == 1987)
    cons = df.country.unique()
    years = df.year.unique()
    for cont in cons:
        for yeart in years:
            if df.loc[(df.country == cont) & (df.year == yeart)].suicides_no.sum() == 0:
                index_t = df.loc[(df.country == cont) & (df.year == yeart)].index
                df.drop(index_t, inplace=True)
                # print('The data from year %s in country %s was removed.'%(yeart, cont))
    return


