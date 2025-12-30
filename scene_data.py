# -*- coding: utf-8 -*-
"""
Cool Lines! — Data scene file

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
import json
from maya import cmds
import pprint

from ui.pyside_compat import QtCore


class GlobalSceneData(QtCore.QObject):
    request_ui_sync = QtCore.Signal()
    request_ui_clear = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(GlobalSceneData, self).__init__()

        self.global_lines_data = {}
        self.scene_data_node = None
        self.scene_data_node_default_name = 'CoolLines_SceneData'

        self.checkSceneDataNode()

    def checkSceneDataNode(self):

        if cmds.objExists(self.scene_data_node_default_name):
            print('SceneDataNode found!')
            self.scene_data_node = self.scene_data_node_default_name
            self.loadSceneData()
            return True

        else:
            print('Cant find data! Creating a new node so you can draw... :)')
            self.createSceneDataNode()
            return False

    def createSceneDataNode(self):
        # Create Node to store data. Data will be empty at first.
        self.scene_data_node = cmds.scriptNode(st=0, bs='', n=self.scene_data_node_default_name, stp='python')

    def addLineData(self, line_data):
        self.global_lines_data[line_data["name"]] = line_data
        self.request_ui_sync.emit()
        self.saveSceneData()

    def getGlobalLinesData(self):
        return self.global_lines_data

    def removeLineData(self, line_key):
        self.global_lines_data.pop(line_key)
        self.saveSceneData()
        self.request_ui_sync.emit()

    def clearGlobalLinesData(self):
        self.global_lines_data.clear()
        self.saveSceneData()
        self.request_ui_clear.emit()

    def updateLineData(self, line_key, new_line_data, update_name=False):

        print('*********')
        print('Updating Line Data:')

        if update_name:
            self.global_lines_data.pop(line_key)
            self.global_lines_data[new_line_data["name"]] = new_line_data
            pprint.pprint(self.global_lines_data[new_line_data["name"]])

        else:
            self.global_lines_data[line_key] = new_line_data
            pprint.pprint(self.global_lines_data[line_key])

        self.saveSceneData()
        self.request_ui_sync.emit()

    def saveSceneData(self):
        # Dump data to node:
        if self.scene_data_node:
            cmds.scriptNode(self.scene_data_node, e=True, bs=json.dumps(self.global_lines_data))
        else:
            cmds.error("Cannot save scene data because there is no scene data node..")

    def loadSceneData(self):
        # Attempt Loading data from node:
        if self.scene_data_node:
            scene_data_str = cmds.scriptNode(self.scene_data_node, q=True, bs=True)
        else:
            cmds.error("Cannot load scene data because there is no scene data node..")
            return

        if scene_data_str:
            scene_data = json.loads(scene_data_str)

            print('******************')
            print('Loaded Data:')
            print(scene_data)

            self.rebuildData(scene_data)
            self.request_ui_sync.emit()
        else:
            print("Skipping loading, data empty !")
            self.global_lines_data.clear()
            self.request_ui_clear.emit()

    def rebuildData(self, scene_data):

        for current_line_name in list(scene_data.keys()):
            # Safe data rebuilding:
            if cmds.objExists(scene_data[current_line_name]["group"]):
                self.global_lines_data[current_line_name] = dict(scene_data[current_line_name])
            else:
                print(f"Cannot find {current_line_name}'s Data ! Removing...")

        print('Data rebuilt successfully')
        self.saveSceneData()

    def detectSceneChange(self):

        # A new scene has been opened..
        if self.checkSceneDataNode():
            pass
        else:
            self.global_lines_data.clear()  # if create new scene while script still opened
            self.request_ui_clear.emit()