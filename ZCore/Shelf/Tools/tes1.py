from ZCore.Shelf.context_build import *

import ZCore.ShelfBase as ShelfBase

class tes1_item(ShelfBase.GraphicButton):
    def __init__(self, app=None):

        super(tes1_item, self).__init__()
        self.app = app

    def onClick(self, event):
        self.app.outputLogInfo("tes1")

item_class = tes1_item