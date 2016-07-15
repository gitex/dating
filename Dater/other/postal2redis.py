#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This script needs files from http://download.geonames.org/export/zip/.
# Create new folder, add files in the folder and variable PATH_ZIPCODES use.
#

import glob
from zipfile import ZipFile
import re
import redis
from tzwhere import tzwhere

PATH_GEONAMES = 'C:\Users\Eugene\Flask\plansq\data\geonames'
START_NAME = 'postal'

r = redis.StrictRedis('localhost', 6379, 0)


def timezones2redis():
    """
    Function will convert timeZones.txt to redis
    """
    timezone_data = {}
    with file(PATH_GEONAMES + '\\timeZones.txt') as f:
        for zone_list in map(lambda x: x.split('\t'), f.readlines()):
            zone = map(lambda x: x.strip(), zone_list)
            timezone_data[zone[1]] = zone[-1]
    r.hmset('timezones', timezone_data)


def countryInfo2redis():
    countries_in_base = list(r.lrange('countries', 0, -1))

    with file(PATH_GEONAMES + '\\countryInfo.txt') as f:
        countryInfo_strings = filter(lambda x: not x.startswith('#'), f.readlines())
        countryInfo_lists = map(lambda x: x.split('\t')[:-1], countryInfo_strings)
        for country in countryInfo_lists:
            data = {
                'ISO': country[0],
                'ISO3': country[1],
                'ISO-Numeric': country[2],
                'Country': country[4],
                'Capital': country[5],
                'Population': country[7],
                'Languages': country[15]
            }
            if data['ISO'] not in countries_in_base:
                r.lpush('countries', data['ISO'])
            r.hmset('country:' + data['ISO'], data)


def postal2redis():
    timezones2redis()

    all_zip = r.lrange(START_NAME + ':all', 0, -1)
    tz = tzwhere.tzwhere()

    for file_zip in glob.glob(PATH_GEONAMES + '\zipcodes\*.zip'):
        zipfile = ZipFile(file_zip, 'r')
        for file_txt in zipfile.namelist():
            if 'readme' not in file_txt:
                zipcodes_data = zipfile.read(file_txt).split('\n')

                for line in zipcodes_data:
                    city_data = line.split('\t')

                    data = dict(
                        country_code=city_data[0].upper(),
                        postal_code=re.sub('[\s]+', '', city_data[1]),
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

                    data['timezoneName'] = tz.tzNameAt(float(data['latitude']), float(data['longitude']))
                    data['timezoneTime'] = r.hget('timezones', data['timezoneName'])

                    if 'CEDEX' not in data['postal_code']:
                        country_and_postal = '{0}:{1}'.format(data['country_code'].lower(), data['postal_code'])
                        if country_and_postal not in all_zip:
                            all_zip.append(country_and_postal)
                        r.lpush(START_NAME + ':all', country_and_postal)
                        r.lpush(START_NAME + ':{0}:all'.format(data['country_code']), data['postal_code'])
                        r.hmset(START_NAME + ':' + country_and_postal, data)
                        print country_and_postal


if __name__ == '__main__':
    postal2redis()
