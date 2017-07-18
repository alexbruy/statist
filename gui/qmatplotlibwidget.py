# -*- coding: utf-8 -*-

"""
***************************************************************************
    qmatplotlibwidget.py
    ---------------------
    Date                 : July 2014
    Copyright            : (C) 2014-2015 by Alexander Bruy
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
__copyright__ = '(C) 2014-2015, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QPalette, QIcon
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QAction

import matplotlib
mplVersion = matplotlib.__version__.split('.')

from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

if int(mplVersion[0]) >= 1 and int(mplVersion[1]) >= 4:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
else:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

pluginPath = os.path.split(os.path.dirname(__file__))[0]


class QMatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.parent = parent

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)

        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.figure.canvas.setFocusPolicy(Qt.ClickFocus)
        self.figure.canvas.setFocus()

        rcParams['font.serif'] = 'Verdana, Arial, Liberation Serif'
        rcParams['font.sans-serif'] = 'Tahoma, Arial, Liberation Sans'
        rcParams['font.cursive'] = 'Courier New, Arial, Liberation Sans'
        rcParams['font.fantasy'] = 'Comic Sans MS, Arial, Liberation Sans'
        rcParams['font.monospace'] = 'Courier New, Liberation Mono'


class QMatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = QMatplotlibCanvas()
        self.ax = self.canvas.ax
        self.figure = self.canvas.figure
        self.toolBar = NavigationToolbar(self.canvas, self)

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
        self.actionToggleGrid = QAction(self.tr('Toggle grid'), self.toolBar)
        self.actionToggleGrid.setIcon(
            QIcon(os.path.join(pluginPath, 'icons', 'toggleGrid.svg')))
        self.actionToggleGrid.setCheckable(True)

        self.actionToggleGrid.triggered.connect(self.toggleGrid)

        self.toolBar.insertAction(self.toolBar.actions()[7], self.actionToggleGrid)
        self.toolBar.insertSeparator(self.toolBar.actions()[8])

    def toggleGrid(self):
        self.ax.grid()
        self.canvas.draw()

    def alignLabels(self):
        self.figure.autofmt_xdate()

    def clear(self):
        self.ax.clear()
        self.canvas.draw()

    def setTitle(self, text):
        self.ax.set_title(text)

    def setXAxisCaption(self, text):
        self.ax.set_xlabel(text)

    def setYAxisCaption(self, text):
        self.ax.set_ylabel(text)
