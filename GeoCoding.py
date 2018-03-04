# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Geocoding
Description          : Geocoding and reverse Geocoding using Web Services
Date                 : 25/Jun/2013
copyright            : (C) 2009-2017 by ItOpen
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
import sys, os


# Import the PyQt and QGIS libraries
try:
    from qgis.core import Qgis, QgsMessageLog
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5 import uic
    QT_VERSION=5
    os.environ['QT_API'] = 'pyqt5'
    from urllib.request import URLError
except:
    from PyQt4.QtCore import *
    from PyQt4.QtCore import QSettings as QgsSettings
    from PyQt4.QtGui import *
    from PyQt4 import uic
    QT_VERSION=4
    from urllib2 import URLError

# Import the code for the dialog
from .GeoCodingDialog import GeoCodingDialog
from .ConfigDialog import ConfigDialog
from .PlaceSelectionDialog import PlaceSelectionDialog
from .Utils import *

from .geocoders import *



class GeoCoding:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # store layer id
        self.layerid = ''
        self.layer = None
        

    def logMessage(self, msg):
        if self.get_config('writeDebug'):
            QgsMessageLog.logMessage(msg, 'GeoCoding')

    def initGui(self):
        # Create action that will start plugin
        current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.action = QAction(QIcon(os.path.join(current_directory, "geocode_icon.png")), \
        "&GeoCoding", self.iface.mainWindow())
        # connect the action to the run method
        if QT_VERSION == 4:
            self.action.triggered.connect(self.geocode)
        else:
            self.action.triggered.connect(self.geocode)

        # Add toolbar button and menu item
        self.reverseAction=QAction(QIcon(os.path.join(current_directory, "reverse_icon.png")), QCoreApplication.translate('GeoCoding', "&Reverse GeoCoding"), self.iface.mainWindow())
        self.configAction=QAction(QIcon(os.path.join(current_directory, "settings_icon.png")), QCoreApplication.translate('GeoCoding', "&Settings"), self.iface.mainWindow())
        self.aboutAction=QAction(QIcon(os.path.join(current_directory, "about_icon.png")), QCoreApplication.translate('GeoCoding', "&About"), self.iface.mainWindow())
        if QT_VERSION == 4:
            self.configAction.triggered.connect(self.config)
            self.reverseAction.triggered.connect(self.reverse)
            self.aboutAction.triggered.connect(self.about)
        else:
            self.configAction.triggered.connect(self.config)
            self.reverseAction.triggered.connect(self.reverse)
            self.aboutAction.triggered.connect(self.about)

        self.menu = QMenu(QCoreApplication.translate('GeoCoding', "GeoCoding"))
        self.menu.setIcon(QIcon(os.path.join(current_directory, "geocode_icon.png")))
        self.menu.addActions([self.action, self.reverseAction, self.configAction, self.aboutAction])
        self.iface.pluginMenu().addMenu( self.menu )
        self.iface.addToolBarIcon(self.action)
        # read config
        self.config = QgsSettings()
        self.previous_map_tool = self.iface.mapCanvas().mapTool()


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("GeoCoding", self.action)
        self.iface.removePluginMenu("GeoCoding", self.reverseAction)
        self.iface.removePluginMenu("GeoCoding", self.configAction)
        self.iface.removePluginMenu("GeoCoding", self.aboutAction)
        self.iface.removeToolBarIcon(self.action)
        if self.previous_map_tool:
            self.iface.mapCanvas().setMapTool(self.previous_map_tool)

    def config(self):
        # create and show the dialog
        dlg = ConfigDialog(self)
        geocoders = {
                'Nominatim (Openstreetmap)' : 'Nominatim',
                'Google' : 'GoogleV3',
            }
        # Get current index
        try:
            index = list(geocoders.values()).index(self.get_config('GeocoderClass', 'Nominatim'))
        except (ValueError, AttributeError):
            index = 1
        dlg.geocoderComboBox.addItems(geocoders.keys())
        dlg.geocoderComboBox.setCurrentIndex(index)
        # show the dialog
        dlg.show()
        dlg.adjustSize()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # save settings
            self.set_config('GeocoderClass', geocoders[str(dlg.geocoderComboBox.currentText())])
            self.set_config('ZoomScale',  dlg.ZoomScale.text())
            self.set_config('writeDebug',  dlg.debugCheckBox.isChecked())
            self.set_config('googleKey',  dlg.googleKey.text())

    def about(self):
        infoString = QCoreApplication.translate('GeoCoding', "Python GeoCoding Plugin<br>This plugin provides GeoCoding functions using webservices.<br>Author:  Alessandro Pasotti (aka: elpaso)<br>Mail: <a href=\"mailto:info@itopen.it\">info@itopen.it</a><br>Web: <a href=\"http://www.itopen.it\">www.itopen.it</a><br>" + "<b>Do yo like this plugin? Please consider <a href=\"https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TJHLD5DY4LAFQ\">donating</a></b>.")
        QMessageBox.information(self.iface.mainWindow(), "About GeoCoding", infoString)

    def get_config(self,  key, default=''):
        # return a config parameter
        return self.config.value('PythonPlugins/GeoCoding/' + key, default )


    def set_config(self,  key,  value):
        # set a config parameter
        return self.config.setValue('PythonPlugins/GeoCoding/' + key, value)

    def reverse(self):
        # Reverse geocoding
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), chk)
            return
        sb = self.iface.mainWindow().statusBar()
        sb.showMessage(QCoreApplication.translate('GeoCoding', "Click on the map to obtain the address"))
        ct = ClickTool(self.iface,  self.reverse_action);
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(ct)


   # change settings
    def reverse_action(self, point):
        """
        Performs the reverse action calling
        reverse method

        TODO: clear the map tool on error
        (still haven't find how to do it)
        """
        
        geocoder = self.get_geocoder_instance()

        try:
            # reverse lat/lon
            self.logMessage('Reverse clicked point ' + str(point[0]) + ' ' + str(point[1]))
            pt = pointToWGS84(point, self._get_canvas_crs())
            self.logMessage('Reverse transformed point ' + str(pt[0]) + ' ' + str(pt[1]))
            address = geocoder.reverse(pt[0],pt[1])
            self.logMessage(str(address))
            if len(address) == 0:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse GeoCoding error"), unicode(QCoreApplication.translate('GeoCoding', "<strong>Empty result</strong>.<br>")))
            else:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse GeoCoding"),  unicode(QCoreApplication.translate('GeoCoding', "Reverse geocoding found the following address:<br><strong>%s</strong>")) %  address[0][0])
                # save point
                self.save_point(point, address[0][0])
        except Exception as e:
            QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse GeoCoding error"), unicode(QCoreApplication.translate('GeoCoding', "<strong>Unhandled exception</strong>.<br>%s" % e)))
        return


    def geocode(self):
        # run geocoding
        if self.previous_map_tool:
            self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        chk = self.check_settings()
        if len(chk) :
            QMessageBox.information(self.iface.mainWindow(),QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), chk)
            return

        geocoder = self.get_geocoder_instance()
        
        # create and show the dialog
        dlg = GeoCodingDialog()
        # show the dialog
        dlg.adjustSize()
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1 :
            try:
                result = geocoder.geocode(unicode(dlg.address.text()).encode('utf-8'))
            except Exception as e:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "GeoCoding plugin error"), QCoreApplication.translate('GeoCoding', "There was an error with the geocoding service:<br><strong>%s</strong>" % e))
                return

            if not result:
                QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Not found"), QCoreApplication.translate('GeoCoding', "The geocoder service returned no data for the searched address: <strong>%s</strong>." % dlg.address.text()))
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
                        point = places[unicode(place_dlg.placesComboBox.currentText())]
                        self.process_point(place_dlg.placesComboBox.currentText(), point)
            return


    def get_geocoder_instance(self):
        """
        Loads a concrete Geocoder class
        """

        geocoder_class = str(self.get_config('GeocoderClass'))

        if not geocoder_class:
            geocoder_class ='Nominatim'

        if geocoder_class == 'Nominatim':
            return OsmGeoCoder()
        else:
            return GoogleGeoCoder(self.get_config('googleKey'))



    def process_point(self, place, point):
        """
        Transforms the point and save
        """
        # lon lat and transform
        point = QgsPoint(float(point[0]), float(point[1]))
        point = pointFromWGS84(point, self._get_layer_crs())
        
        # Set the extent to our new point
        self.canvas.setCenter(point)

        scale = float(self.get_config('ZoomScale', 0))
        # adjust scale to display correct scale in qgis
        if scale:
            self.canvas.zoomScale(scale)

        # Refresh the map
        self.canvas.refresh()
        # save point
        self.save_point(point, unicode(place))

    def _get_layer_crs(self):
        """get CRS from destination layer or from canvas if the layer does not exist"""
        try:
            return self.layer.crs()
        except:
            return self._get_canvas_crs()


    def _get_canvas_crs(self):
        """compat"""
        try:
            return self.iface.mapCanvas().mapRenderer().destinationCrs()
        except:
            return self.iface.mapCanvas().mapSettings().destinationCrs()

    def _get_registry(self):
        """compat"""
        try:
            return QgsMapLayerRegistry.instance()
        except:
            return QgsProject.instance()

    # save point to file, point is in project's crs
    def save_point(self, point, address):
        self.logMessage('Saving point ' + str(point[0])  + ' ' + str(point[1]))
        # create and add the point layer if not exists or not set
        if not self._get_registry().mapLayer(self.layerid) :
            # create layer with same CRS as map canvas
            crs = self._get_canvas_crs()
            self.layer = QgsVectorLayer("Point?crs=" + crs.authid(), "GeoCoding Plugin Results", "memory")
            self.provider = self.layer.dataProvider()

            # add fields
            self.provider.addAttributes([QgsField("address", QVariant.String)])

            # BUG: need to explicitly call it, should be automatic!
            self.layer.updateFields()

            # Labels on
            try:
                label_settings = QgsPalLayerSettings()
                label_settings.fieldName = "address"
                self.layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
                self.layer.setLabelsEnabled(True)
            except:
                self.layer.setCustomProperty("labeling", "pal")
                self.layer.setCustomProperty("labeling/enabled", "true")
                #self.layer.setCustomProperty("labeling/fontFamily", "Arial")
                #self.layer.setCustomProperty("labeling/fontSize", "10")
                self.layer.setCustomProperty("labeling/fieldName", "address")
                self.layer.setCustomProperty("labeling/placement", "2")

            # add layer if not already
            self._get_registry().addMapLayer(self.layer)

            # store layer id
            self.layerid = self.layer.id()


        # add a feature
        try:
            fields=self.layer.pendingFields()
        except:
            fields=self.layer.fields()

        fet = QgsFeature(fields)
        try:
            fet.setGeometry(QgsGeometry.fromPoint(point))
        except:
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))

        try: # QGIS < 1.9
            fet.setAttributeMap({0 : address})
        except: # QGIS >= 1.9
            fet['address'] = address

        self.layer.startEditing()
        self.layer.addFeatures([ fet ])
        self.layer.commitChanges()


    # check config and project settings before geocoding,
    # return an error string
    def check_settings (self):
        p = QgsProject.instance()
        error = ''
        if QT_VERSION==4:
            if not self.iface.mapCanvas().hasCrsTransformEnabled() and self.iface.mapCanvas().mapRenderer().destinationCrs().authid() != 'EPSG:4326':
                error = QCoreApplication.translate('GeoCoding', "On-the-fly reprojection must be enabled if the destination CRS is not EPSG:4326. Please enable on-the-fly reprojection.")

        return error


if __name__ == "__main__":
    pass
