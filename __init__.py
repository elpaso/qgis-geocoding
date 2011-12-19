# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name			 	 : Geocoding
Description          : Geocoding and reverse Geocoding using Google
Date                 : 28/May/09
copyright            : (C) 2010 by ItOpen
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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "GeoCoding"

def description():
    return "GeoCoding and reverse GeoCoding using Google web services"

def version():
    return "2.2"

def qgisMinimumVersion():
    return "1.6"

def classFactory(iface):
    # loads GeoCoding class from file GeoCoding
    from GeoCoding import GeoCoding
    return GeoCoding(iface)


def experimental():
    return False

def homepage():
    return 'http://www.itopen.it/2009/06/05/geocoding-qgis-plugins-released/'

def repository():
    return 'https://github.com/elpaso/qgis-geocoding'

def tracker():
    return 'https://github.com/elpaso/qgis-geocoding/issues'

def icon():
    return 'geocode_icon.png'
