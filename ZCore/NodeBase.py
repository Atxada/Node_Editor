from PySide2 import QtCore,QtWidgets,QtGui

import GUI.node_creator as node_creator
import GUI.node_content as node_content

import ZCore.ToolsSystem as ToolsSystem

DEBUG = False

NODE_COLORS = {
    "math" : QtGui.QColor("#303030"),
    "evaluation" : QtGui.QColor("#912130"),
    "unknown" :  QtGui.QColor("#454545"),
}

class ZenoNodeGraphics(node_creator.NodeGraphics):
    def __init__(self, node, icon="", parent=None):
        super(ZenoNodeGraphics, self).__init__(node, parent)
        self.icon = icon

    @property
    def node_type(self):
        return self.node.node_type
    
    def getNodeHeaderColor(self, key):
        try: return NODE_COLORS[key]
        except: return NODE_COLORS["unknown"]

    def initSizes(self):
        super(ZenoNodeGraphics, self).initSizes()
        self.width = 160
        self.edge_roundness = 5
        self.edge_padding = 0 # feels like edge padding is edge/outline width
        self.title_height = 20
        self.title_horizontal_padding = 5
        self.title_vertical_padding = 10
        
        # calculate node height from input and output amount
        self.height = self.title_height + (self.node.segment_amount*self.node.socket_spacing) + (self.node.socket_spacing/4)

    def initAsset(self):
        super(ZenoNodeGraphics, self).initAsset()
        self._title_font = QtGui.QFont("Ubuntu", 8)
        self._brush_title = QtGui.QBrush(self.getNodeHeaderColor(self.node_type))
        self._brush_background = QtGui.QBrush(QtGui.QColor("#4b4c51"))
        self._brush_segment = QtGui.QBrush(QtGui.QColor("#595b61")) 
        self._invalid_icon = QtGui.QImage(ToolsSystem.get_path("Sources","icons","node","invalid.png"))

    def initTitle(self):
        super(ZenoNodeGraphics, self).initTitle()
        self.title_item.setPos(self.title_horizontal_padding, -3)

    def paint(self, painter, option, widget):
        '''
        self._brush_title = QtGui.QBrush(QtGui.QColor("#6db463"))
        if self.node.isDirty():
            self._brush_title = QtGui.QBrush(QtGui.QColor("#bbbb4c"))
        if self.node.isInvalid():
            self._brush_title = QtGui.QBrush(QtGui.QColor("#de6e5b"))
        '''

        super(ZenoNodeGraphics, self).paint(painter, option, widget)

        # draw node icon
        painter.drawImage(                    
            QtCore.QRectF(self.width-self.title_horizontal_padding-20, 2.5, 15, 15),
            self.icon,
            QtCore.QRectF(0, 0, 32, 32)
        )

        # draw warning if node is invalid
        if self.node.isInvalid():
            painter.drawImage(
                QtCore.QRectF(-14, -14, 24, 24),
                self._invalid_icon,
                QtCore.QRectF(0, 0, 64, 64)
            )
    
class ZenoNodeContent(node_content.NodeContentWidget):
    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

class ZenoNode(node_creator.NodeConfig):
    icon = ""
    op_code = 0
    op_title = "undefined"
    content_label = ""
    content_label_objname = "zeno_node_bg"

    GraphicNode_class = ZenoNodeGraphics
    NodeContent_class = ZenoNodeContent

    def __init__(self, title=op_title, scene=None, node_type="unknown", inputs=[1,1], outputs=[2]):
        self.node_type = node_type
        super(ZenoNode, self).__init__(title, scene, inputs, outputs) # self.__class__ will access instance from derived class 
        
        self.value = None

        # mark node dirty by default, cuz it's needed to be used/evaluated
        self.markDirty()

    def initInnerClasses(self):
        """Sets up graphics Node and Content Widget"""
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None: self.content = node_content_class(self)
        if graphics_node_class is not None: self.node_graphic = graphics_node_class(self, self.validateIcon(self.icon))

    def initSettings(self):
        super(ZenoNode, self).initSettings()
        self.input_socket_position = node_creator.LEFT_TOP
        self.output_socket_position = node_creator.RIGHT_TOP

    def validateIcon(self, icon):
        if icon == "" or QtGui.QImageReader.canRead(QtGui.QImageReader(icon))==False:    # check if icon not valid, replace with template icon if true
            return ToolsSystem.get_path("Sources","icons","node","python.png")
        return icon

    def evalOperation(self, input1, input2):
        return 1

    def evalImplementation(self):
        # this is where derived class/nodes will implement it's custom evaluation
        input1 = self.getInput(0)
        input2 = self.getInput(1)

        if input1 is None or input2 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.node_graphic.setToolTip("Connect all inputs")
            return None
        
        else:
            value = self.evalOperation(input1.eval(), input2.eval())
            self.value = value
            self.markDirty(False)
            self.markInvalid(False)
            self.node_graphic.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return value

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            if DEBUG: print("_> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value
        
        try:
            value = self.evalImplementation()
            return value
        except ValueError as e:
            self.markInvalid()
            self.node_graphic.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.node_graphic.setToolTip(str(e))
            if DEBUG: print("Node Eval::", e)

    def onInputChanged(self, socket=None):
        if DEBUG: print("%s::__onInputChanged"% self.__class__.__name__)
        self.markDirty()
        self.eval()

    def serialize(self):
        res = super(ZenoNode, self).serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap=[], restore_id=True):
        res = super(ZenoNode, self).deserialize(data, hashmap, restore_id)
        if DEBUG: print('Deserialized zenoNode "%s"'% self.__class__.__name__, "res:", res)
        return res

"""  
class ZenoNodeIcon(QtWidgets.QLabel):
    def __init__(self, icon="", size=(32,32), parent=None):
        super(ZenoNodeIcon, self).__init__(parent)

        self.icon = icon
        self.size = size

        self.initUI()

    def initUI(self):
        self.icon_validator = QtGui.QImageReader(self.icon)
        if QtGui.QImageReader.canRead(self.icon_validator):
            self.item_image = QtGui.QImage(self.icon)
        else:
            self.item_image = QtGui.QImage(ToolsSystem.get_path("Sources","icons","shelf","python.png"))

        self.item_image = self.item_image.scaled(self.size[0],self.size[1],QtCore.Qt.IgnoreAspectRatio,QtCore.Qt.SmoothTransformation)
        self.item_pixmap = QtGui.QPixmap()
        self.item_pixmap.convertFromImage(self.item_image)
        self.setPixmap(self.item_pixmap)
"""