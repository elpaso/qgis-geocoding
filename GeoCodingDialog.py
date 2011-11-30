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
from PyQt4 import QtCore, QtGui 
from Ui_GeoCoding import Ui_GeoCoding
# create the dialog for GeoCoding
class GeoCodingDialog(QtGui.QDialog, Ui_GeoCoding ):
  def __init__(self): 
    QtGui.QDialog.__init__(self) 
    # Set up the user interface from Designer. 
    # #self.ui = Ui_GeoCoding ()
    # #self.ui.setupUi(self)
    self.setupUi(self)
