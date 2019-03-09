

def clean_nan(df):
    df.dropna(subset=['population', 'suicides_no'], inplace=True)
    return


def cat2num():
    return


def check_years(df, year, country):
    """check if the database holds the required info"""
    if not df[(df.year == int(year)) & (df.country == country)].__len__():
        return False
    if not sum(df[(df.year == int(year)) & (df.country == country)].population):
        return False
    if not sum(df[(df.year == int(year)) & (df.country == country)].suicides_no):
        return False

    count = 0
    for i in range(-2, 3):
        if df[(df.year == int(year) + i) & (df.country == country)].__len__():
            count += 1
    if count >= 4:
        return True
