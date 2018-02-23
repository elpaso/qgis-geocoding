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
        point = self.canvas.getCoordinateTransform().toMapPoint(e.pos().x(),e.pos().y())
        self.callback(point)
        return None


def pointToWGS84(point, crs):
    """
    crs is the renderer crs
    """
    t=QgsCoordinateReferenceSystem()
    t.createFromSrid(4326)
    f=crs #QgsCoordinateReferenceSystem()
    #f.createFromProj4(proj4string)
    try:
        transformer = QgsCoordinateTransform(f,t)
    except:
        transformer = QgsCoordinateTransform(f, t, QgsProject.instance())
    try:
        pt = transformer.transform(point)
    except:
        pt = transformer.transform(QgsPointXY(point)) 
    return pt

def pointFromWGS84(point, crs):
    f=QgsCoordinateReferenceSystem()
    f.createFromSrid(4326)
    t=crs # QgsCoordinateReferenceSystem()
    #t.createFromProj4(proj4string)
    try:
        transformer = QgsCoordinateTransform(f,t)
    except:
        transformer = QgsCoordinateTransform(f, t, QgsProject.instance())
    try:
        pt = transformer.transform(point)
    except:
        pt = transformer.transform(QgsPointXY(point)) 
    return pt



