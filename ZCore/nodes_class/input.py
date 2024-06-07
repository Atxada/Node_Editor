from PySide2 import QtCore,QtWidgets,QtGui
from ZCore.Config import *  # with import it's cuz error, looping problem?

import GUI.node_content as node_content
import ZCore.NodeBase as NodeBase
import ZCore.ToolsSystem as ToolsSystem

class ZenoInputContent(node_content.NodeContentWidget):
    def initUI(self):
        self.edit = QtWidgets.QLineEdit("1", self)
        self.edit.setAlignment(QtCore.Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)
        self.edit.setStyleSheet("background: #303030; max-height: 17.5; margin-left: 5px; margin-top: 1.25")

    def serialize(self):    # serialize because there is content inside (line edit)
        res = super(ZenoInputContent,self).serialize()
        res['value'] = self.edit.text()
        return res
    
    def deserialize(self, data, hashmap=[]):   # deserialize because there is content inside (line edit)
        res = super(ZenoInputContent, self).deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res   # idk what & difference with ,
        except Exception as e: pass
        return res

@register_node(OP_NODE_INPUT)
class ZenoNode_Input(NodeBase.ZenoNode):
    icon = ToolsSystem.get_path("Sources","icons","node","in.png")
    op_code = OP_NODE_INPUT
    op_title = "Input"
    content_label = "in"
    content_label_objname = "zeno_node_input"

    def __init__(self, nameID=op_title, scene=None):
        super(ZenoNode_Input, self).__init__(self.__class__.op_title, scene, "evaluation", inputs=[], outputs=[1])    # call init function, cuz this node use custom socket config
        self.eval()

    def initInnerClasses(self): # append custom class to node content
        self.content = ZenoInputContent(self)
        self.node_graphic = NodeBase.ZenoNodeGraphics(self, self.validateIcon(self.icon))
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        unsaved_value = self.content.edit.text()
        saved_value = int(unsaved_value)    # checking if line edit contain correct type(interger)
        self.value = saved_value
        # if everything goes well, pass success evaluation
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.node_graphic.setToolTip("")    # if everything ok, make sure tool tip empty (no warning)

        self.evalChildren()

        return self.value