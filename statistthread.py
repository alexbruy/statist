# -*- coding: utf-8 -*-

"""
***************************************************************************
    statistthread.py
    ---------------------
    Date                 : May 2013
    Copyright            : (C) 2013-2015 by Alexander Bruy
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
__date__ = 'May 2013'
__copyright__ = '(C) 2013-2015, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import math

from PyQt4.QtCore import pyqtSignal, QThread, QMutex

from qgis.core import QgsFeatureRequest


class StatistThread(QThread):
    rangeChanged = pyqtSignal(int)
    updateProgress = pyqtSignal()
    processFinished = pyqtSignal(list)
    processInterrupted = pyqtSignal()

    STRING_TYPES = ['String', 'varchar', 'char', 'text']

    def __init__(self, layer, fieldName, useSelection):
        QThread.__init__(self, QThread.currentThread())
        self.mutex = QMutex()
        self.stopMe = 0
        self.interrupted = False

        self.layer = layer
        self.fieldName = fieldName
        self.useSelection = useSelection

    def run(self):
        if self.getFieldType() in self.STRING_TYPES:
            statText, values = self.statisticsForText()
        else:
            statText, values = self.statisticsForNumbers()

        if not self.interrupted:
            self.processFinished.emit([statText, values])
        else:
            self.processInterrupted.emit()

    def stop(self):
        self.mutex.lock()
        self.stopMe = 1
        self.mutex.unlock()

        QThread.wait(self)

    def statisticsForNumbers(self):
        self.mutex.lock()
        self.stopMe = 0
        self.mutex.unlock()

        index = self.layer.fieldNameIndex(self.fieldName)

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
            self.rangeChanged.emit(count)
            for f in selection:
                if f[index]:
                    value = float(f[index])
                else:
                    value = 0.0

                if isFirst:
                    minValue = value
                    maxValue = value
                    isFirst = False
                else:
                    if value < minValue:
                        minValue = value
                    if value > maxValue:
                        maxValue = value

                values.append(value)
                sumValue += value

                self.updateProgress.emit()

                self.mutex.lock()
                s = self.stopMe
                self.mutex.unlock()
                if s == 1:
                    self.interrupted = True
                    break
        else:
            count = self.layer.featureCount()
            self.rangeChanged.emit(count)

            request = QgsFeatureRequest()
            request.setFlags(QgsFeatureRequest.NoGeometry)
            request.setSubsetOfAttributes([index])

            for f in self.layer.getFeatures(request):
                if f[index]:
                    value = float(f[index])
                else:
                    value = 0.0

                if isFirst:
                    minValue = value
                    maxValue = value
                    isFirst = False
                else:
                    if value < minValue:
                        minValue = value
                    if value > maxValue:
                        maxValue = value

                values.append(value)
                sumValue += value

                self.updateProgress.emit()

                self.mutex.lock()
                s = self.stopMe
                self.mutex.unlock()
                if s == 1:
                    self.interrupted = True
                    break

        # calculate additional values
        rValue = maxValue - minValue
        uniqueValue = getUniqueValuesCount(self.layer, index, self.useSelection)

        if count > 0:
            meanValue = sumValue / count
            if meanValue != 0.00:
                for v in values:
                    stdDevValue += ((v - meanValue) * (v - meanValue))
                stdDevValue = math.sqrt(stdDevValue / count)
                cvValue = stdDevValue / meanValue

        if count > 1:
            tmp = values
            tmp.sort()
            # calculate median
            if (count % 2) == 0:
                medianValue = 0.5 * (tmp[(count - 1) / 2] + tmp[count / 2])
            else:
                medianValue = tmp[(count + 1) / 2 - 1]

        # generate output
        statsText = []
        statsText.append(self.tr("Count:%d") % (count))
        statsText.append(self.tr("Unique values:%d") % (uniqueValue))
        statsText.append(self.tr("Minimum value:%f") % (minValue))
        statsText.append(self.tr("Maximum value:%f") % (maxValue))
        statsText.append(self.tr("Range:%f") % (rValue))
        statsText.append(self.tr("Sum:%f") % (sumValue))
        statsText.append(self.tr("Mean value:%f") % (meanValue))
        statsText.append(self.tr("Median value:%f") % (medianValue))
        statsText.append(self.tr("Standard deviation:%f") % (stdDevValue))
        statsText.append(self.tr("Coefficient of Variation:%f") % (cvValue))

        return statsText, values

    def statisticsForText(self):
        self.mutex.lock()
        self.stopMe = 0
        self.mutex.unlock()

        index = self.layer.fieldNameIndex(self.fieldName)

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
            self.rangeChanged.emit(count)
            for f in selection:
                if f[index]:
                    length = float(len(f[index]))
                else:
                    length = 0.0

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

                values.append(length)
                sumValue += length

                self.updateProgress.emit()

                self.mutex.lock()
                s = self.stopMe
                self.mutex.unlock()
                if s == 1:
                    self.interrupted = True
                    break
        else:
            count = self.layer.featureCount()
            self.rangeChanged.emit(count)

            request = QgsFeatureRequest()
            request.setFlags(QgsFeatureRequest.NoGeometry)
            request.setSubsetOfAttributes([index])

            for f in self.layer.getFeatures(request):
                if f[index]:
                    length = float(len(f[index]))
                else:
                    length = 0.0

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

                values.append(length)
                sumValue += length

                self.updateProgress.emit()

                self.mutex.lock()
                s = self.stopMe
                self.mutex.unlock()
                if s == 1:
                    self.interrupted = True
                    break

        # calculate mean length if possible
        n = float(len(values))
        if n > 0:
            meanValue = sumValue / n

        # generate output
        statsText = []
        statsText.append(self.tr("Minimum length:%d") % (minValue))
        statsText.append(self.tr("Maximum length:%d") % (maxValue))
        statsText.append(self.tr("Mean length:%f") % (meanValue))
        statsText.append(self.tr("Filled:%d") % (countFilled))
        statsText.append(self.tr("Empty:%d") % (countEmpty))
        statsText.append(self.tr("Count:%d") % (count))

        return statsText, values

    def getUniqueValuesCount(self):
        if self.useSelection:
            values = []
            idx = self.layer.fieldNameIndex(self.fieldName)
            for f in self.layer.selectedFeatures():
                if f[idx] not in values:
                    values.append(f[fieldIndex])
            return len(values)
        else:
            return len(layer.uniqueValues(fieldIndex))

    def getFieldType(self):
        fields = self.layer.pendingFields()
        for field in fields:
            if field.name() == self.fieldName:
                return field.typeName()
