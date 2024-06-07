"""this module will automatically register necessary component whenever imported to other module"""

import json
import os

class ConfException(Exception): pass
class InvalidRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass

#-------------------------------------------------------------------------------------
#--------------------------------------- Nodes --------------------------------------- 
#-------------------------------------------------------------------------------------

LISTBOX_MIMETYPE = "application/x-item"

# Change UI ordering by changing the value (factor default)
OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_SPLINE = 3
OP_NODE_ADD = 4
OP_NODE_SUBTRACT = 5
OP_NODE_MULTIPLY = 6
OP_NODE_DIVIDE = 7

# List of all nodes available
ZENO_NODES = {}
NODES_NAME = {} # list node name as key

def register_node_now(op_code, class_reference):
    if op_code in ZENO_NODES:
        raise InvalidRegistration("Duplicate node registration of '%s'. There is already %s" 
                                      %(op_code, ZENO_NODES[op_code]))
    ZENO_NODES[op_code] = class_reference
    NODES_NAME[class_reference.op_title] = op_code

def register_node(op_code):    # this function called automatically with passed argumnet from whatever under @register_node decorator, weird...
    def decorator(original_class):  # this nested function add extra functionality when register node called, think as it's the syntax u must follow
        register_node_now(op_code, original_class)  # your custom action when this decorator called
        return original_class                       # return this is a must, to preserve the class/function's behavior underneath this decorator
    return decorator                                # return this decorator to execute it according to https://www.youtube.com/watch?v=MYAEv3JoenI

def get_class_from_opcode(op_code):
    if op_code not in ZENO_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return ZENO_NODES[op_code]

# import all nodes and trigger automatic registration
from ZCore.nodes_class import *

#-------------------------------------------------------------------------------------
#--------------------------------------- Shelf --------------------------------------- 
#-------------------------------------------------------------------------------------
"""
SHELF_FACTORY_ORDER = ["Context", "Tools"]  # control shelf order, name and validity (anything beside this name will be ignored, even tho it's found under shelf)
SHELF_TAB_CLASS = {}  # shelf_title : item class list

# get all module item inside shelf folder's sub-directory, only include directory specify by shelf_factory_order 
for subDir in os.walk(SHELF_DIR):
    if os.path.basename(subDir[0]) in SHELF_FACTORY_ORDER: 
        shelf_title = (os.path.basename(subDir[0]))
        if shelf_title in SHELF_TAB_CLASS.keys(): raise InvalidRegistration("Duplicate shelf registration of '%s'. There is already %s" %(shelf_title))
        shelf_item_module = [item for item in subDir[2] if not item == "__init__.py" and item[-3:] == ".py"]
        item_class = []
        for module in shelf_item_module:
            spec = importlib.util.spec_from_file_location(module, SHELF_DIR+"/%s/%s"%(shelf_title, module))
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            item_class.append(foo.item_class)
        SHELF_TAB_CLASS[shelf_title] = item_class

# initalize it according to shelf factor order list, passing the app, 1 time process
def init_tab_widget(app):
    tab_widget_list = []
    for title in SHELF_FACTORY_ORDER:
        tab_widget = ShelfBase.ZenoTabContainer()
        for shelf_item in SHELF_TAB_CLASS[title]:
            tab_widget.itemLayout.addWidget(shelf_item(app))
        tab_widget_list.append(tab_widget)
    return tab_widget_list

"""
OP_TAB_CONTEXT = 1
OP_TAB_TOOLS = 2
SHELF_TAB = {}

def register_tab_now(op_code, class_reference):
    if op_code in SHELF_TAB:
        raise InvalidRegistration("Duplicate tab registration of '%s'. There is already %s"
                                    %(op_code, SHELF_TAB[op_code]))
    SHELF_TAB[op_code] = class_reference

def register_tab(op_code):
    def decorator(original_class):
        register_tab_now(op_code, original_class)
        return original_class
    return decorator

def get_tab_from_opcode(op_code):
    if op_code not in SHELF_TAB: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return SHELF_TAB[op_code]

# import all tabs and trigger automatic registration
from ZCore.Shelf import *