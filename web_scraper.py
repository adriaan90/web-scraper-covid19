import requests
import pandas
import time
import numpy as np
from bs4 import BeautifulSoup
from datetime import date
import tweepy
import schedule
import os
from os import environ
from secrets import *

print('This is a twitter bot')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

def data_interval():
    #Use today's data to determine interval
    URL = 'https://www.worldometers.info/coronavirus/#countries'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Isolate table data showing covid19 data per country
    results = soup.find(id="main_table_countries_today")
    content = results.find_all('td')

    # convert data to a list
    data = []
    for item in content:
        data.append(item.text.strip())
        # print(item.text)

    # Determine interval when new row in table starts
    interval = data.index("USA") - data.index("World")
    print(f"Interval is {interval}")

    return interval

def scrape_table(table_ID):
    #Retrieve website HTML
    URL = 'https://www.worldometers.info/coronavirus/#countries'
    html_of_page = requests.get(URL)
    soup = BeautifulSoup(html_of_page.content, 'html.parser')

    #Isolate table data showing covid19 data per country
    table_container = soup.find(id=table_ID)
    table_content = table_container.find_all('td')

    #convert data to a list
    table_data = []
    for item in table_content:
        table_data.append(item.text.strip())

    #determine interval when new line in table starts
    interval = data_interval()

    #Populate lists for dictionary
    countries = table_data[::interval]
    total_cases = table_data[1::interval]
    new_cases = table_data[2::interval]
    total_deaths = table_data[3::interval]
    new_deaths = table_data[4::interval]

    #Add lists to covid19_table dictionary
    column_names = ["Country", "Total Cases", "New Cases", "Total Deaths", "New Deaths"]
    covid19_table = {
        "columns": column_names,
        "country": countries,
        "total_cases": total_cases,
        "new_cases": new_cases,
        "total_deaths": total_deaths,
        "new_deaths": new_deaths
        }
    return covid19_table

def Growth_factor(growth_today, growth_yesterday):
    #Gf = new cases for today / new cases for yesterday
    # Gf = N_i/N_i-1
    print(growth_today)
    print(growth_yesterday)
    # Check if variables are not empty
    if growth_today:
        if growth_yesterday:
            Gf = round(float(growth_today)/float(growth_yesterday),2)
        else:
            Gf = 0
    else:
        Gf = 0

    return Gf

def dict_index(dict,search_term):
    #returns position of search term in given dictionary
    return dict["country"].index(search_term)

def tweet_input(country_name):
    # Creates dictionary with data for tweet content from scraped data
    table_today = scrape_table("main_table_countries_today")
    table_yesterday = scrape_table("main_table_countries_yesterday")

    index_country_today = dict_index(table_today,country_name)
    index_country_yesterday = dict_index(table_yesterday,country_name)
    index_world_today = dict_index(table_today, "World")
    index_world_yesterday = dict_index(table_yesterday, "World")

    Gf_country = Growth_factor(table_today["new_cases"][index_country_today].replace(',',''),
                               table_yesterday["new_cases"][index_country_yesterday].replace(',',''))
    Gf_world = Growth_factor(table_today["new_cases"][index_world_today].replace(',', ''),
                               table_yesterday["new_cases"][index_world_yesterday].replace(',', ''))
    tweet_data = {
        country_name: {
            "Total_cases": table_today["total_cases"][index_country_today],
            "New_cases": table_today["new_cases"][index_country_today],
            "Total_deaths": table_today["total_deaths"][index_country_today],
            "New_deaths": table_today["new_deaths"][index_country_today],
            "Gf": Gf_country
        },
        "Total": {
            "Total_cases": table_today["total_cases"][index_world_today],
            "New_cases": table_today["new_cases"][index_world_today],
            "Total_deaths": table_today["total_deaths"][index_world_today],
            "New_deaths": table_today["new_deaths"][index_world_today],
            "Gf": Gf_world
        }
    }
    return tweet_data

def tweet_stat(country_name):
    # Creates a .txt file with the content of the tweet
    tweet_data = tweet_input(country_name)
    with open('tweet.txt', 'w', encoding='utf-8') as f:
        f.write(f'#COVID19 stats {str(date.today())}:\n\
           \n{country_name}:\
           \nCases: {str(tweet_data[country_name]["Total_cases"])} ({str(tweet_data[country_name]["New_cases"])})\
           \nDeaths: {str(tweet_data[country_name]["Total_deaths"])} ({str(tweet_data[country_name]["New_deaths"])})\
           \nGrowth factor: {str(tweet_data[country_name]["Gf"])}\n\
           \nWorld:\
           \nCases: {str(tweet_data["Total"]["Total_cases"])} ({str(tweet_data["Total"]["New_cases"])})\
           \nDeaths: {str(tweet_data["Total"]["Total_deaths"])} ({str(tweet_data["Total"]["New_deaths"])})\
           \nGrowth factor: {str(tweet_data["Total"]["Gf"])}')

    with open('tweet.txt', 'r') as f:
        api.update_status(f.read())

tweet_stat("UK")
sleep(15)
tweet_stat("South Africa")
