# -*- coding: utf-8 -*-

#******************************************************************************
#
# Statist
# ---------------------------------------------------------
# Provides basic statistics information on any (numeric or string) field
# of vector layer.
#
# Copyright (C) 2009-2013 Alexander Bruy (alexander.bruy@gmail.com)
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


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from ui.ui_statistdialogbase import Ui_StatistDialog

import statistthread
import statist_utils as utils

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams


class StatistDialog(QDialog, Ui_StatistDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

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
        rcParams["font.serif"] = "Verdana, Arial, Liberation Serif"
        rcParams["font.sans-serif"] = "Tahoma, Arial, Liberation Sans"
        rcParams["font.cursive"] = "Courier New, Arial, Liberation Sans"
        rcParams["font.fantasy"] = "Comic Sans MS, Arial, Liberation Sans"
        rcParams["font.monospace"] = "Courier New, Liberation Mono"

        self.values = None

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

        self.cmbLayers.currentIndexChanged.connect(self.reloadFields)
        self.chkUseTextFields.stateChanged.connect(self.reloadFields)

        self.chkShowGrid.stateChanged.connect(self.refreshPlot)
        self.chkAsPlot.stateChanged.connect(self.refreshPlot)
        self.btnRefresh.clicked.connect(self.refreshPlot)

        self.manageGui()
        self.axes.set_title(self.tr("Frequency distribution"))

    def manageGui(self):
        self.cmbLayers.clear()
        self.cmbLayers.addItems(utils.getVectorLayerNames())

        self.btnRefresh.setEnabled(False)

    def reloadFields(self):
        self.cmbFields.clear()

        self.axes.clear()
        self.lstStatistics.clearContents()
        self.lstStatistics.setRowCount(0)

        self.spnMinX.setValue(0.0)
        self.spnMaxX.setValue(0.0)

        layer = utils.getVectorLayerByName(self.cmbLayers.currentText())

        if layer.selectedFeatureCount() != 0:
            self.chkUseSelected.setCheckState(Qt.Checked)
        else:
            self.chkUseSelected.setCheckState(Qt.Unchecked)

        if self.chkUseTextFields.checkState():
            self.cmbFields.addItems(utils.getFieldNames(layer, [QVariant.String]))
        else:
            self.cmbFields.addItems(utils.getFieldNames(layer, [QVariant.Int, QVariant.Double]))

    def accept(self):
        self.axes.clear()
        self.spnMinX.setValue(0.0)
        self.spnMaxX.setValue(0.0)
        self.lstStatistics.clearContents()
        self.lstStatistics.setRowCount(0)

        layer = utils.getVectorLayerByName(self.cmbLayers.currentText())

        if self.chkUseSelected.isChecked() and \
                layer.selectedFeatureCount() == 0:
            QMessageBox.warning(self,
                                self.tr('No selection'),
                                self.tr('There is no selection in input '
                                        'layer. Uncheck corresponding option '
                                        'or select some features before '
                                        'running analysis'))
            return

        self.workThread = statistthread.StatistThread(layer,
                                                      self.cmbFields.currentText(),
                                                      self.chkUseSelected.isChecked()
                                                     )
        self.workThread.rangeChanged.connect(self.setProgressRange)
        self.workThread.updateProgress.connect(self.updateProgress)
        self.workThread.processFinished.connect(self.processFinished)
        self.workThread.processInterrupted.connect(self.processInterrupted)

        self.btnOk.setEnabled(False)
        self.btnClose.setText(self.tr("Cancel"))
        self.buttonBox.rejected.disconnect(self.reject)
        self.btnClose.clicked.connect(self.stopProcessing)

        self.workThread.start()

    def reject(self):
        QDialog.reject(self)

    def setProgressRange(self, maxValue):
        self.progressBar.setRange(0, maxValue)

    def updateProgress(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

    def processFinished(self, statData):
        self.stopProcessing()

        # populate table with results
        self.tableData = statData[0]
        self.values = statData[1]
        rowCount = len(self.tableData)
        self.lstStatistics.setRowCount(rowCount)
        for i in xrange(rowCount):
            tmp = self.tableData[i].split(":")
            item = QTableWidgetItem(tmp[0])
            self.lstStatistics.setItem(i, 0, item)
            item = QTableWidgetItem(tmp[1])
            self.lstStatistics.setItem(i, 1, item)

        self.lstStatistics.resizeRowsToContents()

        self.btnRefresh.setEnabled(True)

        # create histogram
        self.refreshPlot()

        self.restoreGui()

    def processInterrupted(self):
        self.restoreGui()

    def stopProcessing(self):
        if self.workThread is not None:
            self.workThread.stop()
            self.workThread = None

    def restoreGui(self):
        self.progressBar.setFormat("%p%")
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)

        self.buttonBox.rejected.connect(self.reject)
        self.btnClose.clicked.disconnect(self.stopProcessing)
        self.btnClose.setText(self.tr("Close"))
        self.btnOk.setEnabled(True)

    def refreshPlot(self):
        self.axes.clear()
        self.axes.set_title(self.tr("Frequency distribution"))
        interval = None

        if self.values is None:
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
            self.axes.hist(self.values, 18, interval, alpha=0.5, histtype="bar")
        else:
            n, bins, pathes = self.axes.hist(self.values, 18, interval, alpha=0.5, histtype="bar")
            self.axes.clear()
            c = []
            for i in range(len(bins) - 1):
                s = bins[i + 1] - bins[i]
                c.append(bins[i] + (s / 2))

            self.axes.plot(c, n, "ro-")

        self.axes.grid(self.chkShowGrid.isChecked())
        self.axes.set_ylabel(unicode(self.tr("Count")))
        self.axes.set_xlabel(unicode(self.cmbFields.currentText()))
        self.figure.autofmt_xdate()
        self.canvas.draw()

    def keyPressEvent(self, event):
        if event.modifiers() in [Qt.ControlModifier, Qt.MetaModifier] and event.key() == Qt.Key_C:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(self.tableData))
        else:
            QDialog.keyPressEvent(self, event)
