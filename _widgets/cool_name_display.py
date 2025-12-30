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



class CoolNameDisplay(QtWidgets.QWidget):

    name_changed= QtCore.Signal(str)

    def __init__(self, line_data, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)


        self.line_data= line_data
        
        self.main_layout= QtWidgets.QStackedLayout()
        self.setLayout(self.main_layout)


        self.name_label= QtWidgets.QLabel(self)
        self.name_label.setText(self.line_data["name"])

        self.name_lineedit= QtWidgets.QLineEdit(self)
        self.name_lineedit.hide()

        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.name_lineedit)



        self.edit_state= False

        # Connections:
        self.name_lineedit.editingFinished.connect(self.confirmChanges)


    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.switchMode()


    def switchMode(self):

        if self.edit_state:
            pass
        else:
            self.name_lineedit.setText(self.name_label.text())
            self.main_layout.setCurrentWidget(self.name_lineedit)
            
            self.name_lineedit.setFocus()
            self.name_lineedit.selectAll()
            
            self.edit_state=True


    def confirmChanges(self):

        new_text= self.name_lineedit.text()
        if new_text == '':
            self.main_layout.setCurrentWidget(self.name_label)
            self.edit_state= False
            return
        
        else:
            self.name_label.setText(new_text)
            self.main_layout.setCurrentWidget(self.name_label)
            self.edit_state= False
            self.name_changed.emit(new_text)
            
        
        
        