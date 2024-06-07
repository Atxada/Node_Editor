from ZCore.Shelf.context_build import *

import ZCore.ShelfBase as ShelfBase

class tes3_item(ShelfBase.GraphicButton):
    def __init__(self, app=None):

        super(tes3_item, self).__init__()
        self.app = app

    def onClick(self, event):
        self.app.outputLogInfo("tes3")

item_class = tes3_item