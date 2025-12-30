# -*- coding: utf-8 -*-
"""
Cool Lines! — Maya 2022+ PySide6/PySide2 UI and Line Painting Tool

----------

version 1.00    --/--/----

Author: Victor Schenck
Email: -
Created: 2025

----------

version 1.01    12/30/2025

Description : Updating script to handle Pyside6 compat, Maya (2025+)

Contributor: Clement Daures
Company: The Rigging Atlas
Email: theriggingatlas@proton.me
"""
from ui.pyside_compat import (
    QtWidgets, QtCore, QtGui,
)


class CoolImgButton(QtWidgets.QPushButton):
    def __init__(self, img_path:str, btn_size :QtCore.QSize, img_size :QtCore.QSize, bg_color :QtGui.QColor, corner_radius= 10, *args, **kwargs):
        QtWidgets.QPushButton.__init__(self, *args, **kwargs)

        self.button_size= btn_size
        self.pixmap= QtGui.QPixmap(img_path)
        self.corner_radius= corner_radius
        self.img_size= img_size
        self.bg_color= bg_color


    def paintEvent(self, event):
        
        btn_rect= event.rect()
                   
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        p_path= QtGui.QPainterPath()
        p_path.addRoundedRect(btn_rect, self.corner_radius, self.corner_radius)

        # Scale img
        scaled_pixmap = self.pixmap.scaled(
        self.img_size, 
        QtCore.Qt.KeepAspectRatioByExpanding,
        QtCore.Qt.SmoothTransformation
        )
    
        # Center img
        x = btn_rect.x() - (scaled_pixmap.width() - btn_rect.width()) / 2
        y = btn_rect.y() - (scaled_pixmap.height() - btn_rect.height()) / 2

        painter.fillPath(p_path, self.bg_color) # CD6C1B
        painter.drawPixmap(int(x), int(y), scaled_pixmap)


    def sizeHint(self):
        return self.button_size