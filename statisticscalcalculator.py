# -*- coding: utf-8 -*-

"""
***************************************************************************
    statisticscalcalculator.py
    ---------------------
    Date                 : November 2015
    Copyright            : (C) 2015 by Alexander Bruy
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
__date__ = 'November 2015'
__copyright__ = '(C) 2015, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


from qgis.PyQt.QtCore import pyqtSignal, QObject, QVariant

from qgis.core import (QgsFeatureRequest,
                       QgsStatisticalSummary,
                       QgsStringStatisticalSummary,
                       QgsDateTimeStatisticalSummary
                      )

UNKNOWN = -1
NUMERIC = 0
TEXT = 1
DATETIME = 2


class StatisticsCalculator(QObject):
    calculated = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.data = []
        self.values = []

    def setLayer(self, layer):
        self.layer = layer

    def setField(self, field):
        self.fieldName = field

    def setSelectedOnly(self, selectedOnly):
        self.selectedOnly = selectedOnly

    def calculate(self):
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([self.fieldName], self.layer.fields())
        if self.selectedOnly:
            features = self.layer.getSelectedFeatures(request)
        else:
            features = self.layer.getFeatures(request)

        fieldType = self._fieldType()
        if fieldType == NUMERIC:
            self.values, self.data = self._numericStats(features)
        elif fieldType == TEXT:
            self.values, self.data = self._stringStats(features)
        elif fieldType == DATETIME:
            dataType = self.layer.fields().field(self.fieldName).typeName().lower()
            self.values, self.data = self._datetimeStats(features, dataType)
        else:
            #self.error.emit(self.tr("Unrecognized field type."))
            return

        self.calculated.emit()

    def _fieldType(self):
        field = self.layer.fields().field(self.fieldName)
        if field.type() in (QVariant.Double, QVariant.Int, QVariant.LongLong, QVariant.UInt, QVariant.ULongLong):
            return NUMERIC
        elif field.type() == QVariant.String:
            return TEXT
        elif field.type() in (QVariant.Date, QVariant.DateTime, QVariant.Time):
            return DATETIME
        else:
            return UNKNOWN

    def _numericStats(self, features):
        values = []
        stat = QgsStatisticalSummary()
        for f in features:
            stat.addVariant(f[self.fieldName])
            if f[self.fieldName]:
                values.append(f[self.fieldName])
        stat.finalize()

        cv = stat.stDev() / stat.mean() if stat.mean() != 0 else 0

        data = []
        data.append(self.tr("Count:{}".format(stat.count())))
        data.append(self.tr("Unique values:{}".format(stat.variety())))
        data.append(self.tr("Minimum value:{}".format(stat.min())))
        data.append(self.tr("Maximum value:{}".format(stat.max())))
        data.append(self.tr("Range:{}".format(stat.range())))
        data.append(self.tr("Sum:{}".format(stat.sum())))
        data.append(self.tr("Mean value:{}".format(stat.mean())))
        data.append(self.tr("Median value:{}".format(stat.median())))
        data.append(self.tr("Standard deviation:{}".format(stat.stDev())))
        data.append(self.tr("Coefficient of Variation:{}".format(cv)))
        data.append(self.tr("Minority (rarest occurring value):{}".format(stat.minority())))
        data.append(self.tr("Majority (most frequently occurring value):{}".format(stat.majority())))
        data.append(self.tr("First quartile:{}".format(stat.firstQuartile())))
        data.append(self.tr("Third quartile:{}".format(stat.thirdQuartile())))
        data.append(self.tr("Interquartile Range (IQR):{}".format(stat.interQuartileRange())))
        data.append(self.tr("Missing (NULL) values:{}".format(stat.countMissing())))
        return values, data

    def _stringStats(self, features):
        values = []
        stat = QgsStringStatisticalSummary()
        for f in features:
            stat.addValue(f[self.fieldName])
            if f[self.fieldName]:
                values.append(len(f[self.fieldName]))
        stat.finalize()

        data = []
        data.append(self.tr("Count:{}".format(stat.count())))
        data.append(self.tr("Unique values:{}".format(stat.countDistinct())))
        data.append(self.tr("Minimum length:{}".format(stat.minLength())))
        data.append(self.tr("Maximum length:{}".format(stat.maxLength())))
        data.append(self.tr("Mean length:{}".format(stat.meanLength())))
        data.append(self.tr("Filled values:{}".format(stat.count() - stat.countMissing())))
        data.append(self.tr("Missing (NULL) values:{}".format(stat.countMissing())))
        return values, data

    def _datetimeStats(self, features, dataType):
        values = []
        stat = QgsDateTimeStatisticalSummary()
        for f in features:
            stat.addValue(f[self.fieldName])
            if f[self.fieldName]:
                if dataType == "time":
                    values.append(f[self.fieldName].toPyTime())
                elif dataType == "date":
                    values.append(f[self.fieldName].toPyDate())
                else:
                    values.append(f[self.fieldName].toPyDateTime())
        stat.finalize()

        data = []
        data.append(self.tr("Count:{}".format(stat.count())))
        data.append(self.tr("Unique values:{}".format(stat.countDistinct())))
        data.append(self.tr("Minimum:{}".format(stat.min().toString())))
        data.append(self.tr("Maximum:{}".format(stat.max().toString())))
        data.append(self.tr("Range (days):{}".format(stat.range().days())))
        data.append(self.tr("Missing (NULL) values:{}".format(stat.countMissing())))
        return values, data

