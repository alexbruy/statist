# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
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

from PyQt4.QtCore import (QCoreApplication, QSettings, QLocale, QTranslator)
from PyQt4.QtGui import (QMessageBox, QAction, QIcon, QMenu)

from qgis.core import QGis

from statist.gui.statistdialog import StatistDialog
from statist.gui.aboutdialog import AboutDialog


pluginPath = os.path.dirname(__file__)


class StatistPlugin:
    def __init__(self, iface):
        self.iface = iface

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        overrideLocale = QSettings().value('locale/overrideFlag', False, bool)
        if not overrideLocale:
            locale = QLocale.system().name()[:2]
        else:
            locale = QSettings().value('locale/userLocale', '')

        qmPath = '{}/i18n/statist_{}.qm'.format(pluginPath, locale)

        if os.path.exists(qmPath):
            self.translator = QTranslator()
            self.translator.load(qmPath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        if int(self.qgsVersion) < 20000:
            qgisVersion = '{}.{}.{}'.format(
                self.qgsVersion[0], self.qgsVersion[2], self.qgsVersion[3])
            QMessageBox.warning(self.iface.mainWindow(), 'Statist',
                self.tr('QGIS {} detected.\nThis version of Statist '
                        'requires at least QGIS 2.0. Plugin will not be '
                        'enabled.'.format(qgisVersion)))
            return None

        self.actionRun = QAction(
            self.tr('Statist'), self.iface.mainWindow())
        self.actionRun.setIcon(
            QIcon(os.path.join(pluginPath, 'icons', 'statist.png')))
        self.actionRun.setWhatsThis(
            self.tr('Calculate statistics for a field'))
        self.actionRun.setObjectName('runStatist')
        self.iface.registerMainWindowAction(self.actionRun, "Shift+S")

        self.actionAbout = QAction(
            self.tr('About Statist...'), self.iface.mainWindow())
        self.actionAbout.setIcon(
            QIcon(os.path.join(pluginPath, 'icons', 'about.png')))
        self.actionAbout.setWhatsThis(self.tr('About Statist'))
        self.actionRun.setObjectName('aboutStatist')

        self.iface.addPluginToVectorMenu(
            self.tr('Statist'), self.actionRun)
        self.iface.addPluginToVectorMenu(
            self.tr('Statist'), self.actionAbout)
        self.iface.addVectorToolBarIcon(self.actionRun)

        self.actionRun.triggered.connect(self.run)
        self.actionAbout.triggered.connect(self.about)

    def unload(self):
        self.iface.unregisterMainWindowAction(self.actionRun)

        self.iface.removePluginVectorMenu(
            self.tr('Statist'), self.actionRun)
        self.iface.removePluginVectorMenu(
            self.tr('Statist'), self.actionAbout)
        self.iface.removeVectorToolBarIcon(self.actionRun)

    def run(self):
        dlg = StatistDialog(self.iface)
        dlg.show()
        dlg.exec_()

    def about(self):
        d = AboutDialog()
        d.exec_()

    def tr(self, text):
        return QCoreApplication.translate('Statist', text)
