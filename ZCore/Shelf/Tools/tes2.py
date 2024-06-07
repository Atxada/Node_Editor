from ZCore.Shelf.context_build import *

import ZCore.ShelfBase as ShelfBase

class tes2_item(ShelfBase.GraphicButton):
    def __init__(self, app=None):

        super(tes2_item, self).__init__()
        self.app = app

    def onClick(self, event):
        self.app.outputLogInfo("tes2")

item_class = tes2_item