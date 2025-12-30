# -*- coding: utf-8 -*-
"""
Cool Lines! — Installer

----------

version 1.00    --/--/----

Author: Victor Schenck
Email: -
Created: 2025
"""
from pathlib import Path
from maya import cmds

def onMayaDroppedPythonFile(*args):

    current_path= Path(__file__)
    install_folder_path= current_path.parent
    main_file_path= install_folder_path / './cool_lines.py'

    with open(main_file_path.as_posix(), 'r') as file:

        cool_lines_script= file.read()
        shelf_payload= cool_lines_script.replace("INSTALLATION_PATH_REPLACE_STRING", install_folder_path.as_posix()) #"replace('\\', '/')"


    #Creating shelf button:
    current_shelf_tab = cmds.tabLayout("ShelfLayout", query=True, selectTab=True)
    cmds.shelfButton(parent=current_shelf_tab, imageOverlayLabel="Cool Lines", annotation='Launch Cool Lines :)', image1='paintEffectsTool.png', command=shelf_payload )