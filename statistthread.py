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

import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

import statist_utils as utils

class StatistThread( QThread ):
  rangeChanged = pyqtSignal( int )
  updateProgress = pyqtSignal()
  processFinished = pyqtSignal( list )
  processInterrupted = pyqtSignal()

  STRING_TYPES = [ 'String', 'varchar', 'char', 'text' ]

  def __init__( self, layer, fieldName, useSelection ):
    QThread.__init__( self, QThread.currentThread() )
    self.mutex = QMutex()
    self.stopMe = 0

    self.layer = layer
    self.fieldName = fieldName
    self.useSelection = useSelection

  def run( self ):
    if utils.getFieldType( self.layer, self.fieldName ) in self.STRING_TYPES:
      statText, values = self.statisticsForText()
      self.processFinished.emit( [ statText, values ] )
    else:
      statText, values = self.statisticsForNumbers()
      self.processFinished.emit( [ statText, values ] )

  def stop( self ):
    self.mutex.lock()
    self.stopMe = 1
    self.mutex.unlock()

    QThread.wait( self )

  def statisticsForNumbers( self ):
    self.mutex.lock()
    self.stopMe = 0
    self.mutex.unlock()

    interrupted = False

    index = self.layer.fieldNameIndex( self.fieldName )
    self.layer.select( [ index ], QgsRectangle(), False )

    count = 0
    rValue = 0
    cvValue = 0
    minValue = 0
    maxValue = 0
    sumValue = 0
    meanValue = 0
    medianValue = 0
    stdDevValue = 0
    uniqueValue = 0

    isFirst = True
    values = []

    if self.useSelection:
      selection = self.layer.selectedFeatures()
      count = self.layer.selectedFeatureCount()
      self.rangeChanged.emit( count )
      for f in selection:
        value = float( f.attributeMap()[ index ].toDouble()[ 0 ] )

        if isFirst:
          minValue = value
          maxValue = value
          isFirst = False
        else:
          if value < minValue:
            minValue = value
          if value > maxValue:
            maxValue = value

        values.append( value )
        sumValue += value

        self.updateProgress.emit()

        self.mutex.lock()
        s = self.stopMe
        self.mutex.unlock()
        if s == 1:
          interrupted = True
          break
    else:
      count = self.layer.featureCount()
      self.rangeChanged.emit( count )

      ft = QgsFeature()
      while self.layer.nextFeature( ft ):
        value = float( ft.attributeMap()[ index ].toDouble()[ 0 ] )

        if isFirst:
          minValue = value
          maxValue = value
          isFirst = False
        else:
          if value < minValue:
            minValue = value
          if value > maxValue:
            maxValue = value

        values.append( value )
        sumValue += value

        self.updateProgress.emit()

        self.mutex.lock()
        s = self.stopMe
        self.mutex.unlock()
        if s == 1:
          interrupted = True
          break

    # calculate additional values
    rValue = maxValue - minValue
    uniqueValue = utils.getUniqueValuesCount( self.layer, index, self.useSelection )

    if count > 0:
      meanValue = sumValue / count
      if meanValue != 0.00:
        for v in values:
          stdDevValue += ( ( v - meanValue ) * ( v - meanValue ) )
        stdDevValue = math.sqrt( stdDevValue / count )
        cvValue = stdDevValue / meanValue

    if count > 1:
      tmp = values
      tmp.sort()
      # calculate median
      if ( count % 2 ) == 0:
        medianValue = 0.5 * ( tmp[ ( count - 1 ) / 2 ] + tmp[ count / 2 ] )
      else:
        medianValue = tmp[ ( count + 1 ) / 2  - 1 ]

    # generate output
    statsText = []
    statsText.append( self.tr( "Count:%1" ).arg( count ) )
    statsText.append( self.tr( "Unique values:%1").arg( uniqueValue ) )
    statsText.append( self.tr( "Minimum value:%1").arg( minValue ) )
    statsText.append( self.tr( "Maximum value:%1").arg( maxValue ) )
    statsText.append( self.tr( "Range:%1").arg( rValue ) )
    statsText.append( self.tr( "Sum:%1").arg( sumValue ) )
    statsText.append( self.tr( "Mean value:%1").arg( meanValue ) )
    statsText.append( self.tr( "Median value:%1").arg( medianValue ) )
    statsText.append( self.tr( "Standard deviation:%1").arg( stdDevValue ) )
    statsText.append( self.tr( "Coefficient of Variation:%1").arg( cvValue ) )

    return statsText, values

  def statisticsForText( self ):
    self.mutex.lock()
    self.stopMe = 0
    self.mutex.unlock()

    interrupted = False

    index = self.layer.fieldNameIndex( self.fieldName )
    self.layer.select( [ index ], QgsRectangle(), False )


    count = 0
    sumValue = 0
    minValue = 0
    maxValue = 0
    meanValue = 0
    countEmpty = 0
    countFilled = 0

    isFirst = True
    values = []

    if self.useSelection:
      selection = self.layer.selectedFeatures()
      count = self.layer.selectedFeatureCount()
      self.rangeChanged.emit( count )
      for f in selection:
        length = float( len( f.attributeMap()[ index ].toString() ) )

        if isFirst:
          minValue = length
          maxValue = length
          isFirst = False
        else:
          if length < minValue:
            minValue = length
          if length > maxValue:
            maxValue = length

        # calculate empty and non-empty fields
        if length != 0.00:
          countFilled += 1
        else:
          countEmpty += 1

        values.append( length )
        sumValue += length

        self.updateProgress.emit()

        self.mutex.lock()
        s = self.stopMe
        self.mutex.unlock()
        if s == 1:
          interrupted = True
          break
    else:
      count = self.layer.featureCount()
      self.rangeChanged.emit( count )

      ft = QgsFeature()
      while self.layer.nextFeature( ft ):
        length = float( len( ft.attributeMap()[ index ].toString() ) )

        if isFirst:
          minValue = length
          maxValue = length
          isFirst = False
        else:
          if length < minValue:
            minValue = length
          if length > maxValue:
            maxValue = length

        # calculate empty and non-emtpy fields
        if length != 0.00:
          countFilled += 1
        else:
          countEmpty += 1

        values.append( length )
        sumValue += length

        self.updateProgress.emit()

        self.mutex.lock()
        s = self.stopMe
        self.mutex.unlock()
        if s == 1:
          interrupted = True
          break

    # calculate mean length if possible
    n = float( len( values ) )
    if n > 0:
      meanValue = sumValue / n

    # generate output
    statsText = []
    statsText.append( self.tr( "Minimum length:%1").arg( minValue ) )
    statsText.append( self.tr( "Maximum length:%1").arg( maxValue ) )
    statsText.append( self.tr( "Mean length:%1").arg( meanValue ) )
    statsText.append( self.tr( "Filled:%1").arg( countFilled ) )
    statsText.append( self.tr( "Empty:%1").arg( countEmpty ) )
    statsText.append( self.tr( "Total count:%1").arg( count ) )

    return statsText, values
