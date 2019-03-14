import requests
import lxml.html as lh
import numpy as np
import math


PARAMETERS = {
    "Year_Range": 1,
    "Visualize": False,
    "countries": []
}



# WC_years = ['1982', '1986', '1990', '1994', '1998', '2002', '2006', '2010', '2014']
WC_years = [1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014]
WC_hosts = ["Spain", "Mexico", "Italy", "United States of America", "France", "Japan",
            "Germany", "South Africa", "Brazil"]
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

WC_participants_by_year = {
    1982: ("Poland", "Italy", "Cameroon", "Peru", "Belgium", "Argentina", "Hungary", "El Salvador", "England", "France", "Czechoslovakia", "Kuwait", "Brazil", "Soviet Union", "Scotland", "New Zealand", "NorthernIreland", "Spain", "Yugoslavia", "Honduras", "West Germany", "Austria" , "Algeria", "Chile"),
    1986: ("Argentina", "Italy", "Bulgaria", "South Korea", "Mexico", "Paraguay", "Belgium", "Iraq", "Brazil", "Spain" , "Northern Ireland", "Algeria", "Morocco", "England", "Poland", "Portugal", "Denmark", "West Germany", "Uruguay", "Scotland", "Soviet Union", "France", "Hungary", "Canada"),
    1990: ("Italy" , "Czechoslovakia" , "Austria", "United States of America", "Cameroon", "Romania", "Argentina", "Soviet Union", "Brazil", "Costa Rica", "Scotland" , "Sweden", "West Germany", "Yugoslavia", "Colombia", "United Arab Emirates", "Spain", "Belgium", "Uruguay", "South Korea", "England", "Ireland", "Netherlands", "Egypt"),
    1994: ("Romania", "Switzerland", "United States of America", "Colombia", "Brazil" , "Sweden" , "Russia" , "Cameroon", "Germany", "Spain", "South Korea", "Bolivia", "Nigeria", "Bulgaria" , "Argentina", "Greece", "Mexico", "Ireland", "Italy", "Norway", "Netherlands", "Saudi Arabia" , "Belgium", "Morocco"),
    1998: ("Brazil", "Norway", "Morocco", "Scotland", "Italy", "Chile" , "Austria", "Cameroon", "France" , "Denmark" , "South Africa", "Saudi Arabia", "Nigeria", "Paraguay", "Spain", "Bulgaria", "Netherlands", "Mexico", "Belgium", "South Korea", "Germany", "Yugoslavia", "Iran", "United States of America", "Romania", "England" , "Colombia", "Tunisia", "Argentina", "Croatia", "Jamaica", "Japan"),
    2002: ("Denmark", "Senegal", "Uruguay", "France", "Spain", "Paraguay" , "South Africa" , "Slovenia", "Brazil" , "Turkey" , "Costa Rica", "China", "South Korea", "United States of America", "Portugal", "Poland", "Germany", "Ireland", "Cameroon", "Saudi Arabia", "Sweden", "England", "Argentina", "Nigeria", "Mexico", "Italy", "Croatia", "Ecuador", "Japan", "Belgium", "Russia", "Tunisia"),
    2006: ("Germany", "Ecuador", "Poland", "Costa Rica", "England", "Sweden", "Paraguay", "Trinidad and Tobago", "Argentina", "Netherlands", "Ivory Coast" , "Serbia and Montenegro", "Portugal", "Mexico", "Angola", "Iran", "Italy", "Ghana", "Czech Republic", "United States of America", "Brazil", "Australia", "Croatia", "Japan", "Switzerland", "France", "South Korea", "Togo", "Spain", "Ukraine", "Tunisia", "Saudi Arabia"),
    2010: ("South Africa", "Mexico", "Uruguay", "France", "Argentina" , "Nigeria" , "South Korea", "Greece", "England", "United States of America", "Algeria", "Slovenia", "Germany", "Australia", "Serbia", "Ghana", "Netherlands", "Denmark", "Japan", "Cameroon", "Italy", "Paraguay", "New Zealand", "Slovakia", "Brazil", "NorthKorea", "Ivory Coast", "Portugal", "Spain", "Switzerland", "Honduras", "Chile"),
    2014: ("Brazil" , "Croatia", "Mexico" , "Cameroon", "Spain", "Netherlands", "Chile", "Australia", "Colombia", "Greece", "Ivory Coast", "Japan", "Uruguay", "Costa Rica", "England", "Italy", "Switzerland", "Ecuador", "France", "Honduras", "Argentina", "Bosnia-Herzegovina", "Iran", "Nigeria", "Germany", "Portugal", "Ghana", "United States of America", "Belgium", "Algeria", "Russia", "South Korea")
}

WC_winners = {
    1982: ['Italy'],
    1986: ['Argentina'],
    1990: ['Germany'],
    1994: ['Brazil'],
    1998: ['France'],
    2002: ['Brazil'],
    2006: ['Italy'],
    2010: ['Spain'],
    2014: ['Germany']
}

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


"""get all countries that participated in WC"""
WC_participants = get_participants_from_web()
