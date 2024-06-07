from ZCore.Shelf.context_build import *
from ZCore.ToolsSystem import OUTPUT_INFO, OUTPUT_ERROR, OUTPUT_SUCCESS, OUTPUT_WARNING

import ZCore.ShelfBase as ShelfBase
import ZCore.ToolsSystem as ToolsSystem
import maya.cmds as cmds

@register_item(OP_ITEM_SPLINE)
class spline(ShelfBase.GraphicButton):
    plugin = ToolsSystem.get_path("SplineCtx.py")
    icon = ToolsSystem.get_path("Sources","icons","shelf","context","spline.png")
    def __init__(self, app=None):

        super(spline, self).__init__(self.icon)
        self.app = app

        # plugin (use context via cmds module after load plugin, must match with corresponding command name)
        cmds.loadPlugin(self.plugin)
        self.context = cmds.zSplineCtx()    

    def onClick(self, event):
        if self.app.getCurrentNodeEditorWidget():
            try: cmds.setToolTo(self.context)
            except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)
        else:
            self.app.outputLogInfo("no graphic scene found", OUTPUT_ERROR)