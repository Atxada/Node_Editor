from PySide2 import QtCore,QtWidgets,QtGui
from ZCore.Config import *

import GUI.node_content as node_content
import ZCore.NodeBase as NodeBase
import ZCore.ToolsSystem as ToolsSystem

class ZenoOutputContent(node_content.NodeContentWidget):
    def initUI(self):
        self.label = QtWidgets.QLabel("Result: ", self)
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.label.setObjectName(self.node.content_label_objname)
        self.label.setStyleSheet("margin-left: 5px; margin-top: 5px;")
        self.label.setMinimumWidth(140)  # hypothetical

@register_node(OP_NODE_OUTPUT)
class ZenoNode_Output(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","out.png")
    op_code = OP_NODE_OUTPUT
    op_title = "Output"
    content_label = "out"
    content_label_objname = "zeno_node_output"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Output, self).__init__(self.__class__.op_title, scene, "evaluation", inputs=[1], outputs=[])    # call init function, cuz this node use custom socket config

    def initInnerClasses(self): # append custom class to node content
        self.content = ZenoOutputContent(self)
        self.node_graphic = NodeBase.ZenoNodeGraphics(self, self.validateIcon(self.icon))

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.node_graphic.setToolTip("Input is not connected") 
            self.markInvalid()
            return
        
        value = input_node.eval()
        if value is None:
            self.node_graphic.setToolTip("Input is NaN")    # NaN -> not a number
            self.markInvalid()
            return
        self.content.label.setText("Result: %d"%value)
        self.markInvalid(False)
        self.markDirty(False)
        self.node_graphic.setToolTip("")
        
        return value