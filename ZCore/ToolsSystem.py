""" This Module containing helper function to bridge between maya to ZenoRig or ZenoRig to operating system """
import os
import maya.cmds as cmds

"""
Python 2 Caveat 
-still use old class, pyside2 need new style class for multiple inheritance
-setter getter required object inheritanced
-decodeError exception from json not available
-not support unpacking list (*args)
-not support copy list operation python (2.x till 3.3)
"""

'''
function: 
- initiate the whole ecosystem for the tools
- store all name for each created rig nodes
- first safeguard when create rig nodes
- contains couple specific function for rig nodes
'''

#------------------------------------------ NODE EDITOR ------------------------------------------#
zeno_window = None

#------------------------------------------- NODE DATA -------------------------------------------#
spline_node = [] # def > object store points and connected spline (Type : Structs)
NODE_TYPE = [0,0,0,spline_node]

#--------------------------------------- NODE DEFAULT NAME ---------------------------------------#
SPLINE_DEF_NAME = "zSpline"
NODE_NAME = [0,0,0,SPLINE_DEF_NAME]

#------------------------------------------ RUNTIME DATA -----------------------------------------#
live_mesh = []

#---------------------------------------- SYSTEM CONSTANT ----------------------------------------#
SETUP_GRP_NAME = "setupGrp"

#---------------------------------------- DIRECTORY PATH -----------------------------------------#
""" This can be temporary as os.path can't detect __file__ when using python shell, development only"""
ZCORE_DIR = os.path.dirname(os.path.realpath(__file__))

#---------------------------------------- OUTPUT LOG ENUM ----------------------------------------#
# output log color coded
OUTPUT_INFO = 0
OUTPUT_SUCCESS = 1
OUTPUT_WARNING = 2
OUTPUT_ERROR = 3

# return zcore directory if no argument passed
def get_path(*args):
    path = ZCORE_DIR
    for arg in args:
        path = os.path.join(path, arg)
    if os.path.exists(path):
        return path
    else:
        return False

# function search if setup group present and parent it, if setup group not present create one
# (obj = grp/node to parent to setup)
def parent_setup(obj):
    if cmds.objExists(SETUP_GRP_NAME):
        cmds.parent(obj, SETUP_GRP_NAME)
    else:
        cmds.group(n=SETUP_GRP_NAME, em=1)
        cmds.parent(obj,SETUP_GRP_NAME)

# Note: nameID always unique, name argument is a suggested nameID. if name unique, name and nameID can be the same
# (index = index {refer to ToolsSystem.NODE_TYPE}, name = "customName")
def generate_nameID(index, name=""):
    suffix = 1
    if not name: 
        name = NODE_NAME[index]
        while (name+str(suffix)) in NODE_TYPE[index] or cmds.objExists(name+str(suffix)):
            suffix+=1
        nameID = name + str(suffix)
    else:
        if name in NODE_TYPE[index] or cmds.objExists(name):
            while (name+str(suffix)) in NODE_TYPE[index] or cmds.objExists(name+str(suffix)):
                suffix+=1
            nameID = name + str(suffix)
    NODE_TYPE[index].append(nameID)
    generate_node(index, nameID)
    return nameID

# (index = index {refer to ToolsSystem.NODE_TYPE}, nameID = object unique id)
def generate_node(index, nameID):
    if zeno_window and zeno_window.getCurrentNodeEditorWidget():    # remember if u switch and statement it will emit error cuz if zeno_window none, none has no given attribute
        node_editor = zeno_window.getCurrentNodeEditorWidget()
        node_editor.addNode(index, nameID)

def rename_name(index, new_name):
    '''
    TO DO: check if name exist, if so add sufix (like get unique id)
    '''

def store_data():
    pass

def load_data():
    pass

# ZCore_dir = "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig/ZCore/"
# ZCore_curves_dir = "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig/ZCore/Sources/ControlCurves"
# ZCore_save_dir = "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig/ZCore/Save/"
# ZCore_icon_dir = "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig/ZCore/Sources/icons/"
# ZCore_shelf_dir = "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig/ZCore/Shelf/"
# ZCore_user_script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'Shelf','userPref.json')