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

import locale
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from ui_statistdialogbase import Ui_StatistDialog
import statist_utils as utils

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.font_manager as FontManager

class StatistDialog( QDialog, Ui_StatistDialog ):
  def __init__( self, iface ):
    QDialog.__init__( self )
    self.iface = iface
    self.setupUi( self )

    # add matplotlib figure to dialog
    self.figure = Figure()
    self.axes = self.figure.add_subplot( 111 )
    self.figure.suptitle( self.tr( "Frequency distribution" ) )
    self.canvas = FigureCanvas( self.figure )
    self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot )
    lstActions = self.mpltoolbar.actions()
    self.mpltoolbar.removeAction( lstActions[ 7 ] )
    self.layoutPlot.addWidget( self.canvas )
    self.layoutPlot.addWidget( self.mpltoolbar )

    QObject.connect( self.cmbLayers, SIGNAL( "currentIndexChanged( QString )" ), self.reloadFields )
    QObject.connect( self.chkUseTextFields, SIGNAL( "stateChanged( int )" ), self.reloadFields )

    self.groupBox.hide()
    QObject.connect( self.chkShowGrid, SIGNAL( "stateChanged( int )" ), self.refreshPlot )
    QObject.connect( self.chkAsPlot, SIGNAL( "stateChanged( int )" ), self.refreshPlot )
    QObject.connect( self.btnRefresh, SIGNAL( "clicked()" ), self.refreshPlot )

    self.manageGui()

  def manageGui( self ):
    self.cmbLayers.clear()
    self.cmbLayers.addItems( utils.getVectorLayerNames() )

  def reloadFields( self ):
    self.cmbFields.clear()

    #~ self.lstStatistics.clearContents()
    #~ self.lstStatistics.setRowCount( 0 )
#~
    #~ self.axes.clear()
#~
    #~ self.groupBox.hide()
#~
    #~ self.spnMinX.setValue( 0.0 )
    #~ self.spnMaxX.setValue( 0.0 )
#~
    #~ self.chkShowGrid.blockSignals( True )
    #~ self.chkAsPlot.blockSignals( True )
#~
    #~ self.chkShowGrid.setCheckState( Qt.Unchecked )
    #~ self.chkAsPlot.setCheckState( Qt.Unchecked )
#~
    #~ self.chkShowGrid.blockSignals( False )
    #~ self.chkAsPlot.blockSignals( False )

    layer = utils.getVectorLayerByName( unicode( self.cmbLayers.currentText() ) )
    if layer.selectedFeatureCount() != 0:
      self.chkUseSelected.setCheckState( Qt.Checked )
    else:
      self.chkUseSelected.setCheckState( Qt.Unchecked )

    fields = vLayer.dataProvider().fields()
    fieldNames = []
    if self.chkUseTextFields.checkState():
      for i in fields:
        if fields[ i ].type() == QVariant.String:
          fieldNames.append( unicode( fields[ i ].name() ) )
    else:
      for i in fields:
        if fields[ i ].type() in [ QVariant.Int, QVariant.Double ]:
          fieldNames.append( unicode( fields[ i ].name() ) )

    self.cmbFields.addItems( sorted( fieldNames, cmp=locale.strcoll ) )
    self.cmbFields.setCurrentIndex( -1 )

  def refreshPlot( self ):
    pass

  #~ def startCalculation( self ):
    #~ QObject.disconnect( self.chkGrid, SIGNAL( "stateChanged(int)" ), self.refreshPlot )
    #~ QObject.disconnect( self.chkPlot, SIGNAL( "stateChanged(int)" ), self.refreshPlot )
    #~ self.edMinX.setValue( 0.0 )
    #~ self.edMaxX.setValue( 0.0 )
    #~ self.chkGrid.setCheckState( Qt.Unchecked )
    #~ self.chkPlot.setCheckState( Qt.Unchecked )
    #~ self.axes.clear()
    #~ QObject.connect( self.chkGrid, SIGNAL( "stateChanged(int)" ), self.refreshPlot )
    #~ QObject.connect( self.chkPlot, SIGNAL( "stateChanged(int)" ), self.refreshPlot )
#~
    #~ if self.cmbLayers.currentText() == "":
      #~ QMessageBox.information( self, "Statist: Error", self.tr( "Please specify target vector layer first" ) )
    #~ elif self.cmbFields.currentText() == "":
      #~ QMessageBox.information( self, "Statist: Error", self.tr( "Please specify target field first" ) )
    #~ else:
      #~ vlayer = utils.getVectorLayerByName( self.cmbLayers.currentText() )
      #~ self.calculate( self.cmbLayers.currentText(), self.cmbFields.currentText() )
#~
  #~ def calculate( self, layerName, fieldName ):
    #~ vLayer = utils.getVectorLayerByName( layerName )
    #~ self.tblStatistics.clearContents()
    #~ self.tblStatistics.setRowCount( 0 )
    #~ self.threadCalc = workThread( self.iface.mainWindow(), self, vLayer, fieldName, self.chkUseSelected.checkState() )
    #~ QObject.connect( self.threadCalc, SIGNAL( "runFinished(PyQt_PyObject)" ), self.runFinishedFromThread )
    #~ QObject.connect( self.threadCalc, SIGNAL( "runStatus(PyQt_PyObject)" ), self.runStatusFromThread )
    #~ QObject.connect( self.threadCalc, SIGNAL( "runRange(PyQt_PyObject)" ), self.runRangeFromThread )
#~
    #~ QObject.disconnect( self.btnStop, SIGNAL( "clicked()" ), self.toClipboard )
    #~ self.btnStop.setText( self.tr( "Cancel" ) )
    #~ QObject.connect( self.btnStop, SIGNAL("clicked()" ), self.cancelThread )
    #~ self.btnStop.setEnabled( True )
#~
    #~ self.threadCalc.start()
    #~ return True
#~
  #~ def toClipboard( self ):
    #~ txt = ""
    #~ for i in range( len( self.results ) ):
      #~ txt += self.results[ i ] + "\n"
    #~ clipboard = QApplication.clipboard()
    #~ clipboard.setText( txt )
#~
  #~ def refreshPlot( self ):
    #~ self.axes.clear()
    #~ self.axes.grid( self.chkGrid.isChecked() )
    #~ if self.edMinX.value() == self.edMaxX.value():
      #~ # histogram
      #~ if not self.chkPlot.isChecked():
        #~ self.axes.hist( self.valuesX, 18, alpha=0.5, histtype = "bar" )
      #~ # plot
      #~ else:
        #~ n, bins, pathes = self.axes.hist( self.valuesX, 18, alpha=0.5, histtype = "bar" )
        #~ self.axes.clear()
        #~ self.axes.grid( self.chkGrid.isChecked() )
        #~ c = []
        #~ for i in range( len( bins ) - 1 ):
          #~ s = bins[ i + 1 ] - bins[ i ]
          #~ c.append( bins[ i ] + (s / 2 ) )
#~
        #~ self.axes.plot( c, n, "ro-" )
    #~ else:
      #~ xRange = []
      #~ if self.edMinX.value() > self.edMaxX.value():
        #~ xRange.append( self.edMaxX.value() )
        #~ xRange.append( self.edMinX.value() )
      #~ else:
        #~ xRange.append( self.edMinX.value() )
        #~ xRange.append( self.edMaxX.value() )
      #~ # histogram
      #~ if not self.chkPlot.isChecked():
        #~ self.axes.hist( self.valuesX, 18, xRange, alpha=0.5, histtype = "bar" )
      #~ # plot
      #~ else:
        #~ n, bins, pathes = self.axes.hist( self.valuesX, 18, xRange, alpha=0.5, histtype = "bar" )
        #~ self.axes.clear()
        #~ self.axes.grid( self.chkGrid.isChecked() )
        #~ c = []
        #~ for i in range( len( bins ) - 1 ):
          #~ s = bins[ i + 1 ] - bins[ i ]
          #~ c.append( bins[ i ] + (s / 2 ) )
#~
        #~ self.axes.plot( c, n, "ro-" )
        #~ self.axes.set_xlim( xRange[ 0 ], xRange[ 1 ] )
    #~ self.axes.set_ylabel( self.tr( "Count" ), fontproperties = self.fp )
    #~ field = unicode( self.cmbFields.currentText() )
    #~ self.axes.set_xlabel( field, fontproperties = self.fp )
    #~ self.figure.autofmt_xdate()
    #~ self.canvas.draw()
#~
  #~ def cancelThread( self ):
    #~ self.threadCalc.stop()
#~
  #~ def runFinishedFromThread( self, output ):
    #~ self.threadCalc.stop()
    #~ self.results = output[ 0 ]
#~
    #~ n = len( self.results )
    #~ self.tblStatistics.setRowCount( n )
    #~ for r in range( n ):
      #~ tmp = self.results[ r ].split( ":" )
      #~ item = QTableWidgetItem( tmp[ 0 ] )
      #~ self.tblStatistics.setItem( r, 0, item )
      #~ item = QTableWidgetItem( tmp[ 1 ] )
      #~ self.tblStatistics.setItem( r, 1, item )
    #~ self.tblStatistics.verticalHeader().hide()
#~
    #~ # enable copy to clipboard
    #~ QObject.disconnect( self.btnStop, SIGNAL( "clicked()" ), self.cancelThread )
    #~ self.btnStop.setText( self.tr ( "Copy" ) )
    #~ QObject.connect( self.btnStop, SIGNAL( "clicked()" ), self.toClipboard )
#~
    #~ self.axes.clear()
    #~ self.axes.grid( self.chkGrid.isChecked() )
    #~ self.axes.set_ylabel( self.tr( "Count" ), fontproperties = self.fp )
    #~ field = unicode( self.cmbFields.currentText() )
    #~ self.axes.set_xlabel( field, fontproperties = self.fp )
    #~ self.valuesX = output[ 2 ]
    #~ self.axes.hist( self.valuesX, 18, alpha=0.5, histtype = "bar" )
    #~ self.figure.autofmt_xdate()
    #~ self.canvas.draw()
#~
    #~ self.groupBox.show()
    #~ return True
#~
  #~ def runStatusFromThread( self, status ):
    #~ self.progressBar.setValue( status )
#~
  #~ def runRangeFromThread( self, range_vals ):
    #~ self.progressBar.setRange( range_vals[ 0 ], range_vals[ 1 ] )
#~
#~ class workThread( QThread ):
  #~ def __init__( self, parentThread, parentObject, vlayer, fieldName, useSelection ):
    #~ QThread.__init__( self, parentThread )
    #~ self.parent = parentObject
    #~ self.running = False
    #~ self.vlayer = vlayer
    #~ self.fieldName = fieldName
    #~ self.useSelection = useSelection
#~
  #~ def run( self ):
    #~ self.running = True
    #~ ( lst, cnt, val ) = self.statistics( self.vlayer, self.fieldName )
    #~ self.emit( SIGNAL( "runFinished(PyQt_PyObject)" ), ( lst, cnt, val ) )
    #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0 )
#~
  #~ def stop( self ):
    #~ self.running = False
#~
  #~ def statistics( self, vlayer, fieldName ):
    #~ vprovider = vlayer.dataProvider()
    #~ allAttrs = vprovider.attributeIndexes()
    #~ vprovider.select( allAttrs )
    #~ fields = vprovider.fields()
    #~ index = vprovider.fieldNameIndex( fieldName )
    #~ feat = QgsFeature()
    #~ nVal = 0
    #~ values = []
    #~ first = True
    #~ nElement = 0
    #~ meanVal = 0
    #~ sumVal = 0
    #~ if utils.getFieldType( vlayer, fieldName ) in ( 'String', 'varchar', 'char', 'text' ):
      #~ fillVal = 0
      #~ emptyVal = 0
      #~ #if vlayer.selectedFeatureCount() != 0:
      #~ if self.useSelection:
        #~ selFeat = vlayer.selectedFeatures()
        #~ nFeat = vlayer.selectedFeatureCount()
        #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0 )
        #~ self.emit( SIGNAL( "runRange(PyQt_PyObject)" ), ( 0, nFeat ) )
        #~ for f in selFeat:
          #~ atMap = f.attributeMap()
          #~ lenVal = float( len( atMap[ index ].toString() ) )
          #~ if first:
            #~ minVal = lenVal
            #~ maxVal = lenVal
            #~ first = False
          #~ else:
            #~ if lenVal < minVal: minVal = lenVal
            #~ if lenVal > maxVal: maxVal = lenVal
          #~ if lenVal != 0.00:
            #~ fillVal += 1
          #~ else:
            #~ emptyVal += 1
          #~ values.append( lenVal )
          #~ sumVal = sumVal + lenVal
          #~ nElement += 1
          #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
      #~ else:
        #~ nFeat = vprovider.featureCount()
        #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0 )
        #~ self.emit( SIGNAL( "runRange(PyQt_PyObject)" ), ( 0, nFeat ) )
        #~ while vprovider.nextFeature( feat ):
          #~ atMap = feat.attributeMap()
          #~ lenVal = float( len( atMap[ index ].toString() ) )
          #~ if first:
            #~ minVal = lenVal
            #~ maxVal = lenVal
            #~ first = False
          #~ else:
            #~ if lenVal < minVal: minVal = lenVal
            #~ if lenVal > maxVal: maxVal = lenVal
          #~ if lenVal != 0.00:
            #~ fillVal += 1
          #~ else:
            #~ emptyVal += 1
          #~ values.append( lenVal )
          #~ sumVal = sumVal + lenVal
          #~ nElement += 1
          #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
      #~ nVal= len( values )
      #~ if nVal > 0.00:
        #~ meanVal = sumVal / nVal
      #~ lstStats = []
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Count:" ) + unicode( nVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Minimum length:" ) + unicode( minVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Maximum length:" ) + unicode( maxVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Mean lengtn:" ) + unicode( meanVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Filled:" ) + unicode( fillVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Empty:" ) + unicode( emptyVal ) )
      #~ return ( lstStats, [], values )
    #~ else:
      #~ stdVal = 0
      #~ cvVal = 0
      #~ rVal = 0
      #~ medianVal = 0
      #~ uniqueVal = 0
      #~ maxVal = 0.00
      #~ minVal = 0.00
      #~ # selection
      #~ #if vlayer.selectedFeatureCount() != 0:
      #~ if self.useSelection:
        #~ selFeat = vlayer.selectedFeatures()
        #~ uniqueVal = utils.getUniqueValsCount( vlayer, index, True )
        #~ nFeat = vlayer.selectedFeatureCount()
        #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0 )
        #~ self.emit( SIGNAL( "runRange(PyQt_PyObject)" ), ( 0, nFeat ) )
        #~ for f in selFeat:
          #~ atMap = f.attributeMap()
          #~ value = float( atMap[ index ].toDouble() [ 0 ] )
          #~ if first:
            #~ minVal = value
            #~ maxVal = value
            #~ first = False
          #~ else:
            #~ if value < minVal: minVal = value
            #~ if value > maxVal: maxVal = value
          #~ values.append( value )
          #~ sumVal = sumVal + value
          #~ nElement += 1
          #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
      #~ else: # whole layer
        #~ uniqueVal = utils.getUniqueValsCount( vlayer, index, False )
        #~ nFeat = vprovider.featureCount()
        #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0 )
        #~ self.emit( SIGNAL( "runRange(PyQt_PyObject)" ), ( 0, nFeat ) )
        #~ vprovider.select( allAttrs )
        #~ while vprovider.nextFeature( feat ):
          #~ atMap = feat.attributeMap()
          #~ value = float( atMap[ index ].toDouble() [ 0 ] )
          #~ if first:
            #~ minVal = value
            #~ maxVal = value
            #~ first = False
          #~ else:
            #~ if value < minVal: minVal = value
            #~ if value > maxVal: maxVal = value
          #~ values.append( value )
          #~ sumVal = sumVal + value
          #~ nElement += 1
          #~ self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
      #~ nVal= len( values )
      #~ rVal = maxVal - minVal
      #~ if nVal > 1:
        #~ lstVal = values
        #~ lstVal.sort()
        #~ if ( nVal % 2 ) == 0:
          #~ medianVal = 0.5 * ( lstVal[ ( nVal - 1 )/ 2 ] + lstVal[ ( nVal ) / 2 ] )
        #~ else:
          #~ medianVal = lstVal[ ( nVal + 1 ) / 2  - 1 ]
      #~ if nVal > 0.00:
        #~ meanVal = sumVal / nVal
        #~ if meanVal != 0.00:
          #~ for val in values:
            #~ stdVal += ( ( val - meanVal ) * ( val - meanVal ) )
          #~ stdVal = math.sqrt( stdVal / nVal )
          #~ cvVal = stdVal / meanVal
      #~ lstStats = []
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Count:" ) + unicode( nVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Unique values:" ) + unicode( uniqueVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Minimum value:" ) + unicode( minVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Maximum value:" ) + unicode( maxVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Swing:" ) + unicode( rVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Sum:" ) + unicode( sumVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Mean value:" ) + unicode( meanVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Median value:" ) + unicode( medianVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Standard deviation:" ) + unicode( stdVal ) )
      #~ lstStats.append( QCoreApplication.translate( "statResult", "Coefficient of Variation:" ) + unicode( cvVal ))
      #~ return ( lstStats, [], values )
