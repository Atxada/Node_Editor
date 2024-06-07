from ZCore.Config import *

import ZCore.ShelfBase as ShelfBase

# item order (factory default)
OP_ITEM_SPLINE = 1

SHELF_ITEM = {}

def register_item_now(op_code, class_reference):
    if op_code in SHELF_ITEM:
        raise InvalidRegistration("Duplicate item registration of '%s'. There is already %s"%(op_code, SHELF_ITEM[op_code]))
    SHELF_ITEM[op_code] = class_reference

def register_item(op_code):
    def decorator(original_class):
        register_item_now(op_code, original_class)
        return original_class
    return decorator

# import all item and trigger automatic registration
from ZCore.Shelf.Context import *

@ register_tab(OP_TAB_CONTEXT)
class ZenoTab_Context(ShelfBase.ZenoTabContainer):
    title = "Context"

    def __init__(self, app):
        super(ZenoTab_Context, self).__init__(app)

        self.app = app

        self.initItem()

    def initItem(self):
        keys = list(SHELF_ITEM.keys())
        keys.sort()
        for key in keys:
            self.itemLayout.addWidget(SHELF_ITEM[key](self.app))