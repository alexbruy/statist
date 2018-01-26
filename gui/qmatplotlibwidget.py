# -*- coding: utf-8 -*-

"""
***************************************************************************
    qmatplotlibwidget.py
    ---------------------
    Date                 : July 2014
    Copyright            : (C) 2014-2018 by Alexander Bruy
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
__date__ = 'July 2014'
__copyright__ = '(C) 2014-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QPalette, QIcon
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QAction

from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

pluginPath = os.path.split(os.path.dirname(__file__))[0]


class QMatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.parent = parent

        # Typically we want plot to be ~1.33x wider than tall.
        # Common sizes: (10, 7.5) and (12, 9)
        self.figure = Figure(figsize=(12, 9))

        self.axes = self.figure.add_subplot(111)

        # Remove the plot frame lines. They are unnecessary chartjunk.
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["right"].set_visible(False)

        # Ensure that the axis ticks only show up on the bottom and left
        # of the plot. Ticks on the right and top of the plot are generally
        # unnecessary chartjunk.
        self.axes.get_xaxis().tick_bottom()
        self.axes.get_yaxis().tick_left()

        FigureCanvasQTAgg.__init__(self, self.figure)
        FigureCanvasQTAgg.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

        self.figure.canvas.setFocusPolicy(Qt.ClickFocus)
        self.figure.canvas.setFocus()

        rcParams["font.serif"] = "Verdana, Arial, Liberation Serif"
        rcParams["font.sans-serif"] = "Tahoma, Arial, Liberation Sans"
        rcParams["font.cursive"] = "Courier New, Arial, Liberation Sans"
        rcParams["font.fantasy"] = "Comic Sans MS, Arial, Liberation Sans"
        rcParams["font.monospace"] = "Courier New, Liberation Mono"


class QMatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = QMatplotlibCanvas()
        self.axes = self.canvas.axes
        self.figure = self.canvas.figure
        self.toolBar = NavigationToolbar2QT(self.canvas, self)

        bgColor = self.palette().color(QPalette.Background).name()
        self.figure.set_facecolor(bgColor)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)
        self.layout.setMargin(0)

        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self._setupToolbar()

    def _setupToolbar(self):
        self.actionToggleGrid = QAction(self.tr("Toggle grid"), self.toolBar)
        self.actionToggleGrid.setIcon(
            QIcon(os.path.join(pluginPath, "icons", "toggleGrid.svg")))
        self.actionToggleGrid.setCheckable(True)

        self.actionToggleGrid.triggered.connect(self.toggleGrid)

        self.toolBar.insertAction(self.toolBar.actions()[7], self.actionToggleGrid)
        self.toolBar.insertSeparator(self.toolBar.actions()[8])

    def toggleGrid(self):
        self.axes.grid()
        self.canvas.draw()

    def alignLabels(self):
        self.figure.autofmt_xdate()

    def clear(self):
        self.axes.clear()
        if self.actionToggleGrid.isChecked():
            self.axes.grid()
        self.canvas.draw()

    def setTitle(self, text):
        self.axes.set_title(text, fontsize=22)

    def setXAxisCaption(self, text):
        self.axes.set_xlabel(text, fontsize=16)

    def setYAxisCaption(self, text):
        self.axes.set_ylabel(text, fontsize=16)

    def setXLimit(self, minimum, maximum):
        self.axes.xlim(minimum, maximum)

    def setYLimit(self, minimum, maximum):
        self.axes.ylim(minimum, maximum)
