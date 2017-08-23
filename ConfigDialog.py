"""
***************************************************************************
Name			 	 : Geocoding
Description          : Geocoding and reverse Geocoding using Google
Date                 : 2/May/13
copyright            : (C) 2013 by ItOpen
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
import os

# Import the PyQt and QGIS libraries
try:
    from qgis.core import Qgis
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5 import uic
    QT_VERSION=5
    os.environ['QT_API'] = 'pyqt5'
except:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4 import uic
    QT_VERSION=4


# create the dialog for Config
class ConfigDialog(QDialog ):

    def __init__(self, caller):
        super(ConfigDialog, self ).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Ui_Config.ui'), self)

        # stupid qvariant return a tuple...
        zoom_scale = caller.get_config('ZoomScale', 0)
        # Use pdb for debugging
        #import pdb
        ## These lines allow you to set a breakpoint in the app
        #pyqtRemoveInputHook()
        #pdb.set_trace()

        self.ZoomScale.setValue(int(zoom_scale))


