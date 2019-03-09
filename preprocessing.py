

def clean_nan(df):
    df.dropna(subset=['population', 'suicides_no'], inplace=True)
    return


def cat2num():
    return

