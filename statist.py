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

import statistdialog
import aboutdialog
import statist_utils as utils

import resources_rc


class StatistPlugin:
    def __init__(self, iface):
        self.iface = iface

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        # For i18n support
        userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/statist"
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/statist"

        overrideLocale = bool(QSettings().value("locale/overrideFlag", False))
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", "")

        if QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + "/i18n/statist_" + localeFullName + ".qm"
        else:
            translationPath = systemPluginPath + "/i18n/statist_" + localeFullName + ".qm"

        self.localePath = translationPath
        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        if int(self.qgsVersion) < 10900:
            qgisVersion = self.qgsVersion[0] + "." + self.qgsVersion[2] + "." + self.qgsVersion[3]
            QMessageBox.warning(self.iface.mainWindow(),
                                QCoreApplication.translate("Statist", "Statist: Error"),
                                QCoreApplication.translate("Statist", "QGIS %s detected.\n") % (qgisVersion) +
                                QCoreApplication.translate("Statist", "This version of Statist requires at least QGIS 2.0\nPlugin will not be enabled.")
                               )
            return None

        self.actionRun = QAction(QCoreApplication.translate("Statist", "Statist"), self.iface.mainWindow())
        self.iface.registerMainWindowAction(self.actionRun, "Shift+S")
        self.actionRun.setIcon(QIcon(":/icons/statist.png"))
        self.actionRun.setWhatsThis("Calculate statistics for field")
        self.actionAbout = QAction(QCoreApplication.translate("Statist", "About Statist..."), self.iface.mainWindow())
        self.actionAbout.setIcon(QIcon(":/icons/about.png"))
        self.actionAbout.setWhatsThis("About Statist")

        self.iface.addPluginToVectorMenu(QCoreApplication.translate("Statist", "Statist"), self.actionRun)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate("Statist", "Statist"), self.actionAbout)
        self.iface.addVectorToolBarIcon(self.actionRun)

        self.actionRun.triggered.connect(self.run)
        self.actionAbout.triggered.connect(self.about)

    def unload(self):
        self.iface.unregisterMainWindowAction(self.actionRun)

        self.iface.removeVectorToolBarIcon(self.actionRun)
        self.iface.removePluginVectorMenu(QCoreApplication.translate("Statist", "Statist"), self.actionRun)
        self.iface.removePluginVectorMenu(QCoreApplication.translate("Statist", "Statist"), self.actionAbout)

    def run(self):
        layersCount = len(utils.getVectorLayerNames())
        if layersCount == 0:
            self.iface.messageBar().pushMessage(QCoreApplication.translate("Statist", "Project doesn't have any vector layers"))
            return

        d = statistdialog.StatistDialog(self.iface)
        d.show()
        d.exec_()

    def about(self):
        d = aboutdialog.AboutDialog()
        d.exec_()
