#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, glob
from zipfile import ZipFile
import re
from pymongo import MongoClient

PATH_ZIPCODES = 'C:\Users\Eugene\Flask\plansq\data\zipcodes\\'

client = MongoClient('localhost', 27017)
database = client.mydb.geolocation

for file_zip in glob.glob(PATH_ZIPCODES + '*.zip'):
    zipfile = ZipFile(file_zip, 'r')
    for file_txt in zipfile.namelist():
        zipcodes_data = zipfile.read(file_txt).split('\n')

        for line in zipcodes_data:
            city_data = line.split('\t')

            data = dict(
                country_code=city_data[0].upper(),
                postal_code=re.sub('[^\d]+', '', city_data[1]),
                place_name=city_data[2],
                admin_name_1=city_data[3],
                admin_code_1=city_data[4],
                admin_name_2=city_data[5],
                admin_code_2=city_data[6],
                admin_name_3=city_data[7],
                admin_code_3=city_data[8],
                latitude=city_data[9],
                longitude=city_data[10],
                accuracy=city_data[11])

            database.save(data)