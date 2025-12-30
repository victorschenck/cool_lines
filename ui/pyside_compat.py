# -*- coding: utf-8 -*-
"""
PySide compatibility layer for Maya 2022+
Automatically detects and imports the correct PySide version

---

version 1.01    12/30/2025

Contributor: Clement Daures
Company: The Rigging Atlas
Email: theriggingatlas@proton.me
"""

# ---------- IMPORT ----------

import sys
import maya.cmds as cmds

# ---------- SETUP ----------


# Detect Maya version
maya_version = int(cmds.about(version=True))

# Import the appropriate PySide version
if maya_version >= 2025:
    # Maya 2025+ uses PySide6
    import PySide6.QtWidgets as QtWidgets
    import PySide6.QtCore as QtCore
    import PySide6.QtGui as QtGui

    from PySide6.QtGui import QRegularExpressionValidator as QRegExpValidator
    from PySide6.QtCore import QRegularExpression as QRegExp
    from PySide6.QtGui import QAction


    import maya.OpenMayaUI as omui
    from shiboken6 import wrapInstance

    PYSIDE_VERSION = 6

else:
    # Maya 2017-2024 uses PySide2
    import PySide2.QtWidgets as QtWidgets
    import PySide2.QtCore as QtCore
    import PySide2.QtGui as QtGui

    from PySide2.QtGui import QRegExpValidator
    from PySide2.QtCore import QRegExp
    from PySide2.QtWidgets import QAction

    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance

    PYSIDE_VERSION = 2


def get_maya_main_window():
    """
    Get Maya's main window as a Qt widget.
    Compatible with both PySide2 and PySide6.

    Returns:
        QWidget: Maya's main window widget or None
    """
    ptr = omui.MQtUtil.mainWindow()
    if ptr:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    return None


# Export commonly used classes for easy imports
__all__ = [
    'QtWidgets',
    'QtCore',
    'QtGui',
    'QRegExp',
    'QRegExpValidator',
    'QAction',
    'get_maya_main_window',
    'wrapInstance',
    'PYSIDE_VERSION'
]