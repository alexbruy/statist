# -*- coding: utf-8 -*-

"""
***************************************************************************
    aboutdialog.py
    ---------------------
    Date                 : July 2013
    Copyright            : (C) 2013-2018 by Alexander Bruy
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
__date__ = 'July 2013'
__copyright__ = '(C) 2013-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import configparser

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QTextDocument, QPixmap, QDesktopServices
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog

from qgis.core import QgsApplication

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, "ui", "aboutdialogbase.ui"))


class AboutDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

        self.btnHelp = self.buttonBox.button(QDialogButtonBox.Help)

        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(pluginPath, "metadata.txt"))
        version = cfg["general"]["version"]

        self.lblLogo.setPixmap(
            QPixmap(os.path.join(pluginPath, "icons", "statist.png")))
        self.lblVersion.setText(self.tr("Version: {}".format(version)))

        doc = QTextDocument()
        doc.setHtml(self.getAboutText())
        self.textBrowser.setDocument(doc)
        self.textBrowser.setOpenExternalLinks(True)

        self.buttonBox.helpRequested.connect(self.openHelp)

    def openHelp(self):
        locale = QgsApplication.locale()

        if locale in ["uk"]:
            QDesktopServices.openUrl(
                QUrl("https://github.com/alexbruy/statist"))
        else:
            QDesktopServices.openUrl(
                QUrl("https://github.com/alexbruy/statist"))

    def getAboutText(self):
        return self.tr(
            "<p>Calculates basic statistics information on any (numeric, text, "
            "date/time) field of the vector layer. Also shows frequency "
            "distribution.</p>"
            "<p><strong>Developers</strong>: Alexander Bruy</p>"
            "<p><strong>Homepage</strong>: "
            "<a href='https://github.com/alexbruy/statist'>"
            "https://github.com/alexbruy/statist</a></p>"
            "<p>Please report bugs at "
            "<a href='https://github.com/alexbruy/statist/issues/'>"
            "bugtracker</a>.</p>")
