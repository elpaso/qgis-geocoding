"""
***************************************************************************
Name			 	 : Geocoding
Description          : Geocoding and reverse Geocoding using Google
Date                 : 28/May/09
copyright            : (C) 2009-2013 by ItOpen
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

from qgis.core import *
from qgis.gui import *

class ClickTool(QgsMapTool):
    def __init__(self,iface, callback):
        QgsMapTool.__init__(self,iface.mapCanvas())
        self.iface      = iface
        self.callback   = callback
        self.canvas     = iface.mapCanvas()
        return None


    def canvasReleaseEvent(self,e):
        point = e.mapPoint()
        self.callback(point)
        return None


def pointToWGS84(point, crs):
    """
    crs is the renderer crs
    """
    t = QgsCoordinateReferenceSystem('EPSG:4326')
    transformer = QgsCoordinateTransform(crs, t, QgsProject.instance())
    return transformer.transform(QgsPointXY(point))

def pointFromWGS84(point, crs):
    f = QgsCoordinateReferenceSystem('EPSG:4326')
    transformer = QgsCoordinateTransform(f, crs, QgsProject.instance())
    return transformer.transform(QgsPointXY(point))



