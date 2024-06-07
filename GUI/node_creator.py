# -*- coding: utf-8 -*-
"""This module containing all graphical class for node representation."""
# class define base template graphic node inside node editor

# NOTES:
# early bug fix > fix before video reach the solution, might need modified

# ---------------------------------- Problem ----------------------------------
# -calcPath inside edge graphic fire simultaneously, might be expensive
# deserialize inside node config, in python 2.7 can't have multiple inheritance therefore can't check if node content instance is from serializable (ref to node content also,if fixed)

from collections import OrderedDict

from PySide2 import QtCore,QtWidgets,QtGui

from GUI.serializable import Serializable

import math

import GUI.node_content as node_content
import GUI.node_edge_graphic_path as edge_path

DEBUG = False
DEBUG_REMOVE_WARNING = False  
DEBUG_ITEM = False # delete later when bezier fixed

# sockets constant
LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

# sockets color
SOCKET_COLORS = [
    QtGui.QColor("#FFFF7700"),
    QtGui.QColor("#609f62"),    # integer
    QtGui.QColor("#FF0056a6"),
    QtGui.QColor("#FFa86db1"),
    QtGui.QColor("#FFb54747"),
    QtGui.QColor("#FFdbe220")
]

# edge graphic constant
EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2 

class SocketGraphics(QtWidgets.QGraphicsItem):
    """Class representing Graphic `Socket` in ``QGraphicsScene``"""
    def __init__(self, socket):
        """
        :param socket: reference to :class:`~GUI.node_creator.SocketConfig`
        :type socket: :class:`~GUI.node_creator.SocketConfig`
        """
        super(SocketGraphics,self).__init__(socket.node.node_graphic)

        self.socket = socket

        self.isHighlighted = False

        self.radius = 5.0   # default 6.0
        self.outline_width = 1.0
        self.initAssets()

    @property
    def socket_type(self):
        return self.socket.socket_type

    def getSocketColor(self, key):
        """Returns the ``QColor`` for this ``key``"""
        if type(key) == int: return SOCKET_COLORS[key]
        elif type(key) == str: return QtGui.QColor(key)
        else: return QtCore.Qt.transparent

    def changeSocketType(self):
        """Change the Socket Type"""
        self._color_background = self.getSocketColor(self.socket_type)
        self._brush = QtGui.QBrush(self._color_background)
        self.update()

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color_background = self.getSocketColor(self.socket_type)
        self._color_outline = QtGui.QColor("#1b1818")
        self._color_highlight = QtGui.QColor("#FF37A6FF")

        self._pen = QtGui.QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._pen_highlight = QtGui.QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.0)
        self._brush = QtGui.QBrush(self._color_background)

    def paint(self, painter, option, widget):
        """Paint socket (circle)"""
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.isHighlighted else self._pen_highlight)
        painter.drawEllipse(-self.radius,
                            -self.radius,
                            2*self.radius,
                            2*self.radius)
        
    def boundingRect(self):
        """Defining Qt' bounding rectangle"""
        return QtCore.QRectF(-self.radius - self.outline_width,
                             -self.radius - self.outline_width,
                             2*(self.radius+self.outline_width),
                             2*(self.radius+self.outline_width)).normalized()

class SocketConfig(Serializable):
    Socket_Graphic_Class = SocketGraphics

    """Class representing Socket."""
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1, multi_edges=True, socket_amount=1, is_input=False):
        """
        :param node: reference to the :class:`~GUI.node_creator.NodeConfig` containing this `Socket`
        :type node: :class:`~GUI.node_creator.NodeConfig`
        :param index: Current index of this socket in the position
        :type index: ``int``
        :param position: Socket position. See :ref:`socket-position-constants`
        :param socket_type: Constant defining type(color) of this socket
        :param multi_edges: Can this socket have multiple `Edges` connected?
        :type multi_edges: ``bool``
        :param socket_amount: number of total sockets on this position (not total socket attached to node)
        :type socket_amount: ``int``
        :param is_input: Is this an input `Socket`?
        :type is_input: ``bool``

        :Instance Attributes:

            - **node** - reference to the :class:`~GUI.node_creator.NodeConfig` containing this `Socket`
            - **edges** - list of `Edges` connected to this `Socket`
            - **grSocket** - reference to the :class:`~GUI.node_creator.SocketGraphics`
            - **position** - Socket position. See :ref:`socket-position-constants`
            - **index** - Current index of this socket in the position
            - **socket_type** - Constant defining type(color) of this socket
            - **socket_amount** - number of sockets on this side (not total socket attached to node)
            - **is_multi_edges** - ``True`` if `Socket` can contain multiple `Edges`
            - **is_input** - ``True`` if this socket serves for Input
            - **is_output** - ``True`` if this socket serves for Output
        """
        Serializable.__init__(self)

        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges
        self.socket_amount = socket_amount
        self.is_input = is_input
        self.is_output = not self.is_input

        self.socket_graphic = self.__class__.Socket_Graphic_Class(self)

        self.setSocketPosition()

        self.edges = []

    def delete(self):
        """Clean delete this `Socket` from graphics scene"""
        self.socket_graphic.setParentItem(None)
        self.node.scene.scene_graphic.removeItem(self.socket_graphic)
        del self.socket_graphic

    def changeSocketType(self, new_socket_type):
        """
        Change the socket type

        :param new_socket_type: new socket type
        :type new_socket_type: ``int``
        :return: Returns ``True`` if the socket type was actually changed
        :rtype: ``bool``
        """
        if self.socket_type != new_socket_type:
            self.socket_type = new_socket_type
            self.socket_graphic.changeSocketType()
            return True
        return False

    def setSocketPosition(self):
        """Helper function to set `Graphics Socket` position. Exact socket position is calculated
        inside :class:`~NodeConfig`."""
        # asterisk > parse arg from tuple
        self.socket_graphic.setPos(*self.node.getSocketPosition(self.index, self.position, self.socket_amount))

    def getSocketPosition(self):
        """
        :return: Returns this `Socket` position according to the implementation stored in
            :class:`~NodeConfig`
        :rtype: ``x, y`` position
        """
        return (self.node.getSocketPosition(self.index, self.position, self.socket_amount))

    def getSocketScenePosition(self):
        """
        :return: Returns this `Socket` position from absolute scene position
        :rtype: ``x, y`` position
        """
        return self.node.getSocketScenePosition(self)

    def hasAnyEdge(self):
        """
        Returns ``True`` if any :class:`~EdgeConfig` is connected to this socket

        :return: ``True`` if any :class:`~EdgeConfig` is connected to this socket
        :rtype: ``bool``
        """
        return len(self.edges) > 0

    def isConnected(self, edge):
        """
        Returns ``True`` if :class:`~EdgeConfig` is connected to this `Socket`

        :param edge: :class:`~EdgeConfig` to check if it is connected to this `Socket`
        :type edge: :class:`~EdgeConfig`
        :return: ``True`` if `Edge` is connected to this socket
        :rtype: ``bool``
        """
        return edge in self.edges

    def addEdge(self, edge=None):
        """
        Append an Edge to the list of connected Edges

        :param edge: :class:`~EdgeConfig` to connect to this `Socket`
        :type edge: :class:`~EdgeConfig`
        """
        self.edges.append(edge)

    def removeEdge(self, edge):
        """
        Disconnect passed :class:`~EdgeConfig` from this `Socket`
        :param edge: :class:`~EdgeConfig` to disconnect
        :type edge: :class:`~EdgeConfig`
        """
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNING:
                print ("!W", "Socket::removeEdge", "wanna remove edge", edge, 
                       "from self.edges but it's not in the list")

    def removeAllEdges(self, silent=False):
        """Disconnect all `Edges` from this `Socket`"""
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()   # remove with notifications

    #def hasEdge(self):
    #   return self.edges is not None
    
    def determineMultiEdges(self, data):
        """
        Deserialization helper function.
        This function is here to help solve the issue of opening older files in the newer format.
        If the 'multi_edges' param is missing in the dictionary, we determine if this `Socket`
        should support multiple `Edges`.

        :param data: `Socket` data in ``dict`` format for deserialization
        :type data: ``dict``
        :return: ``True`` if this `Socket` should support multi_edges
        """
        if 'multi_edges' in data:
            return data['multi_edges']
        else:  
            # older version, make output socket (right) multi_edges by default
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self):
        return OrderedDict([    
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        self.is_multi_edges = self.determineMultiEdges(data)
        self.changeSocketType(data['socket_type'])
        hashmap[data['id']] = self
        return True

class NodeGraphics(QtWidgets.QGraphicsItem, object):
    """Class describing Graphics representation of :class:`~GUI.node_creator.NodeConfig`"""
    def __init__(self, node, parent=None):
        """
        :param node: reference to :class:`~NodeConfig`
        :type node: :class:`~NodeConfig`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:

            - **node** - reference to :class:`~NodeConfig`
        """
        super(NodeGraphics,self).__init__(parent)
        self.node = node
        
        # init node flags
        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAsset()
        self.initUI()

    @property
    def content(self):
        """Reference to `Node Content`"""
        return self.node.content if self.node else None

    @property   # getter
    def title(self): 
        """title of this `Node`

        :getter: current Graphics Node title
        :setter: stores and make visible the new title
        :type: str
        """
        return self._title

    @title.setter # set title
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def initUI(self):
        """Set up this ``QGraphicsItem``"""
        # set initial pos (at center of editor)
        # self.setPos(self.node.scene.width-(self.width/2), 
        #             self.node.scene.height-(self.height/2))

        self.setFlag(NodeGraphics.ItemIsSelectable)
        self.setFlag(NodeGraphics.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        # init title
        self.initTitle()
        self.title = self.node.title

        self.initContent()

    def initSizes(self):
        """Set up internal attributes like `width`, `height`, etc."""
        self.width = 180
        self.height = 120  # default 240
        self.edge_roundness = 10
        self.edge_padding = 10
        self.title_height = 30
        self.title_horizontal_padding = 5
        self.title_vertical_padding = 5

    def initAsset(self):
        """Initialize ``QObjects`` -> ``QColor``, ``QPen`` and ``QBrush``"""
        self._title_color = QtCore.Qt.white
        self._title_font = QtGui.QFont("Ubuntu", 10)

        self._color = QtGui.QColor("#1b1818")
        self._color_selected = QtGui.QColor("#FFFFA637")
        self._color_hovered = QtGui.QColor("#FF37A6FF")

        self._pen_default = QtGui.QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QtGui.QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QtGui.QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.5)

        self._brush_title = QtGui.QBrush(QtGui.QColor("#FF313131"))
        self._brush_background = QtGui.QBrush(QtGui.QColor("#E3212121"))
        self._brush_segment = QtGui.QBrush(QtGui.QColor("#E3212121"))

    def onSelected(self):
        """Our event handling when the node was selected"""
        self.node.scene.scene_graphic.itemSelected.emit()

    def doSelect(self, new_state=True):
        """Safe version of selecting the `Graphics Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def mouseMoveEvent(self, event):
        """Overridden event to detect that we moved with this `Node`"""
        super(NodeGraphics,self).mouseMoveEvent(event)

        # optimize me pls, just update the selected nodes
        for node in self.scene().scene.nodes: 
            if node.node_graphic.isSelected():
                node.updateConnectedEdges()

        self._was_moved = True
    
    def mouseReleaseEvent(self, event):
        """Overriden event to handle when we moved, selected or deselected this `Node`"""
        super(NodeGraphics,self).mouseReleaseEvent(event)

        # handle when node graphic moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("move node", setModified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()     # also trigger itemSelected when node was moved

            # store the last selected state, because moving also select the nodes
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()
            
            # skip storing selection (below)
            return

        # update history if last state doesn't match with current state (selected) or active selected doesn't match with last selected 
        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def mouseDoubleClickEvent(self, event):
        """Overriden event for doubleclick. Resend to `NodeConfig::onDoubleClicked`"""
        self.node.onDoubleClicked(event)

    def hoverEnterEvent(self, event):
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def boundingRect(self):
        """Defining Qt' bounding rectangle"""
        return QtCore.QRectF(0, 0, self.width, self.height).normalized()

    def initTitle(self):
        """Set up the title Graphics representation: font, color, position, etc."""
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.node = self.node    # forget what this one for, but when disable seems no issue
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)

    def initContent(self):
        """Set up the `grContent` - ``QGraphicsProxyWidget`` to have a container for `Graphics Content`"""
        if self.content is not None:
            self.content.setGeometry(self.edge_padding, 
                                    self.title_height + self.edge_padding,
                                    self.width-2*self.edge_padding,
                                    self.height-2*self.edge_padding-self.title_height)
            
        # get the QGraphicsProxyWidget when inserted into the scene_graphic
        self.content_graphic = self.node.scene.scene_graphic.addWidget(self.content)
        self.content_graphic.setParentItem(self)    # parent content to node

    def paint(self, painter, option, widget):
        """Painting the rounded rectanglar `Node`"""
        # paint title segment
        path_title = QtGui.QPainterPath()
        path_title.setFillRule(QtCore.Qt.WindingFill)
        path_title.addRoundedRect(0, 
                                  0, 
                                  self.width, 
                                  self.title_height, 
                                  self.edge_roundness, 
                                  self.edge_roundness)
        path_title.addRect(0,
                           (self.title_height-self.edge_roundness),
                           self.edge_roundness,
                           self.edge_roundness)
        
        path_title.addRect((self.width-self.edge_roundness),
                           (self.title_height-self.edge_roundness),
                           self.edge_roundness,
                           self.edge_roundness)
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # paint content segment
        path_content = QtGui.QPainterPath()
        path_content.setFillRule(QtCore.Qt.WindingFill)
        path_content.addRoundedRect(0,
                                    self.title_height,
                                    self.width,
                                    self.height-self.title_height,
                                    self.edge_roundness,
                                    self.edge_roundness)
        path_content.addRect(0,
                            self.title_height,
                            self.edge_roundness,
                            self.edge_roundness)
        
        path_content.addRect(self.width-self.edge_roundness,
                            self.title_height,
                            self.edge_roundness,
                            self.edge_roundness)
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_background)   
        painter.drawPath(path_content.simplified())    

        # draw segmented row
        path_segment = QtGui.QPainterPath()
        path_segment.setFillRule(QtCore.Qt.WindingFill)
        segment_offset = (self.height-self.title_height) % self.node.socket_spacing # find any empty space after last segment 

        for index in range(0,int((self.height-self.title_height)/self.node.socket_spacing),2):
            y_segment = self.title_height+(self.node.socket_spacing*index)
            path_segment.addRect(0,y_segment,self.width,self.node.socket_spacing)
        
        if segment_offset: 
            if self.height - self.title_height > y_segment + self.node.socket_spacing + self.edge_roundness:
                path_segment.addRoundedRect(0, 
                                            y_segment + self.node.socket_spacing*2, 
                                            self.width,
                                            segment_offset,
                                            self.edge_roundness,
                                            self.edge_roundness)
                path_segment.addRect(0,
                                     y_segment + self.node.socket_spacing*2,
                                     self.edge_roundness,
                                     self.edge_roundness)
                
                path_segment.addRect(self.width-self.edge_roundness,
                                     y_segment + self.node.socket_spacing*2,
                                     self.edge_roundness,
                                     self.edge_roundness)
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_segment)
        painter.drawPath(path_segment) 

        # paint outline element
        path_outline = QtGui.QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width+2, self.height+2, self.edge_roundness, self.edge_roundness)
        painter.setBrush(QtCore.Qt.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)               # paint it again so there is overlapping effect being drawn
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected) 
            painter.drawPath(path_outline.simplified())

class NodeConfig(Serializable, object):
    """Class representing `Node` in the `Scene`."""
    GraphicNode_class = NodeGraphics
    NodeContent_class = node_content.NodeContentWidget
    Socket_class = SocketConfig
    
    # (title = node title (should be unique) , scene = graphic scene)
    def __init__(self, nameID, scene, inputs=[], outputs=[]):
        """
        :param nameID: Node Name show in Scene (must be unique)
        :type nameID: str
        :param scene: reference to the :class:`~GUI.node_editor.Scene`
        :type scene: :class:`~GUI.node_editor.Scene`
        :param inputs: list of :class:`~SocketConfig` types from which the `Sockets` will be created automatically
        :param outputs: list of :class:`~SocketConfig` types from which the `Sockets` will be created automatically

        :Instance Attributes:

            - **scene** - reference to the :class:`~GUI.node_editor.Scene`
            - **node_graphic** - Instance of :class:`~NodeGraphics` handling graphical representation in the ``GraphicsScene``. Automatically created in the constructor
            - **content** - Instance of :class:`~GUI.node_content` which is child of ``QWidget`` representing container for all inner widgets inside of the Node. Automatically created in the constructor
            - **inputs** - list containing Input :class:`~SocketConfig` instances
            
        """
        Serializable.__init__(self)

        # the setup here will be used inside graphic node, from instance referencing
        self._title = nameID # title
        self.scene = scene

        self.content = None
        self.node_graphic = None

        self.segment_amount = max(len(inputs),len(outputs))    # to automatically adjust height for zeno node
        self.initSettings()
        self.initInnerClasses()
        self.title = nameID # title
        
        self.scene.addNode(self)
        self.scene.scene_graphic.addItem(self.node_graphic)

        # create sockets for inputs and outputs
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

        # dirty and evaluation
        self._is_dirty = False
        self._is_invalid = False

    @property   # getter
    def title(self): 
        """
        Title shown in the scene

        :getter: return current Node title
        :setter: sets Node title and passes it to Graphics Node class
        :type: ``str``
        """
        return self._title

    @title.setter # set title
    def title(self, value):
        self._title = value
        self.node_graphic.title = self._title

    @property
    def pos(self):
        """
        Retrieve Node's position in the Scene

        :return: Node position
        :rtype: ``QPointF``
        """
        return self.node_graphic.pos() # return QpointF
    
    def setPos(self, x, y):
        """
        Sets position of the Graphics Node

        :param x: X `Scene` position
        :param y: Y `Scene` position
        """
        self.node_graphic.setPos(x, y)

    def initInnerClasses(self):
        """Sets up graphics Node and Content Widget"""
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None: self.content = node_content_class(self)
        if graphics_node_class is not None: self.node_graphic = graphics_node_class(self)

    def getNodeContentClass(self):
        """Returns class representing nodeeditor constant"""
        return self.__class__.NodeContent_class
    
    def getGraphicsNodeClass(self):
        return self.__class__.GraphicNode_class

    def initSettings(self):
        """Initialize properties and socket information"""
        self.socket_spacing = 20

        self.input_socket_position = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.socket_offsets = {
            LEFT_BOTTOM : -1,
            LEFT_CENTER : -1,
            LEFT_TOP : -1,
            RIGHT_BOTTOM : 1,
            RIGHT_CENTER : 1,
            RIGHT_TOP : 1,
        }

    def initSockets(self, inputs, outputs, reset=True):
        """ Create sockets for inputs and outputs

        :param inputs: list of Socket Types (int)
        :type inputs: ``list``
        :param outputs: list of Socket Types (int)
        :type outputs: ``list``
        :param reset: if ``True`` destroys and removes old `Sockets`
        :type reset: ``bool``
        """

        if reset:
            # clear old sockets
            if hasattr(self,'inputs') and hasattr(self, 'outputs'):
                # remove socket graphic from scene
                for socket in (self.inputs+self.outputs):
                    self.scene.scene_graphic.removeItem(socket.socket_graphic)
                self.inputs = []
                self.outputs = []

        # create new sockets
        for counter,item in enumerate(inputs):
            socket = self.__class__.Socket_class(node=self, 
                                                index=counter, 
                                                position=self.input_socket_position, 
                                                socket_type=item, 
                                                multi_edges=self.input_multi_edged, 
                                                socket_amount=len(inputs),
                                                is_input=True)
            counter+=1
            self.inputs.append(socket)

        for counter,item in enumerate(outputs):
            socket = self.__class__.Socket_class(node=self, 
                                                index=counter, 
                                                position=self.output_socket_position, 
                                                socket_type=item, multi_edges=self.output_multi_edged,
                                                socket_amount=len(outputs),
                                                is_input=False)
            counter+=1
            self.outputs.append(socket)

    def onEdgeConnectionChanged(self, new_edge):
        """
        Event handling that any connection (`Edge`) has changed. Currently not used...

        :param new_edge: reference to the changed :class:`~EdgeConfig`
        :type new_edge: :class:`~EdgeConfig`
        """
        pass
        #print("%s::onEdgeConnectionChanged"% self.__class__.__name__, new_edge)

    def onInputChanged(self, socket):
        """Event handling when Node's input Edge has changed. We auto-mark this `Node` to be `Dirty` with all it's
        descendants

        :param socket: reference to the changed :class:`~SocketConfig`
        :type socket: :class:`~SocketConfig`
        """
        self.markDirty()
        self.markDescendantsDirty()
        #print("%s::onInputChanged"% self.__class__.__name__, socket)

    def onDeserialized(self, data):
        """Event manually called when this node was deserialized, can be used for custom use. Currently called when node is deserialized from scene
        Passing `data` containing the data which have been deserialized"""
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics Node in `Scene`"""
        pass

    def doSelect(self, new_state=True):
        """Shortcut method for selecting/deselecting the `Node`

        :param new_state: ``True`` if you want to select the `Node`. ``False`` if you want to deselect the `Node`
        :type new_state: ``bool``
        """
        self.node_graphic.doSelect(new_state)

    def isSelected(self):
        """Returns ``True`` if current `Node` is selected"""
        return self.node_graphic.isSelected()

    def getSocketPosition(self, index, position, num_socket=1):
        """
        Get the relative `x, y` position of a :class:`~SocketConfig`. This is used for placing
        the `Graphics Sockets` on `Graphics Node`.

        :param index: Order number of the Socket. (0, 1, 2, ...)
        :type index: ``int``
        :param position: `Socket Position Constant` describing where the Socket is located. See :ref:`socket-position-constants`
        :type position: ``int``
        :param num_out_of: Total number of Sockets on this `Socket Position`
        :type num_out_of: ``int``
        :return: Position of described Socket on the `Node`
        :rtype: ``x, y``
        """
        x = self.socket_offsets[position] if position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM) else self.node_graphic.width + self.socket_offsets[position]

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = (self.node_graphic.height - 
                 self.node_graphic.edge_roundness - 
                 self.node_graphic.title_vertical_padding) + (
                 index*self.socket_spacing)
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            node_height = self.node_graphic.height
            top_offset = self.node_graphic.title_height + 2 * self.node_graphic.title_vertical_padding + self.node_graphic.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_socket * self.socket_spacing
            new_top = available_height - total_height_of_all_sockets

            #y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height/2 + (index-0.5)*self.socket_spacing
            if num_socket > 1:
                y -= self.socket_spacing * (num_socket-1)/2

        elif position in (LEFT_TOP, RIGHT_TOP):
            y = (self.node_graphic.title_height +
                 (self.node_graphic.title_vertical_padding/2) +
                 self.node_graphic.edge_roundness) + (
                 index*self.socket_spacing)
        else:
            y = 0 # this should never happen, else something error
        return [x, y]
    
    def getSocketScenePosition(self, socket):
        """Get absolute Socket posiiton in the Scene

        :param socket: which `Socket` we want to know
        :return: (x,y) socket's scene position
        """
        nodepos = self.node_graphic.pos()
        socketpos = self.getSocketPosition(socket.index, socket.position, socket.socket_amount)
        return (nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])

    def updateConnectedEdges(self):
        """Recalculate (Refresh) positions of all connected `Edges`. Used for updating Graphics Edges"""
        for socket in self.inputs + self.outputs:
            #if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        """
        remove this instance (Node) from ``Scene``
        """
        if DEBUG: print("> Removing Node", self)
        if DEBUG: print(" - remove all edges from sockets")
        for socket in (self.inputs+self.outputs):
            for edge in socket.edges:
                if DEBUG: print("   - removing from socket: ", socket, "edge: ", edge)
                edge.remove()
        if DEBUG: print(" - remove node graphics")
        self.scene.scene_graphic.removeItem(self.node_graphic)
        self.node_graphic = None
        if DEBUG: print(" - remove node from the scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - node successfully removed, done!")

    # node evaluation stuff (getter setter using function)

    def isDirty(self):
        """Is this node marked as `Dirty`

        :return: ``True`` if `Node` is marked as `Dirty`
        :rtype: ``bool``
        """
        return self._is_dirty

    def markDirty(self, value=True):
        """Mark this `Node` as `Dirty`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `Node` should be `Dirty`. ``False`` if you want to un-dirty this `Node`
        :type new_value: ``bool``
        """
        self._is_dirty = value
        if self._is_dirty: self.onMarkedDirty()
        self.node_graphic.update()  # early bug fix (image not update inside node)

    def onMarkedDirty(self): 
        """Called when this `Node` has been marked as `Dirty`. This method is supposed to be overridden"""
        pass

    def markChildrenDirty(self, value=True):
        """Mark all first level children of this `Node` to be `Dirty`. Not this `Node` it self. Not other descendants

        :param new_value: ``True`` if children should be `Dirty`. ``False`` if you want to un-dirty children
        :type new_value: ``bool``
        """
        for node in self.getChildrenNodes():
            node.markDirty(value)

    def markDescendantsDirty(self, value=True):
        """Mark all children and descendants of this `Node` to be `Dirty`. Not this `Node` it self

        :param new_value: ``True`` if children and descendants should be `Dirty`. ``False`` if you want to un-dirty children and descendants
        :type new_value: ``bool``
        """
        for node in self.getChildrenNodes():
            node.markDirty(value)
            node.markDescendantsDirty(value)    # recursive call, to find all child along the connection

    def isInvalid(self):
        """Is this node marked as `Invalid`?

        :return: ``True`` if `Node` is marked as `Invalid`
        :rtype: ``bool``
        """
        return self._is_invalid

    def markInvalid(self, value=True):
        """Mark this `Node` as `Invalid`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `Node` should be `Invalid`. ``False`` if you want to make this `Node` valid
        :type new_value: ``bool``
        """
        self._is_invalid = value
        if self._is_invalid: self.onMarkedInvalid()
        self.node_graphic.update() # early bug fix (image not update inside node)

    def onMarkedInvalid(self): 
        """Called when this `Node` has been marked as `Invalid`. This method is supposed to be overridden"""
        pass

    def markChildrenInvalid(self, value=True):
        """Mark all first level children of this `Node` to be `Invalid`. Not this `Node` it self. Not other descendants

        :param new_value: ``True`` if children should be `Invalid`. ``False`` if you want to make children valid
        :type new_value: ``bool``
        """
        for node in self.getChildrenNodes():
            node.markInvalid(value)

    def markDescendantsInvalid(self, value=True):
        """Mark all children and descendants of this `Node` to be `Invalid`. Not this `Node` it self

        :param new_value: ``True`` if children and descendants should be `Invalid`. ``False`` if you want to make children and descendants valid
        :type new_value: ``bool``
        """
        for node in self.getChildrenNodes():
            node.markInvalid(value)
            node.markChildrenInvalid(value)

    def eval(self, index=0):
        """Evaluate this `Node`. This is supposed to be overridden. See :ref:`evaluation` for more"""
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    def evalChildren(self):
        """Evaluate all children of this `Node`"""
        for node in self.getChildrenNodes():
            node.eval()

    # traversing node functions

    def getChildrenNodes(self):
        """
        Retreive all first-level children connected to this `Node` `Outputs`

        :return: list of `Nodes` connected to this `Node` from all `Outputs`
        :rtype: List[:class:`~GUI.node_creator.NodeConfig`]
        """
        if self.outputs == []: return []
        nodes = []
        for index in range(len(self.outputs)):
            for edge in self.outputs[index].edges:
                node = edge.getOtherSocket(self.outputs[index]).node
                nodes.append(node)
        return nodes
    
    def getInput(self, index=0):
        """
        Get the **first**  `Node` connected to the  Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: :class:`~GUI.node_creator.NodeConfig` which is connected to the specified `Input` or ``None`` if
            there is no connection or the index is out of range
        :rtype: :class:`~GUI.node_creator.NodeConfig` or ``None``
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0 : return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except Exception as e:
            print(e)
            return None
        
    def getInputWithSocket(self, index=0):
        """
        Get the **first**  `Node` connected to the Input specified by `index` and the connection `Socket`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~nodeeditor.node_node.Node` and :class:`~nodeeditor.node_socket.Socket` which
            is connected to the specified `Input` or ``None`` if there is no connection or the index is out of range
        :rtype: (:class:`~nodeeditor.node_node.Node`, :class:`~nodeeditor.node_socket.Socket`)
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None, None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket
        except Exception as e:
            print(e)
            return None, None   
    
    def getInputWithSocketIndex(self, index=0):
        """
        Get the **first**  `Node` connected to the Input specified by `index` and the connection `Socket`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~NodeConfig` and :class:`~SocketConfig` which
            is connected to the specified `Input` or ``None`` if there is no connection or the index is out of range
        :rtype: (:class:`~NodeConfig`, int)
        """
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node, socket.index
        except IndexError:
            # print("EXC: Trying to get input with socket index %d, but none is attached to" % index, self)
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def getInputs(self, index=0):
        """
        Get **all** `Nodes` connected to the Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: all :class:`~GUI.node_creator.NodeConfig` instances which are connected to the
            specified `Input` or ``[]`` if there is no connection or the index is out of range
        :rtype: List[:class:`~GUI.node_creator.NodeConfig`]
        """
        inputs = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            inputs.append(other_socket.node)
        return inputs
    
    def getOutputs(self, index=0):
        """
        Get **all** `Nodes` connected to the Output specified by `index`

        :param index: Order number of the `Output Socket`
        :type index: ``int``
        :return: all :class:`~GUI.node_creator.NodeConfig` instances which are connected to the
            specified `Output` or ``[]`` if there is no connection or the index is out of range
        :rtype: List[:class:`~GUI.node_creator.NodeConfig`]
        """
        outputs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outputs.append(other_socket.node)
        return outputs

    # serialization functions

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}
        return OrderedDict([    
            ('id', self.id),
            ('title', self.title),  # early bug fix (before fix > self._title)
            ('pos_x', self.node_graphic.scenePos().x()),
            ('pos_y', self.node_graphic.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', ser_content),
        ])
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        try:
            if restore_id: self.id = data['id']
            hashmap[data['id']] = self

            self.setPos(data['pos_x'],data['pos_y'])
            self.title = data['title']

            # sort node inputs by index
            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1000)
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1000)
            num_inputs = len(data['inputs'])
            num_outputs = len(data['outputs'])

            # reuse existing sockets, dont create new ones if not necessary (assign to usable socket)
            for socket_data in data['inputs']:
                usable_socket = None 
                for socket in self.inputs:
                    if socket.index == socket_data['index']:
                        usable_socket = socket
                        break
                if usable_socket is None:
                    # desired socket is not present, create new one 
                    usable_socket = self.__class__.Socket_class(node=self, 
                                                                index=socket_data['index'],
                                                                position=socket_data['position'],
                                                                socket_type=socket_data['socket_type'], 
                                                                socket_amount=num_inputs,
                                                                is_input=True)
                    self.inputs.append(usable_socket)
                usable_socket.deserialize(socket_data, hashmap, restore_id)

            for socket_data in data['outputs']:
                usable_socket = None
                for socket in self.outputs:
                    if socket.index == socket_data['index']:
                        usable_socket = socket
                        break
                if usable_socket is None:
                    # desired socket is not present, create new one 
                    usable_socket = self.__class__.Socket_class(node=self, 
                                                                index=socket_data['index'],
                                                                position=socket_data['position'],
                                                                socket_type=socket_data['socket_type'],
                                                                socket_amount=num_outputs,
                                                                is_input=False)
                    self.outputs.append(usable_socket)
                usable_socket.deserialize(socket_data, hashmap, restore_id)
        
        except Exception as e: print(e)

        # deserialize the content of the node (last step)
        if isinstance(self.content, Serializable):
            res = self.content.deserialize(data['content'], hashmap)
            return res

        return True 

class EdgeGraphics(QtWidgets.QGraphicsPathItem):
    """Base class for Graphics Edge"""
    def __init__(self, edge, parent=None):
        """
        :param edge: reference to :class:`~GUI.node_creator.EdgeConfig`
        :type edge: :class:`~GUI.node_creator.EdgeConfig`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance attributes:

            - **edge** - reference to :class:`~GUI.node_creator.EdgeConfig`
            - **posSource** - ``[x, y]`` source position in the `Scene`
            - **posDestination** - ``[x, y]`` destination position in the `Scene`
        """
        super(EdgeGraphics,self).__init__(parent)

        self.edge = edge

        # init variables
        self.pos_source = [0, 0]
        self.pos_destination = [200, 100]

        # create instance of our path class
        self.pathCalculator = self.determineEdgePathClass()(self)

        # init edge flags
        self._last_selected_state = False
        self.hovered = False

        self.initAssets()
        self.initUI()

    def initUI(self):
        """Set up this ``QGraphicsPathItem``"""
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True) # create bounding box to graphic item according to shape function, overlap will trigger hover event
        self.setZValue(-1)

    def initAssets(self):
        """Initialize ``QObjects`` -> ``QColor``, ``QPen`` and ``QBrush``"""
        self._color = self._default_color = QtGui.QColor("#507d8c")
        self._color_selected = QtGui.QColor("#FFA637")
        self._color_hovered = QtGui.QColor("#FF37A6FF")
        self._color_dragging = QtGui.QColor("#fff537") # #15142b (Darker color)
        self._pen = QtGui.QPen(self._color)
        self._pen_selected = QtGui.QPen(self._color_selected)
        self._pen_dragging = QtGui.QPen(self._color_dragging)
        self._pen_hovered = QtGui.QPen(self._color_hovered)
        self._pen_dragging.setStyle(QtCore.Qt.DashLine)
        self._pen.setWidthF(2.5)
        self._pen_selected.setWidthF(3.0)
        self._pen_dragging.setWidthF(3.0)
        self._pen_hovered.setWidthF(5.0)
        if self.edge.start_socket:  # check if current edge have start_socket, if not skip to prevent error
            self.changeColor(self.edge.start_socket.socket_graphic.getSocketColor(self.edge.start_socket.socket_type))


    def createEdgePathCalculator(self):
        """Create instance of :class:`~GUI.node_edge_graphic_path.EdgePathBaseGraphics`"""
        self.pathCalculator = self.determineEdgePathClass()(self)
        return self.pathCalculator
    
    def determineEdgePathClass(self):
        """Decide which graphicsEdgePath class should be used to calculate path according to edgeConfig.edge_type value"""
        if self.edge.edge_type == EDGE_TYPE_BEZIER:
            return edge_path.EdgePathBezierGraphics
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return edge_path.EdgePathDirectGraphics
        else:
            return edge_path.EdgePathBezierGraphics

    def makeUnselectable(self):
        """Used for drag edge to disable click detection over this graphics item"""
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(False)

    def changeColor(self, color):
        """Change color of the edge from string hex value `#00ff00`"""
        # print("^Called change color to:", color.red(), color.green(), color.blue(), "on edge:", self.edge)
        self._color = QtGui.QColor(color) if type(color) == str else color
        self._pen = QtGui.QPen(self._color)
        self._pen.setWidthF(3.0)
    
    def setColorFromSockets(self):
        """Change color according to connected sockets. Returns ``True`` if color can be determined"""
        socket_type_start = self.edge.start_socket.socket_type
        socket_type_end = self.edge.end_socket.socket_type
        if socket_type_start != socket_type_end: return False
        self.changeColor(self.edge.start_socket.socket_graphic.getSocketColor(socket_type_start))

    def onSelected(self):
        """Our event handling when the edge was selected"""
        self.edge.scene.scene_graphic.itemSelected.emit()

    def doSelect(self, new_state=True):
        """Safe version of selecting the `Graphics Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def mouseReleaseEvent(self, event):
        """Overridden Qt's method to handle selecting and deselecting this `Graphics Edge`"""
        super(EdgeGraphics, self).mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, event):
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def setSource(self, x, y):
        """ Set source point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.pos_source = (x, y)
    
    def setDestination(self, x, y):
        """ Set destination point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.pos_destination = (x, y)

    def boundingRect(self):
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()
    
    def shape(self):
        """Returns ``QPainterPath`` representation of this `Edge`

        :return: path representation
        :rtype: ``QPainterPath``
        """
        return self.calcPath()

    def paint(self, painter, option, widget):
        """Qt's overridden method to paint this Graphics Edge. Path calculated
            in :func:`~GUI.node_creator.EdgeGraphics.calcPath` method"""
        self.setPath(self.calcPath())

        painter.setBrush(QtCore.Qt.NoBrush)

        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        
        painter.drawPath(self.path())

    def intersectsWith(self, p1, p2):
        """Does this Graphics Edge intersect with the line between point A and point B ?

        :param p1: point A
        :type p1: ``QPointF``
        :param p2: point B
        :type p2: ``QPointF``
        :return: ``True`` if this `Graphics Edge` intersects
        :rtype: ``bool``
        """
        cutPath = QtGui.QPainterPath(p1)
        cutPath.lineTo(p2)
        path = self.calcPath()
        return cutPath.intersects(path)

    def calcPath(self):
        """Will handle drawing QPainterPath from Point A to B. Internally there exist self.pathCalculator which
        is an instance of derived :class:`GraphicsEdgePathBase` class
        containing the actual `calcPath()` function - computing how the edge should look like.

        :returns: ``QPainterPath`` of the edge connecting `source` and `destination`
        :rtype: ``QPainterPath``
        """
        return self.pathCalculator.calcPath()

class EdgeConfig(Serializable,object):
    """Class for representing Edge in NodeEditor."""

    edge_validators = []    # class variable containing list of registered edge validators

    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):
        """

        :param scene: Reference to the :py:class:`~GUI.node_editor.Scene`
        :type scene: :py:class:`~GUI.node_editor.Scene`
        :param start_socket: Reference to the starting socket
        :type start_socket: :py:class:`~GUI.node_creator.SocketConfig`
        :param end_socket: Reference to the End socket or ``None``
        :type end_socket: :py:class:`~GUI.node_creator.SocketConfig` or ``None``
        :param edge_type: Constant determining type of edge. See :ref:`edge-type-constants`

        :Instance Attributes:

            - **scene** - reference to the :class:`~GUI.node_editor.Scene`
            - **edge_graphic** - Instance of :class:`~GUI.node_creator.EdgeGraphics` subclass handling graphical representation in the ``QGraphicsScene``.
        """
        Serializable.__init__(self)
        self.scene = scene

        if DEBUG:
            self.source_debug = None
            self.destination_debug = None

        # default init
        self._start_socket = None
        self._end_socket = None
        self.edge_graphic = None # prevent error when changing edge color 

        self.start_socket = start_socket
        self.end_socket = end_socket
        self._edge_type = edge_type

        # create Graphics Edge instance
        self.edge_graphic = self.createEdgeClassInstance()

        self.scene.addEdge(self)

    @property
    def start_socket(self): 
        """
        Start socket

        :getter: Returns start :class:`~SocketConfig`
        :setter: Sets start :class:`~SocketConfig` safely
        :type: :class:`~SocketConfig`
        """
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # if edge were assigned to some socket, delete edge from the socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # assign new start socket
        self._start_socket = value
        # addEdge to socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)
            if self.edge_graphic:
                # change edge color according to socket source
                self.edge_graphic.changeColor(self.start_socket.socket_graphic.getSocketColor(self.start_socket.socket_type))

    @property
    def end_socket(self): 
        """
        End socket

        :getter: Returns end :class:`~SocketConfig` or ``None`` if not set
        :setter: Sets end :class:`~SocketConfig` safely
        :type: :class:`~SocketConfig` or ``None``
        """
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        # if edge were assigned to some socket, delete edge from the socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # assign new end socket
        self._end_socket = value
        # addEdge to socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self): 
        """
        Edge type

        :getter: get edge type constant for current ``Edge``. See :ref:`edge-type-constants`
        :setter: sets new edge type. On background, creates new :class:`~EdgeGraphics`
            child class if necessary, adds this ``QGraphicsPathItem`` to the ``QGraphicsScene`` and updates edge sockets
            positions.
        """
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        # assign new value
        self._edge_type = value

        # update the edge_graphic pathCalculator
        self.edge_graphic.createEdgePathCalculator()

        if self.start_socket is not None:
            self.updatePositions()

    @classmethod
    def getEdgeValidators(cls):
        """Return the list of Edge validator callbacks"""
        return cls.edge_validators

    @classmethod
    def registerEdgeValidator(cls, validator_callback):
        """Register Edge Validator Callback

        :param validator_callback: A function handle to validate Edge
        :type validator_callback: `function`
        """
        cls.edge_validators.append(validator_callback)

    @classmethod
    def validateEdge(cls, start_socket, end_socket):
        """Validate Edge agains all registered `Edge Validator Callbacks`

        :param start_socket: Starting :class:`~SocketConfig` of Edge to check
        :type start_socket: :class:`~SocketConfig`
        :param end_socket: Target/End :class:`~SocketConfig` of Edge to check
        :type end_socket: :class:`~SocketConfig`
        :return: ``True`` if the Edge is valid or ``False`` if not
        :rtype: ``bool``
        """
        for validator in cls.getEdgeValidators():
            if not validator(start_socket, end_socket):
                return False
        return True

    def getGraphicsEdgeClass(self):
        """Returns the class representing Graphics Edge"""
        return EdgeGraphics
    
    def createEdgeClassInstance(self):
        """Create instance of edge_graphics class
        :return: Instance of `edge_graphic` class representing the graphics edge in scene graphic
        """
        self.edge_graphic = self.getGraphicsEdgeClass()(self)
        self.scene.scene_graphic.addItem(self.edge_graphic)
        if self.start_socket is not None:
            self.updatePositions()
        return self.edge_graphic

    def getOtherSocket(self, known_socket):
        """
        Returns the opposite socket on this ``Edge``

        :param known_socket: Provide known :class:`~SocketConfig` to be able to determine the opposite one.
        :type known_socket: :class:`~SocketConfig`
        :return: The oposite socket on this ``Edge`` or ``None``
        :rtype: :class:`~SocketConfig` or ``None``
        """
        return self.start_socket if known_socket == self.end_socket else self.end_socket
    
    def doSelect(self, new_state=True):
        """
        Provide the safe selecting/deselecting operation. In the background it takes care about the flags, notifications
        and storing history for undo/redo.

        :param new_state: ``True`` if you want to select the ``Edge``, ``False`` if you want to deselect the ``Edge``
        :type new_state: ``bool``
        """
        self.edge_graphic.doSelect(new_state)

    def updatePositions(self):
        """
        Updates the internal `Graphics Edge` positions according to the start and end :class:`~SocketConfig`.
        This should be called if you update ``Edge`` positions.
        """
        source_position = self.start_socket.getSocketPosition()
        source_position[0] += self.start_socket.node.node_graphic.pos().x()
        source_position[1] += self.start_socket.node.node_graphic.pos().y()
        self.edge_graphic.setSource(*source_position)
        if self.end_socket is not None:
            end_position = self.end_socket.getSocketPosition()
            end_position[0] += self.end_socket.node.node_graphic.pos().x()
            end_position[1] += self.end_socket.node.node_graphic.pos().y()
            self.edge_graphic.setDestination(*end_position)
        else:
            self.edge_graphic.setDestination(*source_position)
        self.edge_graphic.update()

    def remove_from_sockets(self):
        """
        Helper function which sets start and end :class:`~SocketConfig` to ``None``
        """
        #if self.start_socket is not None:
        #    self.start_socket.removeEdge(None)
        #if self.end_socket is not None:
        #    self.end_socket.removeEdge(None)
        self.start_socket = None
        self.end_socket = None

    def remove(self, silent_for_socket=None, silent=False):
        """
        Safely remove this Edge.

        Removes `Graphics Edge` from the ``QGraphicsScene`` and it's reference to all GC to clean it up.
        Notifies nodes previously connected :class:`~NodeConfig` (s) about this event.

        Triggers Nodes:

        - :py:meth:`~NodeConfig.onEdgeConnectionChanged`
        - :py:meth:`~NodeConfig.onInputChanged`

        :param silent_for_socket: :class:`~SocketConfig` of a :class:`~NodeConfig` which
            won't be notified, when this ``Edge`` is going to be removed
        :type silent_for_socket: :class:`~SocketConfig`
        :param silent: ``True`` if no events should be triggered during removing
        :type silent: ``bool``
        """
        old_sockets = [self.start_socket, self.end_socket]

        # ugly hack?, sometimes when removing edge_graphics froms scene, it stays there! Qt problem?
        # self.edge_graphic.hide()
        self.scene.scene_graphic.removeItem(self.edge_graphic)
        self.scene.scene_graphic.update()

        self.remove_from_sockets()
        
        self.edge_graphic = None
        try:
            self.scene.removeEdge(self)
        except ValueError:  # detect if edge already deleted, then do nothing
            pass
        
        try:
            # notify nodes from old sockets
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        # if we requested silence for socket and it's this one, skip notifications
                        continue

                    # notify socket's node
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input: socket.node.onInputChanged(socket)

        except Exception as e: print (e)

    def serialize(self):
        return OrderedDict([    
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id if self.start_socket is not None else None),
            ('end', self.end_socket.id if self.end_socket is not None else None),
        ])
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']