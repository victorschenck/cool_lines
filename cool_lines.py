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

import sys
sys.path.append("INSTALLATION_PATH_REPLACE_STRING")
from importlib import reload
from pathlib import Path

from maya import cmds, mel
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from ui.pyside_compat import (
    QtWidgets, QtCore, QtGui,
    QRegExp,
    QRegExpValidator,
    QAction,
    get_maya_main_window,
)


import scene_data
reload(scene_data)

from _widgets import cool_checkbox, cool_name_display, cool_img_button
reload(cool_checkbox)
reload(cool_name_display)
reload(cool_img_button)

from _widgets.cool_checkbox import CoolCheckbox
from _widgets.cool_name_display import CoolNameDisplay
from _widgets.cool_img_button import CoolImgButton


orange_theme= """
    QWidget {
        background-color: transparent;
        color: #fa901e;
        border: none;
    }
    QPushButton {
        background-color: #CD6C1B;
        border-radius: 10px;
        color: #F8D7BB;
        padding: 7px;
    }
    QPushButton:hover {
        background-color: #823F06;
    }
    QCheckBox {
        color: #fa901e;
    }
    QLineEdit {
        background-color: #220E00;
        border: none;
        border-radius: 6px;
        color: #fa901e;
        padding: 3px;
    }
    QTextEdit {
        background-color: #4d4d4d;
        border: 1px solid #4d4d4d;
        color: #fa901e;
        padding: 3px;
    }
    QProgressBar {
        border: 1px solid #444444;
        border-radius: 7px;
        background-color: #2e2e2e;
        text-align: center;
        font-size: 10pt;
        color: white;
    }
    QProgressBar::chunk {
        background-color: #3a3a3a;
        width: 5px;
    }
    QScrollBar:vertical {
        border: none;
        background-color: transparent;
        width: 10px;
        margin: 16px 0 16px 0;
    }
    QScrollBar::handle:vertical {
        background-color: #fa901e;
        border-radius: 5px;
    }
    QScrollBar:horizontal {
        border: none;
        background-color: #fa901e;
        height: 10px;
        margin: 0px 16px 0 16px;
    }
    QScrollBar::handle:horizontal {
        background-color: #444444;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px; 
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QTabWidget {
        background-color: #2e2e2e;
        border: none;
    }
    QTabBar::tab {
        background-color: #2e2e2e;
        color: #fa901e;
        padding: 7px 7px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        border: none;
    }
 
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #fa901e;
        color: white;
    }

    QListWidget{
        border-radius: 10px;
        background-color: #220E00;
    }

    QListView::item:selected{
        border-radius: 10px;
        background-color: #A3541A;
    }

    QMenu{
        background-color: #220E00;
    }

    QMenu::item:selected{
        background-color: #462002;
        color: #fa901e;
    }

    QDialog{
        background-color: #462002;
    }"""

# light brown #462002
# dark brown #220E00

main_window_instance= None
paint_on_mesh= None
scene_lines_data= {}
global_scene_data_obj= scene_data.GlobalSceneData()
cool_lines_shader= None
line_default_scale= 0.1
line_subdiv_offset= 0.1
line_resolution= 10

# Installing script job to refresh file on opened
scene_event_catcher_num= cmds.scriptJob(event=["SceneOpened", global_scene_data_obj.detectSceneChange])
print(scene_event_catcher_num)


def detectOrCreateShader():

    global cool_lines_shader
    if cmds.objExists('CoolLinesShader'):
        cool_lines_shader= 'CoolLinesShader'

    else:
        print('Preview Shader for outlines not found... Creating one.')
        cool_lines_shader= cmds.createNode('surfaceShader', name="CoolLinesShader", ss=True)
    
    return cool_lines_shader


class DockableWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super(DockableWindow, self).__init__(parent)

        self.setGeometry(200,200,200,600)

        #Making the window appear on top:
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Cool Lines!')
        
        #Creating the tab widget:
        self.main_widget = mainWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_widget)

        #Adding menu bar:
        #Creating the Tool Bar:
        menu_bar = QtWidgets.QMenuBar(self)
        self.main_layout.setMenuBar(menu_bar)
        file_menu = menu_bar.addMenu("File")
        bake_menu = menu_bar.addMenu("Bake")
        
        refresh_file_action = QAction("Manual Refesh", self)
        refresh_file_action.triggered.connect(self.fileChange)
        refresh_file_action.setShortcut(QtGui.QKeySequence("Alt+R"))
        file_menu.addAction(refresh_file_action)

        bake_line_action = QAction("Bake All Lines", self)
        bake_line_action.triggered.connect(bakeAllLines)
        bake_menu.addAction(bake_line_action)

        self.setStyleSheet(orange_theme)

    def closeEvent(self, event: QtGui.QCloseEvent):
        print(f"Clearing scene event catcher: {scene_event_catcher_num}")
        cmds.scriptJob(kill=scene_event_catcher_num, force=True)
        event.accept()

    
    def dockCloseEventTriggered(self):
        print(f"Clearing scene event catcher: {scene_event_catcher_num}")
        cmds.scriptJob(kill=scene_event_catcher_num, force=True)
        super(DockableWindow, self).dockCloseEventTriggered()


    def fileChange(self):
        global_scene_data_obj.detectSceneChange()



class mainWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        #Main Layout:
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setStyleSheet('''font: 75 13pt "Microsoft YaHei UI";''')

        #####################################
        #Creation
        self.target_mesh_label = QtWidgets.QLabel(self)
        self.target_mesh_label.setText('Target Mesh')
        
        self.set_target_mesh_hlayout = QtWidgets.QHBoxLayout()

        self.set_target_mesh_lineedit = QtWidgets.QLineEdit(self)
        self.set_target_mesh_button = QtWidgets.QPushButton(self)
        self.set_target_mesh_button.setText('Set !')

        self.set_target_mesh_hlayout.addWidget(self.set_target_mesh_lineedit)
        self.set_target_mesh_hlayout.addWidget(self.set_target_mesh_button)


        self.paint_options_buttons_hlayout= QtWidgets.QHBoxLayout()

        brush_icon_path= Path(scene_data.__file__).parent / './_icons/brush_icon.png'
        self.create_paint_line_button= CoolImgButton(img_path=brush_icon_path.as_posix(), btn_size= QtCore.QSize(80, 80), img_size=QtCore.QSize(70,70),
                                          bg_color= QtGui.QColor("#CD6C1B"))
        self.create_paint_line_button.setToolTip("Draw a line on the target mesh !")
        
        edge_line_icon_path= Path(scene_data.__file__).parent / './_icons/edge_line_icon.png'
        self.create_edge_line_button= CoolImgButton(img_path=edge_line_icon_path.as_posix(), btn_size= QtCore.QSize(80, 80), img_size=QtCore.QSize(70,70),
                                          bg_color= QtGui.QColor("#CD6C1B"))
        self.create_edge_line_button.setToolTip("Use an edge of the target mesh to generate a line !")
        
        paint_bucket_icon_path= Path(scene_data.__file__).parent / './_icons/paint_bucket_icon.png'
        self.assign_shader_button= CoolImgButton(img_path=paint_bucket_icon_path.as_posix(), btn_size= QtCore.QSize(80, 80), img_size=QtCore.QSize(70,70),
                                          bg_color= QtGui.QColor("#CD6C1B"))
        self.assign_shader_button.setToolTip("Assign default line shader to selected strokes !")
        
        self.paint_options_buttons_hlayout.addStretch()
        self.paint_options_buttons_hlayout.addWidget(self.create_paint_line_button)
        self.paint_options_buttons_hlayout.addWidget(self.create_edge_line_button)
        self.paint_options_buttons_hlayout.addWidget(self.assign_shader_button)
        self.paint_options_buttons_hlayout.addStretch()


        self.default_scale_title_label= QtWidgets.QLabel(self)
        self.default_scale_title_label.setText("Default Scale")


        self.default_scale_lineedit = QtWidgets.QLineEdit(self)
        validator = QRegExpValidator(QRegExp(r'[0-9]+.[0-9][0-9][0-9][0-9]'))
        self.default_scale_lineedit.setValidator(validator)
        self.default_scale_lineedit.setText('0.100')

        self.subdived_target_offset_label= QtWidgets.QLabel(self)
        self.subdived_target_offset_label.setText("Subdiv Offset")
        self.subdived_target_offset_label.setToolTip("When drawing on subdived mesh, the line clips inside. You can adjust it here.")

        self.subdived_target_offset_lineedit = QtWidgets.QLineEdit(self)
        validator = QRegExpValidator(QRegExp(r'[0-9]+.[0-9][0-9][0-9][0-9]'))
        self.subdived_target_offset_lineedit.setValidator(validator)
        self.subdived_target_offset_lineedit.setText('0.1')

        self.line_resolution_label= QtWidgets.QLabel(self)
        self.line_resolution_label.setText("Line Resolution")
        self.line_resolution_label.setToolTip("1 is full accuracy (too much). Default is 5. The more you add, the lower the resolution gets.")

        self.line_resolution_lineedit = QtWidgets.QLineEdit(self)
        validator = QRegExpValidator(QRegExp(r'[0-9][0-9][0-9][0-9][0-9]'))
        self.line_resolution_lineedit.setValidator(validator)
        self.line_resolution_lineedit.setText('5')

        self.scene_content_label= QtWidgets.QLabel(self)
        self.scene_content_label.setText("Scene Content")

        self.lines_list_widget = QtWidgets.QListWidget(self)
        self.lines_list_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lines_list_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.lines_list_widget.viewport().installEventFilter(self)

        self.credits_label= QtWidgets.QLabel(self)
        self.credits_label.setText("Credits (Hover)")
        self.credits_label.setToolTip("Dev: Victor Schenck / Sources: Beranger Roussel's website / Icons: icons8.com")
        self.credits_label.setStyleSheet("""font: 75 8pt "Microsoft YaHei UI";""")

        
        #####################################
        #Organizing:
        self.main_layout.addWidget(self.target_mesh_label)
        self.main_layout.addLayout(self.set_target_mesh_hlayout)

        self.main_layout.addLayout(self.paint_options_buttons_hlayout)

        self.main_layout.addWidget(self.default_scale_title_label)
        self.main_layout.addWidget(self.default_scale_lineedit)

        self.main_layout.addWidget(self.subdived_target_offset_label)
        self.main_layout.addWidget(self.subdived_target_offset_lineedit)
        
        self.main_layout.addWidget(self.line_resolution_label)
        self.main_layout.addWidget(self.line_resolution_lineedit)

        self.main_layout.addWidget(self.scene_content_label)
        self.main_layout.addWidget(self.lines_list_widget)

        self.main_layout.addWidget(self.credits_label)


        #####################################
        #Connections:

        global_scene_data_obj.request_ui_sync.connect(self.refreshList)
        global_scene_data_obj.request_ui_clear.connect(self.lines_list_widget.clear)

        self.set_target_mesh_button.clicked.connect(self.setTargetMeshButtonClicked)
        self.create_edge_line_button.clicked.connect(self.createLineFromEdge)
        self.create_paint_line_button.clicked.connect(self.paintLineOnMesh)
        self.assign_shader_button.clicked.connect(self.assignPreviewShader)

        self.lines_list_widget.itemClicked.connect(self.selectLineInMaya)

        self.default_scale_lineedit.textChanged.connect(self.changeLineDefaultScale)
        self.subdived_target_offset_lineedit.textChanged.connect(self.changeLineSubdivOffset)
        self.line_resolution_lineedit.textChanged.connect(self.changeLineResolution)


        self.refreshList()

        # extra
        self.target_mesh=None


    def eventFilter(self, source, event):
        # Deselect item when nothing clicked
        if source == self.lines_list_widget.viewport() and event.type() == QtCore.QEvent.MouseButtonPress:
            
            item = self.lines_list_widget.itemAt(event.pos())
            if not item:
                self.lines_list_widget.clearSelection()
        
        # Always return the parent's result so we don't break default behavior
        return super().eventFilter(source, event)

        
    def refreshList(self):
        
        # Scroll preservation store scroll value
        list_scrollbar = self.lines_list_widget.verticalScrollBar()
        current_scroll_value = list_scrollbar.value()

        
        self.lines_list_widget.clear()
        global_scene_data= global_scene_data_obj.getGlobalLinesData()

        for current_line_name in list(global_scene_data.keys()):

            current_line_data= dict(global_scene_data[current_line_name])

            # UI
            current_line_item = QtWidgets.QListWidgetItem()
            current_line_item.setData(QtCore.Qt.UserRole, current_line_data)

            current_line_item_widget = lineListDisplayWidget(current_line_data, current_line_item)
            current_line_item.setSizeHint(current_line_item_widget.sizeHint())

            self.lines_list_widget.addItem(current_line_item)
            self.lines_list_widget.setItemWidget(current_line_item, current_line_item_widget)
            current_line_item_widget.delete_line_item.connect(self.deleteLineItem)
        

        list_scrollbar.setValue(current_scroll_value) # Restore scroll value
        return
    
        


    def deleteLineItem(self, current_widget):
        self.lines_list_widget.takeItem(self.lines_list_widget.currentRow())
        global_scene_data_obj.removeLineData(current_widget.line_data["name"])
        self.deleteLineInMaya(current_widget.line_data)


    def changeLineDefaultScale(self):
        global line_default_scale
        user_input= self.default_scale_lineedit.text()
        if user_input == '': user_input= 0.01
        line_default_scale= float(user_input)


    def changeLineSubdivOffset(self):
        global line_subdiv_offset
        user_input= self.subdived_target_offset_lineedit.text()
        if user_input == '': user_input= 0.01
        line_subdiv_offset= float(user_input)

    
    def changeLineResolution(self):
        global line_resolution
        user_input= self.line_resolution_lineedit.text()
        if user_input == '': user_input= 5
        line_resolution= int(user_input)


    # Maya Interactions:
    def deleteLineInMaya(self, line_data):
        cmds.delete(line_data["group"])


    def selectLineInMaya(self, item):

        line_data= item.data(QtCore.Qt.UserRole)

        # Showing the "Selected !" Message on the selecteds mesh node
        cmds.headsUpMessage( 'Selected !', object= line_data["mesh"] )
        cmds.select([line_data["mesh"], line_data["taper_ctrl_node"]], r=True)
   

    def setTargetMeshButtonClicked(self):
        user_selection= cmds.ls(sl=True)[0]

        if "|" in user_selection: # Means obj is not unique !!!
            QtWidgets.QMessageBox.warning(self, "Can't paint :(", "This object's name is not unique !")
            return
        
        global paint_on_mesh
        paint_on_mesh = user_selection
        self.set_target_mesh_lineedit.setText(paint_on_mesh)


    def createLineFromEdge(self):

        # Getting Line default scale if editing was not done:
        self.changeLineDefaultScale()

        # Checking if selection is on paint on mesh:
        user_selection= cmds.ls(sl=True)

        if not user_selection:
            QtWidgets.QMessageBox.warning(self, "Can't paint :(", "Please select edges of the target mesh !")
            return

        if not paint_on_mesh:
            QtWidgets.QMessageBox.warning(self, "Can't paint :(", "Please provide a target mesh !")
            return

        if '.' in paint_on_mesh:
            QtWidgets.QMessageBox.warning(self, "Can't paint :(", "Please provide a valid target mesh, not a component !")
            return

        if paint_on_mesh in user_selection[0]:
            pass
        else:
            QtWidgets.QMessageBox.warning(self, "Can't paint :(", "The line you selected is not on the target mesh !")
            return

        stroke_id= len(list(global_scene_data_obj.getGlobalLinesData().keys()))

        polytocurve_result = cmds.polyToCurve(form=3,degree=1)
        polytocurve_curve = polytocurve_result[0]
        polytocurve_node = polytocurve_result[1]

        cmds.select(cl=True)
        cmds.select(polytocurve_curve)

        mel.eval('performSweepMesh 0;')

        #Finding the sweep mesh node:
        sweep_mesh_node = cmds.listConnections( polytocurve_curve + '.worldSpace[0]', d=True, s=False )[0]
        taper_control_node = createTaperController(sweep_mesh_node, line_type="edge", start_scale_value= line_default_scale)

        cmds.addAttr(taper_control_node, at='enum', k=True, en = '______________', shortName='OPTIMIZATION', h=False)
        cmds.setAttr(taper_control_node + '.OPTIMIZATION', lock=True)

        cmds.addAttr(taper_control_node, at='bool', k=True, shortName='disable')


        cmds.select([polytocurve_curve, paint_on_mesh], r=True)
        print(cmds.CreateWrap())
        
        curve_shape = cmds.listRelatives(polytocurve_curve, s=True)[0]
        wrap_node = cmds.listConnections(curve_shape + '.create')[0]

        result_mesh = cmds.listConnections( sweep_mesh_node + '.outMeshArray[0]', d=True, s=False )[0]
        cmds.setAttr(polytocurve_curve + '.v', 0)

        stroke_group= cmds.group([result_mesh, polytocurve_curve], n=f'Stroke_{stroke_id}_grp')
        
        # Node State Connections!!
        # Connect vis to taper ctrl node to reverse to wrap & sweep nodestate
        reverse_state_node= cmds.createNode('reverse')
        cmds.connectAttr(stroke_group + '.v', taper_control_node + '.disable')
        cmds.connectAttr(taper_control_node + '.disable', reverse_state_node + '.inputX')
        cmds.connectAttr(reverse_state_node + '.outputX', wrap_node + '.nodeState')
        cmds.connectAttr(reverse_state_node + '.outputX', sweep_mesh_node + '.nodeState')

        cmds.delete(polytocurve_node)

        


        # Formatting w stroke name
        line_name= f"Stroke_{stroke_id}"
        result_mesh= cmds.rename(result_mesh, f"Stroke_{stroke_id}_msh")
        sweep_mesh_node= cmds.rename(sweep_mesh_node, f"Stroke_{stroke_id}_sweep")
        wrap_node= cmds.rename(wrap_node, f"Stroke_{stroke_id}_wrap")
        converted_curve_shape= cmds.rename(polytocurve_curve, f"Stroke_{stroke_id}_OGcurve")
        taper_control_node= cmds.rename(taper_control_node, f"edit_Stroke_{stroke_id}")
        reverse_state_node= cmds.rename(reverse_state_node, f"reverse_state_Stroke_{stroke_id}")


        line_data= {"name": line_name,
                    "type": "edge",
                    "group": stroke_group,
                    "mesh": result_mesh,
                    "curve": converted_curve_shape,
                    "sweep_msh_node" : sweep_mesh_node,
                    "taper_ctrl_node": taper_control_node,
                    "wrap_node": wrap_node,
                    "root_convert_grp": None,
                    "converted_curve_grp": None,
                    "reverse_state_node": reverse_state_node
                    }
        


        global_scene_data_obj.addLineData(line_data)

        #Automatic shader assignation :
        cmds.select(result_mesh, r=True)
        cmds.hyperShade(assign= detectOrCreateShader())
        cmds.select(cl=True)
        cmds.flushUndo()

        
    def paintLineOnMesh(self):

        global paint_on_mesh
        if not paint_on_mesh:
            QtWidgets.QMessageBox.warning(self, "Can't paint :(", "Please set a target mesh to paint on it !")
            return

        cmds.select(paint_on_mesh)
        mel.eval("MakePaintable")
        mel.eval("PaintEffectsTool")
        
        # Help here ! https://www.regnareb.com/pro/2014/05/wait-for-user-input-in-maya/
        try:
            cmds.dynWireCtx("paintMesh")
        except RuntimeError:
            pass
        cmds.setToolTo("paintMesh")
        # global paint_on_mesh
        # paint_on_mesh = cmds.ls(sl=True)[0]

        # Getting Line default scale if editing was not done:
        self.changeLineDefaultScale()
        self.changeLineResolution()
        self.changeLineSubdivOffset()

        cmds.scriptJob(runOnce=True, event=("SelectionChanged", drawLine))


    def assignPreviewShader(self):
        global cool_lines_shader
        print("Shader:")
        print(cool_lines_shader)

        maya_selection= True

        # Checking if selected from UI or in maya
        user_selection= cmds.ls(sl=True)
        if len(user_selection) == 2:
            for current_item in user_selection:
                if cmds.nodeType(current_item) == "network":
                    maya_selection= False
                else:
                    continue
        
        if not maya_selection:
            cmds.select(self.lines_list_widget.currentItem().data(QtCore.Qt.UserRole)["mesh"])

        cmds.hyperShade(assign= detectOrCreateShader())


class lineListDisplayWidget(QtWidgets.QWidget):
    delete_line_item= QtCore.Signal(QtWidgets.QWidget)

    def __init__(self, line_data :dict, list_item :QtWidgets.QListWidgetItem, *args,**kwargs):
        QtWidgets.QWidget.__init__(self,*args,**kwargs)

        self.line_data= line_data
        self.list_item= list_item

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize) #Mandatory to scale correctly the widget
        self.setLayout(self.main_layout)

        
        self.line_name_widget= CoolNameDisplay(line_data)

        self.line_type_label= QtWidgets.QLabel(self)
        self.line_type_label.setText(self.line_data["type"])
        self.line_type_label.setStyleSheet('''font: 75 7pt "Microsoft YaHei UI";''')

        # Query initial line grp vis!
        current_line_grp_vis= cmds.getAttr(self.line_data["group"] + '.v')
        current_line_grp_vis= bool(current_line_grp_vis)
        
        self.disable_line_checkbox= CoolCheckbox(self)
        self.disable_line_checkbox.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.disable_line_checkbox.setMinimumSize(30,15)
        self.disable_line_checkbox.setMaximumSize(30,15)
        self.disable_line_checkbox.setupAnimations(animation_curve=QtCore.QEasingCurve.OutBounce, animation_duration=300, start_checked= current_line_grp_vis)
        
        trash_icon_path= Path(scene_data.__file__).parent / './_icons/trash_icon.png'
        self.delete_button= CoolImgButton(img_path=trash_icon_path.as_posix(), btn_size= QtCore.QSize(30, 30), img_size=QtCore.QSize(20,20),
                                          bg_color= QtGui.QColor("#CD6C1B"))

        self.main_layout.addWidget(self.line_name_widget)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.disable_line_checkbox)
        self.main_layout.addWidget(self.delete_button)
        self.main_layout.addWidget(self.line_type_label)
        
        self.setStyleSheet('''font: 75 10pt "Microsoft YaHei UI";''')

        # Connections:
        self.line_name_widget.name_changed.connect(self.changeLineNameWrapper)
        self.disable_line_checkbox.stateChanged.connect(self.toggleLineVisibility)
        self.delete_button.clicked.connect(self.requestDelete)


    def changeLineNameWrapper(self, new_name :str):
        
        print(f'New Name: {new_name}')
        if new_name== self.line_data["name"]:
            print("Same name.")
            return
        
        else:
            line_key= self.line_data["name"]
            self.line_data["name"]= new_name #updating the line_data
                   
            # Shared types data rename:
            stroke_group= cmds.rename(self.line_data["group"], f'{new_name}_grp')
            result_mesh= cmds.rename(self.line_data["mesh"], f"{new_name}_msh")
            sweep_mesh_node= cmds.rename(self.line_data["sweep_msh_node"], f"{new_name}_sweep")
            wrap_node= cmds.rename(self.line_data["wrap_node"], f"{new_name}_wrap")
            converted_curve_shape_node= cmds.rename(self.line_data["curve"], f"{new_name}_OGcurve")
            taper_control_node= cmds.rename(self.line_data["taper_ctrl_node"], f"edit_Stroke_{new_name}")
            reverse_state_node= cmds.rename(self.line_data["reverse_state_node"], f"reverse_state_Stroke_{new_name}")

            new_data= {"name": new_name,
                       "type": self.line_data.get("type"),
                        "group": stroke_group,
                        "mesh": result_mesh,
                        "curve": converted_curve_shape_node,
                        "sweep_msh_node" : sweep_mesh_node,
                        "taper_ctrl_node": taper_control_node,
                        "wrap_node": wrap_node,
                        "root_convert_grp": None,
                        "converted_curve_grp": None,
                        "reverse_state_node": reverse_state_node
                        }

            # Unique type data rename:
            if self.line_data["type"] == "paint":

                root_converted_curve_group= cmds.rename(self.line_data["root_convert_grp"], f"{new_name}_keep_grp")
                converted_curve_grp= cmds.rename(self.line_data["converted_curve_grp"], f"{new_name}_OGCuve_grp")

                paint_unique_data={"converted_curve_grp": root_converted_curve_group,
                                   "root_convert_grp": converted_curve_grp,
                                   }
                
                new_data.update(paint_unique_data)
            
            global_scene_data_obj.updateLineData(line_key, dict(new_data), update_name=True)


    def toggleLineVisibility(self):
        current_vis= cmds.getAttr(self.line_data["group"] + '.v')
        cmds.setAttr(self.line_data["group"] + '.v', (not current_vis))


    def requestDelete(self):
        self.list_item.listWidget().setCurrentItem(self.list_item)
        self.delete_line_item.emit(self)



def drawLine():

    cmds.setToolTo( 'moveSuperContext' )

    shape = cmds.listRelatives( cmds.ls(sl=True), fullPath=False, shapes=True)[0]

    if not shape:
        print("Paint operation aborted...")
        return

    if cmds.objectType(shape) == 'stroke':

        print(shape)
        stroke_shape = shape

        # Setting the smooth to max in the stroke shape
        cmds.setAttr(stroke_shape + '.smoothing', 100)


        print ("Stroke Done! Converting...")
        mel.eval("PaintEffectsToCurve;")

        

        global line_default_scale
        start_scale= line_default_scale
        
        #Getting the converted curve:
        converted_curve_transform = cmds.listConnections(stroke_shape + '.outMainCurves[0]', d=True, s=False )[0]
        converted_curve_shape= cmds.listRelatives(converted_curve_transform, s=True)[0]

        # Query spans amount to perform reduction based on user curve res
        converted_curve_spans= cmds.getAttr(converted_curve_shape + '.s')

        cmds.select(converted_curve_transform)
        mel.eval(f'rebuildCurve -ch 1 -rpo 1 -rt 0 -end 1 -kr 0 -kcp 0 -kep 1 -kt 0 -s {int(converted_curve_spans/line_resolution)} -d 1 -tol 0.0001;')
        # Paint on mesh subdiv lvl:
        paint_on_mesh_subdiv_lvl=cmds.getAttr(cmds.listRelatives(paint_on_mesh, s=True)[0] + '.displaySmoothMesh')
        shrinkWrapItem(target_msh= paint_on_mesh, wrapped_item= converted_curve_transform, target_subdiv_lvl= paint_on_mesh_subdiv_lvl)
        
        mel.eval('performSweepMesh 0;')


        sweep_mesh_node = cmds.listConnections( converted_curve_transform + '.worldSpace[0]', d=True, s=False)[0]
        taper_control_node = createTaperController(sweep_mesh_node, line_type="paint", paint_mode=True, start_scale_value=start_scale)

        cmds.addAttr(at='enum', k=True, en = '______________', shortName='OPTIMIZATION', h=False)
        cmds.setAttr(taper_control_node + '.OPTIMIZATION', lock=True)

        cmds.addAttr(at='bool', k=True, shortName='disable')


        result_mesh = cmds.listConnections( sweep_mesh_node + '.outMeshArray[0]', d=True, s=False )[0]
        

        #Organizing(Grouping elements):

        stroke_id= len(list(global_scene_data_obj.getGlobalLinesData().keys()))

        first_group = cmds.listRelatives(converted_curve_transform, p=True)[0]
        root_converted_curve_group = cmds.listRelatives(first_group, p=True)[0]

        stroke_transform = cmds.listRelatives(stroke_shape, p=True)[0]
        cmds.setAttr(stroke_transform + '.v', 0)
        cmds.setAttr(root_converted_curve_group + '.v', 0)

        stroke_group= cmds.group([result_mesh, root_converted_curve_group, stroke_transform], n=f'Stroke_{stroke_id}_grp')

        #Baking:
        stroke_transform = cmds.listRelatives(stroke_shape, p=True)[0]
        cmds.delete(stroke_shape)
        cmds.delete(stroke_transform)


        #Wrapping:
        cmds.select([converted_curve_transform, paint_on_mesh], r=True)
        print(cmds.CreateWrap())

        curve_shape = cmds.listRelatives(converted_curve_transform, s=True)[0]
        wrap_node = cmds.listConnections(curve_shape + '.create')[0]
        

        # Node State Connections!!
        # Connect vis to taper ctrl node to reverse to wrap & sweep nodestate
        reverse_state_node= cmds.createNode('reverse', ss=True)
        cmds.connectAttr(stroke_group + '.v', taper_control_node + '.disable')
        cmds.connectAttr(taper_control_node + '.disable', reverse_state_node + '.inputX')
        cmds.connectAttr(reverse_state_node + '.outputX', wrap_node + '.nodeState')
        cmds.connectAttr(reverse_state_node + '.outputX', sweep_mesh_node + '.nodeState')

        converted_curve_grp= cmds.listRelatives(converted_curve_transform, p=True)[0]
        cmds.select(cl=True)

        # Formatting w stroke name
        line_name= f"Stroke_{stroke_id}"
        result_mesh= cmds.rename(result_mesh, f"Stroke_{stroke_id}_msh")
        sweep_mesh_node= cmds.rename(sweep_mesh_node, f"Stroke_{stroke_id}_sweep")
        wrap_node= cmds.rename(wrap_node, f"Stroke_{stroke_id}_wrap")
        root_converted_curve_group= cmds.rename(root_converted_curve_group, f"Stroke_{stroke_id}_keep_grp")
        converted_curve_transform= cmds.rename(converted_curve_transform, f"Stroke_{stroke_id}_OGcurve")
        converted_curve_grp= cmds.rename(converted_curve_grp, f"Stroke_{stroke_id}_OGCuve_grp")
        taper_control_node= cmds.rename(taper_control_node, f"edit_Stroke_{stroke_id}")
        reverse_state_node= cmds.rename(reverse_state_node, f"reverse_state_Stroke_{stroke_id}")


        line_data= {"name": line_name,
                    "type": "paint",
                    "group": stroke_group,
                    "mesh": result_mesh,
                    "curve": converted_curve_transform,
                    "sweep_msh_node" : sweep_mesh_node,
                    "taper_ctrl_node": taper_control_node,
                    "wrap_node": wrap_node,
                    "root_convert_grp": root_converted_curve_group,
                    "converted_curve_grp": converted_curve_grp,
                    "reverse_state_node": reverse_state_node
                    }
        


        global_scene_data_obj.addLineData(line_data)

        #Automatic shader assignation :
        cmds.select(result_mesh, r=True)
        cmds.hyperShade(assign= detectOrCreateShader())
        cmds.select(cl=True)
        cmds.flushUndo()


def createTaperController(sweep_mesh_node, line_type, paint_mode = False, start_scale_value = 1):
        
    #Create Default taper curve:
    taper_control_node = cmds.createNode('network', n=f'{sweep_mesh_node}_taper_control')

    cmds.addAttr(at='enum', k=True, en = '______________', shortName='GLOBAL', h=False)
    cmds.setAttr(taper_control_node + '.GLOBAL', lock=True)
    cmds.addAttr(at='float', k=True, min=0, shortName='scale_profile')

    cmds.addAttr(at='long', k=True, shortName='rotate_profile')
    cmds.setAttr(taper_control_node + '.rotate_profile', 0)

    cmds.addAttr(at='long', k=True, shortName='resolution', min=1)
    cmds.setAttr(taper_control_node + '.resolution', 4)

    cmds.addAttr(at='long', k=True, shortName='precision')
    cmds.addAttr(at='bool', k=True, shortName='optimize_precision')

    if line_type== "paint":
        cmds.setAttr(sweep_mesh_node + '.interpolationMode', 0)
        cmds.setAttr(taper_control_node + '.precision', 100)
        default_interpolation_precision= 100
        
    elif line_type== "edge":
        cmds.setAttr(sweep_mesh_node + '.interpolationMode', 0)
        default_interpolation_precision= 75
       
    cmds.setAttr(taper_control_node + '.precision', default_interpolation_precision)
    cmds.setAttr(taper_control_node + '.optimize_precision', 1)

    cmds.connectAttr(taper_control_node + '.precision', sweep_mesh_node + '.interpolationPrecision')
    cmds.connectAttr(taper_control_node + '.optimize_precision', sweep_mesh_node + '.interpolationOptimize')

    cmds.addAttr(at='enum', k=True, en = '______________', shortName='POINTS', h=False)
    cmds.setAttr(taper_control_node + '.POINTS', lock=True)
    cmds.addAttr(at='float', k=True, shortName='START_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='START_value')
    cmds.addAttr(at='float', k=True, shortName='point1_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='point1_value')
    cmds.addAttr(at='enum', k=True, en = 'None:Linear:Smooth:Spline', shortName='point1_interp')
    cmds.addAttr(at='float', k=True, shortName='point2_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='point2_value')
    cmds.addAttr(at='enum', k=True, en = 'None:Linear:Smooth:Spline', shortName='point2_interp')
    cmds.addAttr(at='float', k=True, shortName='point3_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='point3_value')       
    cmds.addAttr(at='enum', k=True, en = 'None:Linear:Smooth:Spline', shortName='point3_interp')    
    cmds.addAttr(at='float', k=True, min=0, shortName='END_position') 
    cmds.addAttr(at='float', k=True, min=0, shortName='END_value')
    


    cmds.setAttr(taper_control_node + '.scale_profile', 1)

    cmds.setAttr(taper_control_node + '.END_position', 1)
    cmds.setAttr(taper_control_node + '.point1_position', 0.2)
    cmds.setAttr(taper_control_node + '.point2_position', 0.5)
    cmds.setAttr(taper_control_node + '.point3_position', 0.8)

    cmds.setAttr(taper_control_node + '.point1_value', 1)
    cmds.setAttr(taper_control_node + '.point2_value', 1)
    cmds.setAttr(taper_control_node + '.point3_value', 1)

    cmds.setAttr(taper_control_node + '.point1_interp', 1)
    cmds.setAttr(taper_control_node + '.point2_interp', 1)
    cmds.setAttr(taper_control_node + '.point3_interp', 1)


    cmds.connectAttr(taper_control_node + '.scale_profile', sweep_mesh_node + '.scaleProfileX')
    cmds.connectAttr(taper_control_node + '.rotate_profile', sweep_mesh_node + '.rotateProfile')
    cmds.connectAttr(taper_control_node + '.resolution', sweep_mesh_node + '.profilePolySides')

    cmds.connectAttr(taper_control_node + '.START_position', sweep_mesh_node + '.taperCurve[0].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.START_value', sweep_mesh_node + '.taperCurve[0].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.END_position', sweep_mesh_node + '.taperCurve[1].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.END_value', sweep_mesh_node + '.taperCurve[1].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.point1_position', sweep_mesh_node + '.taperCurve[2].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.point1_interp', sweep_mesh_node + '.taperCurve[2].taperCurve_Interp')
    cmds.connectAttr(taper_control_node + '.point1_value', sweep_mesh_node + '.taperCurve[2].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.point2_position', sweep_mesh_node + '.taperCurve[3].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.point2_interp', sweep_mesh_node + '.taperCurve[3].taperCurve_Interp')
    cmds.connectAttr(taper_control_node + '.point2_value', sweep_mesh_node + '.taperCurve[3].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.point3_position', sweep_mesh_node + '.taperCurve[4].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.point3_interp', sweep_mesh_node + '.taperCurve[4].taperCurve_Interp')
    cmds.connectAttr(taper_control_node + '.point3_value', sweep_mesh_node + '.taperCurve[4].taperCurve_FloatValue')


    #Setting the start scale value :
    cmds.setAttr(taper_control_node + '.scale_profile', start_scale_value)

    return taper_control_node


def shrinkWrapItem(target_msh, wrapped_item, target_subdiv_lvl= 0):
    
    if target_subdiv_lvl > 0:
        pass
    else:
        return
    
    shrinkwrap_deformer = cmds.deformer(wrapped_item, type='shrinkWrap')[0] #Applying the shrinkwrap on the object
    
    print(shrinkwrap_deformer)
    #Creating the necessary connections:
    target_msh_shape = cmds.listRelatives(target_msh, s=True)[0] #Gathering the sphere's shape

    #cmds.connectAttr(sphere_geo_shape + '.', shrinkwrap_deformer + '.')
    cmds.connectAttr(target_msh_shape + '.boundaryRule', shrinkwrap_deformer + '.boundaryRule')
    cmds.connectAttr(target_msh_shape + '.continuity', shrinkwrap_deformer + '.continuity')
    cmds.connectAttr(target_msh_shape + '.keepBorder', shrinkwrap_deformer + '.keepBorder')
    cmds.connectAttr(target_msh_shape + '.keepHardEdge', shrinkwrap_deformer + '.keepHardEdge')
    cmds.connectAttr(target_msh_shape + '.keepMapBorders', shrinkwrap_deformer + '.keepMapBorders')
    #cmds.connectAttr(sphere_geo_shape + '.propagateHardness', shrinkwrap_deformer + '.propagateHardness')
    cmds.connectAttr(target_msh_shape + '.smoothUVs', shrinkwrap_deformer + '.smoothUVs')
    cmds.connectAttr(target_msh_shape + '.worldMesh[0]', shrinkwrap_deformer + '.targetGeom')


    #Setting attributes:
    cmds.setAttr(shrinkwrap_deformer + '.prj', 4)
    cmds.setAttr(shrinkwrap_deformer + '.bi', 1)
    cmds.setAttr(shrinkwrap_deformer + '.offset', line_subdiv_offset)
    cmds.setAttr(shrinkwrap_deformer + '.targetSmoothLevel', 3) # 1 start index for this attr

    cmds.select(wrapped_item, r=True)
    mel.eval("DeleteHistory;")
    

def bakeAllLines():
    global_line_data= global_scene_data_obj.getGlobalLinesData()
    cmds.select(cl=True)

    lines_meshes_list= []
    lines_grps_list= []
    # Select All
    for current_line_name in list(global_line_data.keys()):
        current_line_data= global_line_data[current_line_name]
        lines_meshes_list.append(current_line_data["mesh"])
        lines_grps_list.append(current_line_data["group"])


    if cmds.objExists("_BakedLines_grp"):
        bake_grp= "_BakedLines_grp"
    else:
        bake_grp= cmds.group(em=True, n="_BakedLines_grp")

    cmds.select(cl=True)
    cmds.select(lines_meshes_list, r=True)
    mel.eval("DeleteHistory;")

    cmds.parent(lines_meshes_list, bake_grp)
    cmds.delete(lines_grps_list)

    for current_mesh in lines_meshes_list: 
        cmds.rename(current_mesh, f"baked_{current_mesh}") # Prevent name dupes


    global_scene_data_obj.clearGlobalLinesData()
    


if __name__ == '__main__':
    detectOrCreateShader()
    main_window_instance= DockableWindow()
    main_window_instance.show(dockable=True)