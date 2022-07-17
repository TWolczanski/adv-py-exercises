import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, datetime

# how I got the coronavirus data:
# 1. I went to https://ourworldindata.org/covid-cases and from the download section I downloaded a 40 mb csv file containing data for all countries
# 2. I used grep to retrieve the data for Poland:
#    grep "Poland" owid-covid-data.csv > covid.csv

covid = pd.read_csv("covid.csv", encoding="ascii", usecols=["date", "new_cases"])
# I convert dates from strings to objects so I can compare them using >= and <=
covid["date"] = covid["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").date())
covid1 = covid.loc[(covid["date"] >= date(2021, 2, 1)) & (covid["date"] <= date(2021, 4, 30))]
covid2 = covid.loc[(covid["date"] >= date(2021, 6, 1)) & (covid["date"] <= date(2021, 8, 31))]

# how I got the meteorological data:
# 1. I went to https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/dobowe/synop/2021/ and downloaded the .zip files for February, March, April, June, July and August
# 2. I extracted the .csv files and merged them:
#    for file in s_d_t_*.csv
#        cat $file >> meteo.csv
#    end

# months and days in meteo.csv are written with preceding zeroes so I have to convert them to int manually
def convert(s):
    if s[0] == "0":
        s = s[1]
    return int(s)

names = ["location", "year", "month", "day", "temperature"]
# the average day temperature is the 10th value in each row of meteo.csv
meteo = pd.read_csv("meteo.csv", encoding="iso8859-2", header=None, names=names, usecols=[1, 2, 3, 4, 9], converters={"month": convert, "day": convert})
# add a new column storing dates
# axis=1 means that the apply function will iterate through rows instead of columns
meteo["date"] = meteo.apply(lambda row: date(row["year"], row["month"], row["day"]), axis=1)

meteo1 = meteo.loc[(meteo["date"] >= date(2021, 2, 1)) & (meteo["date"] <= date(2021, 4, 30))]
meteo2 = meteo.loc[(meteo["date"] >= date(2021, 6, 1)) & (meteo["date"] <= date(2021, 8, 31))]

meteo1_wroclaw = meteo1.loc[meteo1["location"] == "WROCŁAW-STRACHOWICE"]
meteo2_wroclaw = meteo2.loc[meteo2["location"] == "WROCŁAW-STRACHOWICE"]

fig = plt.figure()

# this is what the plot was supposed to look like (if I understand the exercise correctly)...

# ax1 = fig.add_subplot(2, 1, 1)
# covid1.plot(x="date", y="new_cases", ax=ax1)
# meteo1_wroclaw.plot(x="date", y="temperature", ax=ax1)

# ax2 = fig.add_subplot(2, 1, 2)
# covid2.plot(x="date", y="new_cases", ax=ax2)
# meteo2_wroclaw.plot(x="date", y="temperature", ax=ax2)

# ...but this is what makes much more sense to me

ax1 = fig.add_subplot(2, 2, 1)
ax1.set_ylim([0, 37000])
ax1.set_title("COVID-19 cases - cold season")

ax2 = fig.add_subplot(2, 2, 2)
ax2.set_ylim([0, 37000])
ax2.set_title("COVID-19 cases - warm season")

ax3 = fig.add_subplot(2, 2, 3)
ax3.set_ylim([-10, 30])
ax3.set_title("Average temperature - cold season")

ax4 = fig.add_subplot(2, 2, 4)
ax4.set_ylim([-10, 30])
ax4.set_title("Average temperature - warm season")

covid1.plot(x="date", y="new_cases", ax=ax1)
meteo1_wroclaw.plot(x="date", y="temperature", ax=ax3, color=["red"])
covid2.plot(x="date", y="new_cases", ax=ax2)
meteo2_wroclaw.plot(x="date", y="temperature", ax=ax4, color=["red"])

plt.show()