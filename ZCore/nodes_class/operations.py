from PySide2 import QtCore,QtWidgets,QtGui
from ZCore.Config import *

import GUI.node_content as node_content
import ZCore.NodeBase as NodeBase
import ZCore.ToolsSystem as ToolsSystem

class ZenoOperationsContent(node_content.NodeContentWidget):
    def initUI(self):
        self.input1 = QtWidgets.QLabel("Input 1", self)
        self.input2 = QtWidgets.QLabel("Input 2", self)
        self.addWidgetToLayout([self.input1, self.input2])

@register_node(OP_NODE_ADD)
class ZenoNode_Add(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","add.png")
    op_code = OP_NODE_ADD
    op_title = "Add"
    content_label_objname = "zeno_node_add"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Add, self).__init__(self.__class__.op_title, scene, "math", inputs=[1,1],outputs=[1])    # call init function, cuz this node use custom socket config

    def initInnerClasses(self):
        self.content = ZenoOperationsContent(self)
        self.node_graphic = NodeBase.ZenoNodeGraphics(self, self.validateIcon(self.icon))

    def evalOperation(self, input1, input2):
        return input1 + input2
    
@register_node(OP_NODE_SUBTRACT)
class ZenoNode_Subtract(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","sub.png")
    op_code = OP_NODE_SUBTRACT
    op_title = "Subtract"
    content_label_objname = "zeno_node_subtract"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Subtract, self).__init__(self.__class__.op_title, scene, "math", inputs=[1,1], outputs=[1])    # call init function, cuz this node use custom socket config

    def initInnerClasses(self):
        self.content = ZenoOperationsContent(self)
        self.node_graphic = NodeBase.ZenoNodeGraphics(self, self.validateIcon(self.icon))

    def evalOperation(self, input1, input2):
        return input1 - input2
    
@register_node(OP_NODE_MULTIPLY)
class ZenoNode_Multiply(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","mul.png")
    op_code = OP_NODE_MULTIPLY
    op_title = "Multiply"
    content_label_objname = "zeno_node_multi"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Multiply, self).__init__(self.__class__.op_title, scene, "math", inputs=[1,1], outputs=[1])    # call init function, cuz this node use custom socket config

    def initInnerClasses(self):
        self.content = ZenoOperationsContent(self)
        self.node_graphic = NodeBase.ZenoNodeGraphics(self, self.validateIcon(self.icon))

    def evalOperation(self, input1, input2):
        return input1 * input2
    
@register_node(OP_NODE_DIVIDE)
class ZenoNode_Divide(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","divide.png")
    op_code = OP_NODE_DIVIDE
    op_title = "Divide"
    content_label_objname = "zeno_node_divide"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Divide, self).__init__(self.__class__.op_title, scene, "math", inputs=[1,1], outputs=[1])    # call init function, cuz this node use custom socket config

    def initInnerClasses(self):
        self.content = ZenoOperationsContent(self)
        self.node_graphic = NodeBase.ZenoNodeGraphics(self, self.validateIcon(self.icon))

    def evalOperation(self, input1, input2):
        return input1 / input2