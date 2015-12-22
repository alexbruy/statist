# -*- coding: utf-8 -*-

"""
***************************************************************************
    statistdialog.py
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

import os

from PyQt4 import uic
from PyQt4.QtCore import Qt, QThread
from PyQt4.QtGui import QMessageBox, QDialog, QDialogButtonBox, QTableWidgetItem

from qgis.gui import QgsMapLayerProxyModel, QgsFieldProxyModel, QgsMessageBar

from statist.statisticscalcalculator import StatisticsCalculator


pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'statistdialogbase.ui'))


class StatistDialog(BASE, WIDGET):
    def __init__(self, iface, parent=None):
        super(StatistDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface

        self.thread = QThread()
        self.calculator = StatisticsCalculator()

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

        self.calculator.moveToThread(self.thread)
        self.calculator.calculated.connect(self.thread.quit)
        self.calculator.calculated.connect(self.processFinished)

        self.thread.started.connect(self.calculator.calculate)

        self.cmbLayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.cmbField.setFilters(QgsFieldProxyModel.Numeric | QgsFieldProxyModel.String)

        self.cmbField.setLayer(self.cmbLayer.currentLayer())

    def reloadFields(self):
        #self.axes.clear()
        #self.tblStatistics.clearContents()
        self.tblStatistics.setRowCount(0)

        layer = self.cmbLayer.currentLayer()
        self.cmbField.setLayer(layer)

        if layer.selectedFeatureCount() != 0:
            self.chkSelectedOnly.setChecked(True)
        else:
            self.chkSelectedOnly.setChecked(False)

    def accept(self):
        #self.axes.clear()
        #self.spnMinX.setValue(0.0)
        #self.spnMaxX.setValue(0.0)
        #self.lstStatistics.clearContents()
        self.tblStatistics.setRowCount(0)

        layer = self.cmbLayer.currentLayer()

        if self.chkSelectedOnly.isChecked() and \
                layer.selectedFeatureCount() == 0:
            QgsMessageBar.pushWarning(self.tr('No selection'),
                self.tr('There is no selection in the input layer. Uncheck '
                        'corresponding option or select some features before '
                        'running analysis'))
            return

        self.calculator.setLayer(layer)
        self.calculator.setField(self.cmbField.currentField())
        self.calculator.setSelectedOnly(self.chkSelectedOnly.isChecked())

        self.btnOk.setEnabled(False)
        self.btnClose.setEnabled(False)

        self.thread.start()

    def reject(self):
        QDialog.reject(self)

    def processFinished(self):
        rowCount = len(self.calculator.data)
        self.tblStatistics.setRowCount(rowCount)
        for i in xrange(rowCount):
            tmp = self.calculator.data[i].split(':')
            item = QTableWidgetItem(tmp[0])
            self.tblStatistics.setItem(i, 0, item)
            item = QTableWidgetItem(tmp[1])
            self.tblStatistics.setItem(i, 1, item)

        #self.lstStatistics.resizeRowsToContents()

        self.refreshPlot()

        self.btnOk.setEnabled(True)
        self.btnClose.setEnabled(True)

    def refreshPlot(self):
        #self.axes.clear()
        #self.axes.set_title(self.tr('Frequency distribution'))
        #interval = None

        #if len(self.calculator.values) == 0:
        #    return

        #if self.spnMinX.value() == self.spnMaxX.value():
        #    pass
        #else:
        #    interval = []
        #    if self.spnMinX.value() > self.spnMaxX.value():
        #        interval.append(self.spnMaxX.value())
        #        interval.append(self.spnMinX.value())
        #    else:
        #        interval.append(self.spnMinX.value())
        #        interval.append(self.spnMaxX.value())

        #if not self.chkAsPlot.isChecked():
        #    self.axes.hist(self.calculator.values, 18, interval, alpha=0.5, histtype='bar')
        #else:
        #    n, bins, pathes = self.axes.hist(self.calculator.values, 18, interval, alpha=0.5, histtype='bar')
        #    self.axes.clear()
        #    c = []
        #    for i in range(len(bins) - 1):
        #        s = bins[i + 1] - bins[i]
        #        c.append(bins[i] + (s / 2))

        #    self.axes.plot(c, n, 'ro-')

        #self.axes.grid(self.chkShowGrid.isChecked())
        #self.axes.set_ylabel(self.tr('Count'))
        #self.axes.set_xlabel(self.cmbField.currentText())
        #self.figure.autofmt_xdate()
        #self.canvas.draw()

        self.mplWidget.axes.hist(self.calculator.values, 18, alpha=0.5, histtype='bar')
        self.mplWidget.canvas.draw()


    def keyPressEvent(self, event):
        if event.modifiers() in [Qt.ControlModifier, Qt.MetaModifier] and event.key() == Qt.Key_C:
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(self.calculator.data))
        else:
            QDialog.keyPressEvent(self, event)
