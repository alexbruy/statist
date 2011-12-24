# -*- coding: utf-8 -*-

#*****************************************************************************************************************
# Statist
# --------------------------------------------------
# A python plugin for QGIS. Provides basic statistics information
# on any (numeric or string) field of vector layer. Works fine
# with selected objects and whole layer.
#
# Based on partially rewritten 'Basic statistics' from fTools,
# (C) 2009 Carson Farmer.
#
#  Copyright (C) 2009 Alexander Bruy (alexander.bruy@gmail.com)
#
#  This source is free software; you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This code is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  A copy of the GNU General Public License is available on the World Wide Web
#  at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
#  to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
#  MA 02111-1307, USA.
#
#*****************************************************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import os.path, sys

import doStatist, doAbout, utils

import resources

class statistPlugin:
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

    # static messages
    self.wrongVersion = QCoreApplication.translate( "Statist", "Quantum GIS version detected: " +
    self.QgisVersion + "\n" + "Statist plugin requires version at least 1.0.0!\n" +
      "Plugin not loaded." )

    self.msgError = QCoreApplication.translate( "Statist", "Couldn't import Python module 'matplotlib' for plotting. Without it you won't be able to run Statist." )

    self.aboutString = QCoreApplication.translate( "Statist", "Statist\nQuantum GIS Python plugin\n" +
      "The plugin calculate statistics on selected field of vector layer\n\n" +
      "Author: Alexander Bruy\n" + "Mail: alexander.bruy@gmail.com" )

    self.noLayers = QCoreApplication.translate( "Statist", "Plugin will not run, because there is\n" +
      "no vector layers in this project" )

  def initGui( self ):
    # check Qgis version
    if int( self.QgisVersion ) < 1:
      QMessageBox.warning( self.iface.mainWindow(), "Statist: Error", self.wrongVersion )
      return None

    # create plugin menu
    self.calcStats = QAction( QCoreApplication.translate( "mnuStatist", "Statistics" ), self.iface.mainWindow() )
    self.calcStats.setIcon( QIcon( ":/icons/statist.png" ) )
    self.calcStats.setWhatsThis( "Calculate statistics" )
    self.aboutStatist = QAction( QCoreApplication.translate( "mnuStatist", "About..." ), self.iface.mainWindow() )
    self.aboutStatist.setIcon( QIcon( ":/icons/information.png" ) )
    self.aboutStatist.setWhatsThis( "About Statist plugin" )
    
    if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.addPluginToVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.calcStats )
      self.iface.addPluginToVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.aboutStatist )
      self.iface.addVectorToolBarIcon( self.calcStats )
    else:
      self.iface.addPluginToMenu( QCoreApplication.translate( "Statist", "Statist" ), self.calcStats )
      self.iface.addPluginToMenu( QCoreApplication.translate( "Statist", "Statist" ), self.aboutStatist )
      self.iface.addToolBarIcon( self.calcStats )

    QObject.connect( self.calcStats, SIGNAL( "triggered()" ), self.doCalcStats )
    QObject.connect( self.aboutStatist, SIGNAL( "triggered()" ), self.showAbout )

  def unload( self ):
    if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.removeVectorToolBarIcon( self.calcStats )
      self.iface.removePluginVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.calcStats )
      self.iface.removePluginVectorMenu( QCoreApplication.translate( "Statist", "Statist" ), self.aboutStatist )
    else:
      self.iface.removeToolBarIcon( self.calcStats )
      self.iface.removePluginMenu( QCoreApplication.translate( "Statist", "Statist" ), self.calcStats )
      self.iface.removePluginMenu( QCoreApplication.translate( "Statist", "Statist" ), self.aboutStatist )

  def showAbout( self ):
    #QMessageBox.information( self.iface.mainWindow(), self.tr( "About Statist" ), self.aboutString )
    d = doAbout.dlgAbout( self.iface )
    d.exec_()

  def doCalcStats( self ):
    try:
      from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
      from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
      from matplotlib.figure import Figure
      import matplotlib.font_manager as FontManager
    except ImportError:
      QMessageBox.warning( None, "Statist: Error", msgError )
      return None

    nLayers = len( utils.getLayersNames( "vector" ) )
    if nLayers == 0:
      QMessageBox.warning( self.iface.mainWindow(), "Statist: Error", self.noLayers )
      return None
    d = doStatist.dlgStatist( self.iface )
    d.exec_()
