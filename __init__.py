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


def name():
    return "Statist"


def description():
    return "Calculate and show statistics for a field"


def category():
    return "Vector"


def version():
    return "1.0.1"


def qgisMinimumVersion():
    return "1.8.0"


def author():
    return "Alexander Bruy"


def email():
    return "alexander.bruy@gmail.com"


def icon():
    return "icons/statist.png"


def classFactory(iface):
    from PyQt4.QtGui import QMessageBox

    wnd = iface.mainWindow()

    try:
        import matplotlib.backends.backend_qt4agg
    except ImportError:
        QMessageBox.warning(wnd,
                            wnd.tr("Error while loading plugin"),
                            wnd.tr("Could not find the matplotlib module.\nMake sure the matplotlib is installed")
                           )

        raise ImportError("Missing matplotlib Python module")

    from statist import StatistPlugin
    return StatistPlugin(iface)
