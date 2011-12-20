# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Geocoding
Description          : Geocoding and reverse Geocoding using Google
Date                 : 28/May/09
copyright            : (C) 2009-2010 by ItOpen
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import sys, os

# Make sure geopy is imported from current path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from GeoCodingDialog import GeoCodingDialog
from ConfigDialog import ConfigDialog
from PlaceSelectionDialog import PlaceSelectionDialog
from Utils import *

class GeoCoding:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # store layer id
        self.layerid = ''

    def initGui(self):
        # Create action that will start plugin
        self.action = QAction(QIcon(":/plugins/GeoCoding/geocode_icon.png"), \
        "&GeoCode", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("activated()"), self.geocode)

        # Add toolbar button and menu item

        self.reverseAction=QAction(QIcon(":/plugins/GeoCoding/reverse_icon.png"), QCoreApplication.translate('GeoCoding', "&Reverse GeoCode"), self.iface.mainWindow())
        self.configAction=QAction(QIcon(":/plugins/GeoCoding/settings_icon.png"), QCoreApplication.translate('GeoCoding', "&Settings"), self.iface.mainWindow())
        self.aboutAction=QAction(QIcon(":/plugins/GeoCoding/about_icon.png"), QCoreApplication.translate('GeoCoding', "&About"), self.iface.mainWindow())
        QObject.connect(self.configAction, SIGNAL("activated()"), self.config)
        QObject.connect(self.reverseAction, SIGNAL("activated()"), self.reverse)
        QObject.connect(self.aboutAction, SIGNAL("activated()"), self.about)


        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("GeoCode", self.action)
        self.iface.addPluginToMenu("GeoCode", self.reverseAction)
        self.iface.addPluginToMenu("GeoCode", self.configAction)
        self.iface.addPluginToMenu("GeoCode", self.aboutAction)


        # read config
        self.config = QSettings('ItOpen', 'GeoCoding');


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("GeoCode",self.action)
        self.iface.removeToolBarIcon(self.action)

    # change settings
    def config(self):
        # create and show the dialog
        dlg = ConfigDialog(self)
        geocoders = {
                'Nominatim (Openstreetmap)' : 'Nominatim',
                'Google' : 'Google',
            }
        # Get current index
        try:
            index = geocoders.values().index(self.get_config('GeocoderClass').toString())
        except ValueError:
            index = 1
        dlg.geocoderComboBox.addItems(geocoders.keys())
        dlg.geocoderComboBox.setCurrentIndex(index)
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # save settings
            self.set_config('GoogleAPIKey', dlg.GoogleAPIKey.text())
            self.set_config('GeocoderClass', geocoders[str(dlg.geocoderComboBox.currentText())])
            self.set_config('ZoomScale',  dlg.ZoomScale.text())
            self.store_config()

    def about(self):
        infoString = QString(QCoreApplication.translate('GeoCoding', "Python GeoCoding Plugin<br />This plugin provides GeoCoding functions using webservices.<br />Author: Dr. Alessandro Pasotti (aka: elpaso)<br />Mail: <a href=\"mailto:info@itopen.it\">info@itopen.it</a><br />Web: <a href=\"http://www.itopen.it\">www.itopen.it</a>\n"))
        QMessageBox.information(self.iface.mainWindow(), "About GeoCoding",infoString)

    # return a config parameter
    def get_config(self,  key):
        return self.config.value(key);


   # set a config parameter
    def set_config(self,  key,  value):
        return self.config.setValue(key,  QVariant(value));

    #read config from file
    def read_config(self):
        if not self.config.isWritable():
            infoString = unicode(QCoreApplication.translate('GeoCoding', "<strong>GeoCoding plugin</strong> cannot read config file (%s).<br />Please check your settings and file permissions.")) %  unicode(self.config.fileName())
            QMessageBox.information(self.iface.mainWindow(), "GeoCoding configuration",infoString)


    # save to a file the config array
    def store_config(self):
        if not self.config.isWritable():
            infoString = unicode(QCoreApplication.translate('GeoCoding', "<strong>GeoCoding plugin</strong> cannot write config file (%s).<br />Please check your settings and file permissions.")) %  unicode(self.config.fileName())
            QMessageBox.information(self.iface.mainWindow(), "GeoCoding configuration",infoString)
            return
        self.config.sync ()
        qDebug('geocoding config written on ' + self.config.fileName())


    # Reverse geocoding
    def reverse(self):
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), chk)
            return
        sb = self.iface.mainWindow().statusBar()
        sb.showMessage(QCoreApplication.translate('GeoCoding', "Click on the map to obtain the address"))
        ct = ClickTool(self.iface,  self.reverse_action);
        self.iface.mapCanvas().setMapTool(ct)


   # change settings
    def reverse_action(self, point):
        try:
            geocoder = self.get_geocoder_instance()
        except ImportError, e:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), QCoreApplication.translate('GeoCoding', "Couldn't import Python module 'geopy' for communication with geocoders. Without it you won't be able to run GeoCoding plugin. You can install 'geopy' with the following command: 'sudo easy_install geopy'.<br />If you want to access reverse geocoding services, you will need the experimental version, more info at <a href=\"http://code.google.com/p/geopy/wiki/ReverseGeocoding\">ReverseGeocoding</a><br />Message: %1").arg(e))
            return

        if 'reverse' not in dir(geocoder) :
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), QCoreApplication.translate('GeoCoding', "This Python module 'geopy' version does not support reverse geocoding. You should install the experimental version, more info at <a href=\"http://code.google.com/p/geopy/wiki/ReverseGeocoding\">ReverseGeocoding</a>"))
            return

        try:
            # reverse lat/lon
            pt = pointToWGS84(point)
            address = geocoder.reverse((pt[1],pt[0]));
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse GeoCoding"),  unicode(QCoreApplication.translate('GeoCoding', "Reverse geocoding found the following address:<br /><strong>%s</strong>")) %  unicode(address[0]))
            # save point
            self.save_point(point, unicode(address[0]))
        except (IndexError,  ValueError),  e:
             QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse GeoCoding error"), unicode(QCoreApplication.translate('GeoCoding', "<strong>No location found.</strong><br />Please check your CRS, you have clicked on<br />(Lat Lon) %(lat)f %(lon)f<br />Server response: %(error_message)s")) % {'lat' :  pt[1], 'lon' : pt[0], 'error_message' : e})
        return


    # run geocoding
    def geocode(self):
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(),QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), chk)
            return

        #Import geopy
        try:
            geocoder = self.get_geocoder_instance()
        except ImportError, e:
            sys.path
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), QCoreApplication.translate('GeoCoding', "Couldn't import Python module 'geopy' for communication with geocoders. Without it you won't be able to run GeoCoding plugin. You can install 'geopy' with the following command: 'sudo easy_install geopy'.<br />If you want to access reverse geocoding services, you will need the experimental version, more info at <a href=\"http://code.google.com/p/geopy/wiki/ReverseGeocoding\">ReverseGeocoding</a><br />Message: %1").arg(e))
            return
        # create and show the dialog
        dlg = GeoCodingDialog()
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1 :
            try:
                result = geocoder.geocode(unicode(dlg.address.text()).encode('utf-8'), exactly_one=False)
            except Exception, e:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), QCoreApplication.translate('GeoCoding', "There was an error with the geocoding service:<br /><strong>%1</strong>").arg(unicode(e)))
                return

            places = {}
            for place, point in result:
                places[place] = point

            if len(places) == 1:
                self.process_point(place, point)
            else:
                all_str = QCoreApplication.translate('GeoCoding', 'All')
                place_dlg = PlaceSelectionDialog()
                place_dlg.placesComboBox.addItem(all_str)
                place_dlg.placesComboBox.addItems(places.keys())
                place_dlg.show()
                result = place_dlg.exec_()
                if result == 1 :
                    if place_dlg.placesComboBox.currentText() == all_str:
                        for place in places:
                            self.process_point(place, places[place])
                    else:
                        point = places[str(place_dlg.placesComboBox.currentText())]
                        self.process_point(str(place_dlg.placesComboBox.currentText()), point)
            return


    def get_geocoder_instance(self):
        """
        Loads a concrete Geocoder class
        """
        from geopy import geocoders

        geocoder_class = str(self.get_config('GeocoderClass').toString())

        if not geocoder_class:
            geocoder_class  ='Nominatim'
        geocoder = getattr(geocoders, geocoder_class)
        if 'Google' == geocoder_class:
            return geocoder(api_key=self.get_config('GoogleAPIKey').toString())
        return geocoder()


    def process_point(self, place, point):
        """
        Transforms the point and save
        """
        # lon lat and transform
        point = QgsPoint(point[1], point[0])
        point = pointFromWGS84(point)
        x = point[0]
        y = point[1]
        # stupid qvariant return a tuple
        scale = float(self.get_config('ZoomScale').toInt()[0])
        if not scale:
            scale = float(self.canvas.scale())

        # Create a rectangle to cover the new extent
        rect = QgsRectangle(  \
                        x - scale \
                        , y - scale \
                        , x + scale \
                        , y + scale)
        # Set the extent to our new rectangle
        self.canvas.setExtent(rect)
        # Refresh the map
        self.canvas.refresh()
        # save point
        #self.save_point(point, unicode(dlg.address.text()))
        self.save_point(point, unicode(place))


    # save point to file, point is in project's crs
    def save_point(self, point, address):
        qDebug('Saving point ' + str(point[1])  + ' ' + str(point[0]))
        # create and add the point layer if not exists or not set
        if not QgsMapLayerRegistry.instance().mapLayer(self.layerid) :
            # create layer with same CRS as map canvas
            self.layer = QgsVectorLayer("Point", "GeoCoding Plugin Results", "memory")
            self.provider = self.layer.dataProvider()
            self.layer.setCrs(self.canvas.mapRenderer().destinationCrs())

            # add fields
            self.provider.addAttributes( [QgsField("address", QVariant.String)] )

            # Labels on
            label = self.layer.label()
            label.setLabelField(QgsLabel.Text, 0)
            self.layer.enableLabels(True)

            # add layer if not already
            QgsMapLayerRegistry.instance().addMapLayer(self.layer)

            # store layer id
            self.layerid = QgsMapLayerRegistry.instance().mapLayers().keys()[-1]


        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPoint(point))
        fet.setAttributeMap( { 0 : QVariant(address) } )
        self.provider.addFeatures( [ fet ] )

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.layer.updateExtents()

        self.canvas.refresh()


    # check config and project settings before geocoding,
    # return an error string
    def check_settings (self) :
        p = QgsProject.instance()
        error = ''

        if 'Google' == self.get_config('GeocoderClass').toString() and not len(self.get_config('GoogleAPIKey').toString()) :
            error += unicode(QCoreApplication.translate('GeoCoding', "Google API Key is not set, please check plugin settings."))

        try:
            import simplejson
        except ImportError, e:
            error += QCoreApplication.translate('GeoCoding', "'simplejson' module is required. Please install simplejson with 'easy_install simplejson' or 'pip install simplejson'")

        return error


if __name__ == "__main__":
    pass

