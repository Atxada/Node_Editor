from ZCore.Config import *

import ZCore.ShelfBase as ShelfBase

@ register_tab(OP_TAB_TOOLS)
class ZenoTab_Tools(ShelfBase.ZenoTabContainer):
    title = "Tools"

    def __init__(self, parent=None):
        super(ZenoTab_Tools, self).__init__(parent)