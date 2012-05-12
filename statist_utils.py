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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

def getVectorLayerNames():
  layerMap = QgsMapLayerRegistry.instance().mapLayers()
  layerNames = []
  for name, layer in layerMap.iteritems():
    if layer.type() == QgsMapLayer.VectorLayer:
      layerNames.append( unicode( layer.name() ) )
  return sorted( layerNames, cmp=locale.strcoll )

def getVectorLayerByName( layerName ):
  layerMap = QgsMapLayerRegistry.instance().mapLayers()
  for name, layer in layerMap.iteritems():
    if layer.type() == QgsMapLayer.VectorLayer and layer.name() == layerName:
      if layer.isValid():
        return layer
      else:
        return None

def getFieldNames( layer, fieldTypes ):
  fieldMap = layer.pendingFields()
  fieldNames = []
  for idx, field in fieldMap.iteritems():
    if field.type() in fieldTypes and not field.name() in fieldNames:
      fieldNames.append( unicode( field.name() ) )
  return sorted( fieldNames, cmp=locale.strcoll )

def getFieldType( layer, fieldName ):
  fields = layer.pendingFields()
  for idx, field in fields.iteritems():
    if field.name() == fieldName:
      return field.typeName()

def getUniqueValuesCount( layer, fieldIndex, useSelection ):
  provider = layer.dataProvider()
  vprovider.select( [ fieldIndex ], QgsRectangle(), False )
  count = 0
  values = []
  if useSelection:
    selection = layer.selectedFeatures()
    for f in selection:
      if f.attributeMap()[ fieldIndex ].toString() not in values:
        values.append( f.attributeMap()[ fieldIndex ].toString() )
        count += 1
  else:
    feat = QgsFeature()
    while vprovider.nextFeature( feat ):
      if feat.attributeMap()[ fieldIndex ].toString() not in values:
        values.append( feat.attributeMap()[ fieldIndex ].toString() )
        count += 1
  return count
