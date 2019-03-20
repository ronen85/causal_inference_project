from collections import defaultdict
from matplotlib.pylab import plt
from matplotlib import pyplot as mp
from utilities import *


def bar_graph(category, age_grp, sex, x, y, year=None, country=None):

    plt.figure()
    plt.ylabel('ATE = Y1 - Y0')
    plt.xlabel('Years')
    plt.bar(range(len(x)), x, align='center')
    plt.xticks(range(len(x)), y, rotation='vertical')

    if country:
        plt.title("%s Suicide Rates for WC; %s ages %s" % (country, sex, age_grp))
        name = country + sex + age_grp + '.png'
        # plt.show()
        plt.tight_layout()
        plt.savefig('./graphs/Countries' + '/' + sex + '/' + name.replace(' ', '_'))

    elif year:
        plt.title("Change in Suicide Rates per Country in %s; %s ages %s" % (year, sex, age_grp))
        name = category + sex + str(year) + age_grp + '.png'
        # plt.show()
        plt.tight_layout()
        plt.savefig('./graphs/' + category + '/' + sex + '/' + str(year) + '/' + name.replace(' ', ''))
    else:
        plt.title("Change in Suicide Rates in %s Countries; %s ages %s" % (category, sex, age_grp))
        name = category + sex + age_grp + '.png'
        # plt.show()
        plt.tight_layout()
        plt.savefig('./graphs/' + category + '/' + sex + '/' + name.replace(' ',''))
