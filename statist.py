# -*- coding: utf-8 -*-

#******************************************************************************
#
# Statist
# ---------------------------------------------------------
# Provides basic statistics information on any (numeric or string) field
# of vector layer.
#
# Copyright (C) 2009 - 2012 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

#import statistdialog
from __init__ import version
import statistdialog
import statist_utils as utils

import resources_rc

class StatistPlugin:
  def __init__( self, iface ):
    self.iface = iface

    try:
      self.QgisVersion = unicode( QGis.QGIS_VERSION_INT )
    except:
      self.QgisVersion = unicode( QGis.qgisVersion )[ 0 ]

    # For i18n support
    userPluginPath = QFileInfo( QgsApplication.qgisUserDbFilePath() ).path() + "/python/plugins/statist"
    systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/statist"

    overrideLocale = QSettings().value( "locale/overrideFlag", QVariant( False ) ).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value( "locale/userLocale", QVariant( "" ) ).toString()

    if QFileInfo( userPluginPath ).exists():
      translationPath = userPluginPath + "/i18n/statist_" + localeFullName + ".qm"
    else:
      translationPath = systemPluginPath + "/i18n/statist_" + localeFullName + ".qm"

    self.localePath = translationPath
    if QFileInfo( self.localePath ).exists():
      self.translator = QTranslator()
      self.translator.load( self.localePath )
      QCoreApplication.installTranslator( self.translator )

  def initGui( self ):
    if int( self.QgisVersion ) < 10800:
      qgisVersion = str( self.QgisVersion[ 0 ] ) + "." + str( self.QgisVersion[ 2 ] ) + "." + str( self.QgisVersion[ 3 ] )
      QMessageBox.warning( self.iface.mainWindow(),
                           QCoreApplication.translate( "Statist", "Statist: Error" ),
                           QCoreApplication.translate( "Statist", "Quantum GIS %1 detected.\n" ).arg( qgisVersion ) +
                           QCoreApplication.translate( "Statist", "This version of Statist requires at least QGIS version 1.8.0\nPlugin will not be enabled." ) )
      return None

    self.actionRun = QAction( QCoreApplication.translate( "Statist", "Statist" ), self.iface.mainWindow() )
    self.iface.registerMainWindowAction( self.actionRun, "Shift+S" )
    self.actionRun.setIcon( QIcon( ":/icons/statist.png" ) )
    self.actionRun.setWhatsThis( "Calculate statistics for field" )
    self.actionAbout = QAction( QCoreApplication.translate( "Statist", "About Statist..." ), self.iface.mainWindow() )
    self.actionAbout.setIcon( QIcon( ":/icons/about.png" ) )
    self.actionAbout.setWhatsThis( "About Statist" )

    if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.addPluginToVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionRun )
      self.iface.addPluginToVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionAbout )
      self.iface.addVectorToolBarIcon( self.actionRun )
    else:
      self.iface.addPluginToMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionRun )
      self.iface.addPluginToMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionAbout )
      self.iface.addToolBarIcon( self.actionRun )

    self.actionRun.triggered.connect( self.run )
    self.actionAbout.triggered.connect( self.about )

  def unload( self ):
    self.iface.unregisterMainWindowAction( self.actionRun )

    if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.removeVectorToolBarIcon( self.actionRun )
      self.iface.removePluginVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionRun )
      self.iface.removePluginVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionAbout )
    else:
      self.iface.removeToolBarIcon( self.actionRun )
      self.iface.removePluginMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionRun )
      self.iface.removePluginMenu( QCoreApplication.translate( "Statist", "Statist" ), self.actionAbout )

  def run( self ):
    layersCount = len( utils.getVectorLayerNames() )
    if layersCount == 0:
      QMessageBox.warning( self.iface.mainWindow(),
                           QCoreApplication.translate( "Statist", "Statist: Error" ),
                           QCoreApplication.translate( "Statist", "Plugin will not run, because there is\nno vector layers in this project" ) )
      return None

    d = statistdialog.StatistDialog( self.iface )
    d.show()
    d.exec_()

  def about( self ):
    dlgAbout = QDialog()
    dlgAbout.setWindowTitle( QApplication.translate( "Statist", "About Statist" ) )
    lines = QVBoxLayout( dlgAbout )
    title = QLabel( QApplication.translate( "Statist", "<b>Statist</b>" ) )
    title.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
    lines.addWidget( title )
    ver = QLabel( QApplication.translate( "Statist", "Version: %1" ).arg( version() ) )
    ver.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
    lines.addWidget( ver )
    lines.addWidget( QLabel( QApplication.translate( "Statist", "Provides basic statistics information on\nany (numeric or string) field of vector\nlayer." ) ) )
    lines.addWidget( QLabel( QApplication.translate( "Statist", "<b>Developers:</b>" ) ) )
    lines.addWidget( QLabel( "  Alexander Bruy" ) )
    lines.addWidget( QLabel( QApplication.translate( "Statist", "<b>Homepage:</b>") ) )

    overrideLocale = QSettings().value( "locale/overrideFlag", QVariant( False ) ).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value( "locale/userLocale", QVariant( "" ) ).toString()

    localeShortName = localeFullName[ 0:2 ]
    if localeShortName in [ "ru", "uk" ]:
      link = QLabel( "<a href=\"http://gis-lab.info/qa/statist.html\">http://gis-lab.info/qa/statist.html</a>" )
    else:
      link = QLabel( "<a href=\"http://gis-lab.info/qa/statist-eng.html\">http://gis-lab.info/qa/statist-eng.html</a>" )

    link.setOpenExternalLinks( True )
    lines.addWidget( link )

    btnClose = QPushButton( QApplication.translate( "Statist", "Close" ) )
    lines.addWidget( btnClose )
    btnClose.clicked.connect( dlgAbout.close )

    dlgAbout.exec_()
