from PySide2 import QtCore,QtWidgets,QtGui
from ZCore.Config import *

import GUI.node_content as node_content
import ZCore.NodeBase as NodeBase
import ZCore.ToolsSystem as ToolsSystem

@register_node(OP_NODE_SPLINE)
class ZenoNode_Spline(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","spline.png")
    op_code = OP_NODE_SPLINE
    op_title = "ZSpline"
    content_label = "read-only"
    content_label_objname = "zeno_node_spline"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Spline, self).__init__(nameID, scene, inputs=[2], outputs=[])    # call init function, cuz this node use custom socket config

    def evalImplementation(self):
        self.markInvalid(False)
        self.markDirty(False)
        return 123