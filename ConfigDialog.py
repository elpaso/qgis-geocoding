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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_Config import Ui_Config
# create the dialog for Config
class ConfigDialog(QDialog, Ui_Config ):
    def __init__(self, caller):
        QDialog.__init__(self)
        ##Set up the user interface from Designer.
        ##self.ui = Ui_Config ()
        ##self.ui.setupUi(self)
        self.setupUi(self)

        # stupid qvariant return a tuple...
        zoom_scale = caller.get_config('ZoomScale', 0)
        # Use pdb for debugging
        #import pdb
        ## These lines allow you to set a breakpoint in the app
        #pyqtRemoveInputHook()
        #pdb.set_trace()

        self.ZoomScale.setValue(int(zoom_scale))


