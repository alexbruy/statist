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

import matplotlib
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

version = matplotlib.__version__.split('.')
if int(version[0]) >= 1 and int(version[1]) >= 5:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
else:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from qgis.gui import QgsMapLayerProxyModel, QgsFieldProxyModel

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

        # add matplotlib figure to dialog
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.mpltoolbar = NavigationToolbar(self.canvas, self.widgetPlot)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction(lstActions[7])
        self.layoutPlot.addWidget(self.canvas)
        self.layoutPlot.addWidget(self.mpltoolbar)

        # and configure matplotlib params
        rcParams['font.serif'] = 'Verdana, Arial, Liberation Serif'
        rcParams['font.sans-serif'] = 'Tahoma, Arial, Liberation Sans'
        rcParams['font.cursive'] = 'Courier New, Arial, Liberation Sans'
        rcParams['font.fantasy'] = 'Comic Sans MS, Arial, Liberation Sans'
        rcParams['font.monospace'] = 'Courier New, Liberation Mono'

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

        self.chkShowTextFields.stateChanged.connect(self.reloadFields)

        self.chkShowGrid.stateChanged.connect(self.refreshPlot)
        self.chkAsPlot.stateChanged.connect(self.refreshPlot)
        self.btnRefresh.clicked.connect(self.refreshPlot)

        self.calculator.moveToThread(self.thread)
        self.calculator.calculated.connect(self.thread.quit)
        self.calculator.calculated.connect(self.processFinished)

        self.thread.started.connect(self.calculator.calculate)

        self.axes.set_title(self.tr('Frequency distribution'))

        self.cmbLayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.cmbField.setLayer(self.cmbLayer.currentLayer())
        self.btnRefresh.setEnabled(False)

    def reloadFields(self):
        self.axes.clear()
        self.lstStatistics.clearContents()
        self.lstStatistics.setRowCount(0)

        self.spnMinX.setValue(0.0)
        self.spnMaxX.setValue(0.0)

        layer = self.cmbLayer.currentLayer()

        if layer.selectedFeatureCount() != 0:
            self.chkUseSelected.setCheckState(Qt.Checked)
        else:
            self.chkUseSelected.setCheckState(Qt.Unchecked)

        if self.chkShowTextFields.checkState():
            self.cmbField.setFilters(QgsFieldProxyModel.Numeric | QgsFieldProxyModel.String)
        else:
            self.cmbField.setFilters(QgsFieldProxyModel.Numeric)

        self.cmbField.setLayer(layer)

    def accept(self):
        self.axes.clear()
        self.spnMinX.setValue(0.0)
        self.spnMaxX.setValue(0.0)
        self.lstStatistics.clearContents()
        self.lstStatistics.setRowCount(0)

        layer = self.cmbLayer.currentLayer()

        if self.chkUseSelected.isChecked() and \
                layer.selectedFeatureCount() == 0:
            QMessageBox.warning(self,
                                self.tr('No selection'),
                                self.tr('There is no selection in input '
                                        'layer. Uncheck corresponding option '
                                        'or select some features before '
                                        'running analysis'))
            return

        self.calculator.setLayer(layer)
        self.calculator.setField(self.cmbField.currentField())
        self.calculator.setSelectedOnly(self.chkUseSelected.isChecked())

        self.btnOk.setEnabled(False)
        self.btnClose.setEnabled(False)

        self.thread.start()

    def reject(self):
        QDialog.reject(self)

    def processFinished(self):
        rowCount = len(self.calculator.data)
        self.lstStatistics.setRowCount(rowCount)
        for i in xrange(rowCount):
            tmp = self.calculator.data[i].split(':')
            item = QTableWidgetItem(tmp[0])
            self.lstStatistics.setItem(i, 0, item)
            item = QTableWidgetItem(tmp[1])
            self.lstStatistics.setItem(i, 1, item)

        self.lstStatistics.resizeRowsToContents()

        self.refreshPlot()

        self.btnRefresh.setEnabled(True)
        self.btnOk.setEnabled(True)
        self.btnClose.setEnabled(True)

    def refreshPlot(self):
        self.axes.clear()
        self.axes.set_title(self.tr('Frequency distribution'))
        interval = None

        if len(self.calculator.values) == 0:
            return

        if self.spnMinX.value() == self.spnMaxX.value():
            pass
        else:
            interval = []
            if self.spnMinX.value() > self.spnMaxX.value():
                interval.append(self.spnMaxX.value())
                interval.append(self.spnMinX.value())
            else:
                interval.append(self.spnMinX.value())
                interval.append(self.spnMaxX.value())

        if not self.chkAsPlot.isChecked():
            self.axes.hist(self.calculator.values, 18, interval, alpha=0.5, histtype='bar')
        else:
            n, bins, pathes = self.axes.hist(self.calculator.values, 18, interval, alpha=0.5, histtype='bar')
            self.axes.clear()
            c = []
            for i in range(len(bins) - 1):
                s = bins[i + 1] - bins[i]
                c.append(bins[i] + (s / 2))

            self.axes.plot(c, n, 'ro-')

        self.axes.grid(self.chkShowGrid.isChecked())
        self.axes.set_ylabel(self.tr('Count'))
        self.axes.set_xlabel(self.cmbField.currentText())
        self.figure.autofmt_xdate()
        self.canvas.draw()

    def keyPressEvent(self, event):
        if event.modifiers() in [Qt.ControlModifier, Qt.MetaModifier] and event.key() == Qt.Key_C:
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(self.tableData))
        else:
            QDialog.keyPressEvent(self, event)
