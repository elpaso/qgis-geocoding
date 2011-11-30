"""
***************************************************************************
Name			 	 : Geocoding
Description          : Geocoding and reverse Geocoding using Google
Date                 : 28/May/09 
copyright            : (C) 2009 by ItOpen
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


def pointToWGS84(point):
    p = QgsProject.instance()
    (proj4string,ok) = p.readEntry("SpatialRefSys","ProjectCRSProj4String")
    if not ok:
        return point
    t=QgsCoordinateReferenceSystem()
    t.createFromEpsg(4326)
    f=QgsCoordinateReferenceSystem()
    f.createFromProj4(proj4string)
    transformer = QgsCoordinateTransform(f,t)
    pt = transformer.transform(point)
    return pt

def pointFromWGS84(point):
    p = QgsProject.instance()
    (proj4string,ok) = p.readEntry("SpatialRefSys","ProjectCRSProj4String")
    if not ok:
        return point
    f=QgsCoordinateReferenceSystem()
    f.createFromEpsg(4326)
    t=QgsCoordinateReferenceSystem()
    t.createFromProj4(proj4string)
    transformer = QgsCoordinateTransform(f,t)
    pt = transformer.transform(point)
    return pt



