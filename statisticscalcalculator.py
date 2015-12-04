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


from PyQt4.QtCore import pyqtSignal, QObject

from qgis.core import QgsStatisticalSummary


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
        self.data[:] = []
        self.values[:] = []

        if self._isTextField():
            values, _ = self.layer.getValues(self.fieldName, self.selectedOnly)
            stat = TextStatisticalSummary()
            stat.calculate(values)

            self.values = stat.data

            self.data.append(self.tr('Count:{}'.format(stat.count)))
            self.data.append(self.tr('Unique values:{}'.format(stat.variety)))
            self.data.append(self.tr('Minimum length:{}'.format(stat.min)))
            self.data.append(self.tr('Maximum length:{}'.format(stat.max)))
            self.data.append(self.tr('Mean length:{}'.format(stat.mean)))
            self.data.append(self.tr('Missing (NULL) values:{}'.format(stat.nullCount)))
        else:
            self.values, _, nulls = self.layer.getDoubleValues(self.fieldName, self.selectedOnly)
            stat = QgsStatisticalSummary()
            stat.calculate(self.values)

            if stat.mean() != 0.0:
                cV = stat.stDev() / stat.mean()
            else:
                cV = 0.0

            self.data.append(self.tr('Count:{}'.format(stat.count())))
            self.data.append(self.tr('Unique values:{}'.format(stat.variety())))
            self.data.append(self.tr('Minimum value:{}'.format(stat.min())))
            self.data.append(self.tr('Maximum value:{}'.format(stat.max())))
            self.data.append(self.tr('Range:{}'.format(stat.range())))
            self.data.append(self.tr('Sum:{}'.format(stat.sum())))
            self.data.append(self.tr('Mean value:{}'.format(stat.mean())))
            self.data.append(self.tr('Median value:{}'.format(stat.median())))
            self.data.append(self.tr('Standard deviation:{}'.format(stat.stDev())))
            self.data.append(self.tr('Coefficient of Variation:{}'.format(cV)))
            self.data.append(self.tr('Minority (rarest occurring value):{}'.format(stat.minority())))
            self.data.append(self.tr('Majority (most frequently occurring value):{}'.format(stat.majority())))
            self.data.append(self.tr('First quartile:{}'.format(stat.firstQuartile())))
            self.data.append(self.tr('Third quartile:{}'.format(stat.thirdQuartile())))
            self.data.append(self.tr('Interquartile Range (IQR):{}'.format(stat.interQuartileRange())))
            self.data.append(self.tr('Missing (NULL) values:{}'.format(nulls)))

        self.calculated.emit()

    def _isTextField(self):
        idx = self.layer.fieldNameIndex(self.fieldName)
        fields = self.layer.pendingFields()
        if fields[idx].typeName().lower() in ['string', 'varchar', 'char', 'text']:
            return True
        else:
            return False


class TextStatisticalSummary:
    def __init__(self):
        self.count = 0
        self.nullCount = 0
        self.variety = 0
        self.min = -1
        self.max = -1
        self.mean = 0.0
        self.data = []

    def calculate(self, values):
        self.data[:] = []
        total = len(values)
        self.variety = len(set(values))
        first = True
        sumLength = 0

        for v in values:
            if not v:
                self.nullCount += 1
                continue

            length = len(v)
            self.data.append(length)

            if first:
                self.min = length
                self.max = length
                first = False

            if length < self.min:
                self.min = length
            if length > self.max:
                self.max = length

            sumLength += length

        self.count = total - self.nullCount
        if self.count > 0:
            self.mean = float(sumLength) / self.count
