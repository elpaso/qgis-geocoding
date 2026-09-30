# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Geocoding
Description          : Geocoding and reverse Geocoding using Web Services
Date                 : 23/02/2018
copyright            : (C) 2009-2018 by ItOpen
email                : info@itopen.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys, os, json
from qgis.core import QgsSettings, QgsMessageLog, QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

def logMessage(msg):
    if QgsSettings().value('PythonPlugins/GeoCoding/writeDebug'):
        QgsMessageLog.logMessage(msg, 'GeoCoding')


class GeoCodeException(Exception):
    pass


class BaseGeocoder():

    def get(self, url):
        request = QgsBlockingNetworkRequest()
        logMessage("Calling URL: {}".format(url))
        req = QNetworkRequest( QUrl(url) )
        errCode = request.get( req )
        data = request.reply().content().data()
        if errCode == QgsBlockingNetworkRequest.NoError:
            logMessage("Response: {}".format(data))
            return data
        else:
            raise GeoCodeException("Network error calling URL {}: {}".format(url, errCode))


class OsmGeoCoder(BaseGeocoder):

    url = 'https://nominatim.openstreetmap.org/search?format=json&q={address}'
    reverse_url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}'


    def geocode(self, address):
        try:
            url = self.url.format(**{'address': address})
            results = json.loads(self.get(url))
            return [(rec['display_name'], (rec['lon'], rec['lat'])) for rec in results]
        except Exception as e:
            raise GeoCodeException(str(e))

    def reverse(self, lon, lat):
        """single result"""
        try:
            url = self.reverse_url.format(**{'lon': lon, 'lat': lat})
            rec = json.loads(self.get(url))
            return [(rec['display_name'], (rec['lon'], rec['lat']))]
        except Exception as e:
            raise GeoCodeException(str(e))

class GoogleGeoCoder(BaseGeocoder):

    url = 'https://maps.googleapis.com/maps/api/geocode/json?address={address}'
    reverse_url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}'

    def __init__(self, api_key=None):
        self.api_key = api_key

    def geocode(self, address):

        if self.api_key is not None and self.api_key.replace(' ', '') != '':
            url = self.url + '&key=' + self.api_key
        else:
            url = self.url

        try:
            url = url.format(**{'address': address})
            results = json.loads(self.get(url))
            if "error_message" in results:
                raise GeoCodeException(results["error_message"])
            else:
                results = results['results']
            return [(rec['formatted_address'], (rec['geometry']['location']['lng'], rec['geometry']['location']['lat'])) for rec in results]
        except Exception as e:
            raise GeoCodeException(str(e))

    def reverse(self, lon, lat):
        if self.api_key is not None:
            url = self.reverse_url + '&key=' + self.api_key
        else:
            url = self.reverse_url
        try:
            url = url.format(**{'lon': lon, 'lat': lat})
            results = json.loads(self.get(url))
            if "error_message" in results:
                raise GeoCodeException(results["error_message"])
            return [(rec['formatted_address'], (rec['geometry']['location']['lng'], rec['geometry']['location']['lat'])) for rec in results]
        except Exception as e:
            raise GeoCodeException(str(e))


