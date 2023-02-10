from concept.country import Countries,Country
import csv
import os,codecs
from datetime import datetime
#file = open('./util/OPEC_country.csv')

# file = open('./util/JODI_country_code.csv')
file = codecs.open('./util/CountryList.csv', encoding = 'utf-8')
allCountry = csv.reader(file)

countryList = [(i[0],i[1],i[2]) for i in allCountry]
file.close()

allCountry = Countries(countryList)