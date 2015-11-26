# -*- coding: utf-8 -*-

"""
***************************************************************************
    statist_utils.py
    ---------------------
    Date                 : June 2009
    Copyright            : (C) 2009-2015 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'June 2009'
__copyright__ = '(C) 2009-2015, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import locale

from qgis.core import QgsMapLayerRegistry, QgsMapLayer, QgsFeatureRequest


def getVectorLayerNames():
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    layerNames = []
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer:
            layerNames.append(unicode(layer.name()))
    return sorted(layerNames, cmp=locale.strcoll)


def getVectorLayerByName(layerName):
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer and layer.name() == layerName:
            if layer.isValid():
                return layer
            else:
                return None


def getFieldNames(layer, fieldTypes):
    fields = layer.pendingFields()
    fieldNames = []
    for field in fields:
        if field.type() in fieldTypes and not field.name() in fieldNames:
            fieldNames.append(unicode(field.name()))
    return sorted(fieldNames, cmp=locale.strcoll)


def getFieldType(layer, fieldName):
    fields = layer.pendingFields()
    for field in fields:
        if field.name() == fieldName:
            return field.typeName()


def getUniqueValuesCount(layer, fieldIndex, useSelection):
    count = 0
    values = []
    if useSelection:
        for f in layer.selectedFeatures():
            if f[fieldIndex] not in values:
                values.append(f[fieldIndex])
                count += 1
    else:
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
        for f in layer.getFeatures(request):
            if f[fieldIndex] not in values:
                values.append(f[fieldIndex])
                count += 1
    return count
