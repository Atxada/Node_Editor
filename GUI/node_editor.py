# -*- coding: utf-8 -*-
"""This module containing all window and widget class for node editor system (mouse event, history, clipboard)."""

# class define all the GUI and visual element (except node graphic; see NodeCreator.py)

# NOTES:
#  early bug fix > fix before video reach the solution, might need modified

# --------------------------------------- Problem --------------------------------------- 
#  copy paste node > save graph > load graph > result in name changing (hint: serialize problem) (ideal solution: create system function to handle checking all duplicate)
#  cross cursor sometime being finicky
#  bezier weird curve
#  dragging to socket in between sometime crash (everything was done executed tho, hmm)

# ---------------------------------- Feature expansion ----------------------------------
# dockable (mayaQWidgetDockableMixin clash function close with QMainWindow) (watch chriss zurbrig pyside2 for maya vol.3 01-07)


from collections import OrderedDict     # create ordered dictionary

from PySide2 import QtCore,QtWidgets,QtGui
from shiboken2 import wrapInstance
#from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from GUI.serializable import Serializable

import json
import math
import os

import GUI.node_creator as node_creator
import GUI.node_features as node_features
import GUI.node_edge_dragging as edge_dragging

DEBUG = False
DEBUG_MMB_SCENE_ITEMS = False
DEBUG_MMB_LAST_SELECTIONS = False
DEBUG_PASTING = False    # Clipboard
DEBUG_REMOVE_WARNING = False    # Scene
DEBUG_SELECTION = False    # History
DEBUG_STATE = False  # graphic view 

# graphics view constant
MODE_NO_OPERATION = 1   # ready state (unoccupied)
MODE_EDGE_DRAG = 2      # drag edge state
MODE_EDGE_CUT = 3       # cutting edge state
MODE_EDGE_REROUTING = 4 # Mode representing when we re-reout existing edges
#MODE_NODE_DRAG = 5      # Mode representing when we drag a node to calculate dropping on intersecting edge

EDGE_REROUTING_UE = True   # enbale rerouting edge feature like unreal engine node editor

# socket snapping distance check
EDGE_SNAPPING_RADIUS = 12
# enable socket snapping feature
EDGE_SNAPPING = True

STATE_STRING = ['', 'no operation', 'dragging edge..', 'cutting edge..', 'rerouting edge..'] #'dragging node..'

# custom exception class
class InvalidFile(Exception): pass

class Scene(Serializable, object):
    """Class representing NodeEditor's `Scene`"""
    def __init__(self,width=8000,height=8000):
        """
        :Instance Attributes:

            - **nodes** - list of `Nodes` in this `Scene`
            - **edges** - list of `Edges` in this `Scene`
            - **history** - Instance of :class:`~SceneHistory`
            - **clipboard** - Instance of :class:`~SceneClipboard`
            - **scene_width** - width of this `Scene` in pixels
            - **scene_height** - height of this `Scene` in pixels
        """
        Serializable.__init__(self)
        self.hint = True   # hint when user open the app for the first time
        self.nodes = []
        self.edges = []

        self.width = width
        self.height = height

        # custom flag used to surpess triggering onItemSelected which does a bunch of stuff
        self._silent_selection_events = False

        self._has_been_modified = False
        self._last_selected_items = None

        # initialize all listeners
        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._item_deselected_listeners = []

        # store callback to retrieve the class for nodes
        self.node_class_selector = None
        
        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self.scene_graphic.itemSelected.connect(self.onItemSelected)
        self.scene_graphic.itemsDeselected.connect(self.onItemsDeselected)

    @property
    def has_been_modified(self):
        """
        Has this `Scene` been modified?

        :getter: ``True`` if the `Scene` has been modified
        :setter: set new state. Triggers `Has Been Modified` event
        :type: ``bool``
        """
        return self._has_been_modified
    
    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            # set it now, it will be read soon
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners: callback()

        self._has_been_modified = value

    def initUI(self):
        """Set up Graphics Scene Instance"""
        self.scene_graphic = GraphicsScene(self)
        self.scene_graphic.setGraphicScene(self.width,self.height)

    def getNodeByID(self, node_id):
        """Helper function to find node in the scene according to previous `node_id`

        :param node_id: ID of the node we are looking for
        :type node_id: ``int``
        :return: Found ``Node`` or ``None``
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def setSilentSelectionEvents(self, value=True):
        """Calling this can surpress onItemSelected events to be triggered. This is useful when working with clipboard"""
        self._silent_selection_events = value

    def onItemSelected(self, silent=False):
        """
        Handle Item selection and trigger event `Item Selected`

        :param silent: If ``True`` scene's onItemSelected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        if self._silent_selection_events: return

        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            if not silent:
                # we could create some kind of UI which could be serialized, therefore first run all callbacks...
                for callback in self._item_selected_listeners: callback()
                # store history as a last step always
                self.history.storeHistory("selection changed")

    def onItemsDeselected(self, silent=False):
        """
        Handle Items deselection and trigger event `Items Deselected`

        :param silent: If ``True`` scene's onItemsDeselected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        # somehow this event triggered when dragging file from outside application, is it because of loose focus on our app? it doesn't mean we deselected item in scene!
        # double check if the selection has changed
        current_selected_items = self.getSelectedItems()
        if current_selected_items == self._last_selected_items:
            if DEBUG: print("Qt itemsDeselected Invalid Event! Ignoring")
            return

        self.resetLastSelectedStates()
        if current_selected_items == []:
            self._last_selected_items = []
            if not silent:
                self.history.storeHistory("deselect all")
                for callback in self._item_deselected_listeners: callback()

    def isModified(self):
        """Is this `Scene` dirty or `has been modified` ?

        :return: ``True`` if `Scene` has been modified
        :rtype: ``bool``
        """
        return self.has_been_modified
    
    def getSelectedItems(self):
        """
        Returns currently selected Graphics Items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.scene_graphic.selectedItems()
    
    def doDeselectItems(self, silent=False):
        """
        Deselects everything in scene

        :param silent: If ``True`` scene's onItemDeselected won't be called
        :type silent: ``bool``
        """
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

    # helper listener function
    def addHasBeenModifiedListener(self, callback):
        """
        Register callback for `Has Been Modified` event

        :param callback: callback function
        """
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback):
        """
        Register callback for `Item Selected` event

        :param callback: callback function
        """
        self._item_selected_listeners.append(callback)

    def addItemDeselectedListener(self, callback):
        """
        Register callback for `Items Deselected` event

        :param callback: callback function
        """
        self._item_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback):
        """
        Register callback for `Drag Enter` event

        :param callback: callback function
        """
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self.getView().addDropListener(callback)

    # custom flag to detect node or edge has been selected...
    def resetLastSelectedStates(self):
        """Resets internal `selected flags` in all `Nodes` and `Edges` in the `Scene`"""
        for node in self.nodes:
            node.node_graphic._last_selected_state = False
        for edge in self.edges:
            edge.edge_graphic._last_selected_state = False      

    def getView(self):
        """Shortcut for returning `Scene` ``QGraphicsView``

        :return: ``QGraphicsView`` attached to the `Scene`
        :rtype: ``QGraphicsView``
        """
        return self.scene_graphic.views()[0]

    def getItemAt(self, pos):
        """Shortcut for retrieving item at provided `Scene` position

        :param pos: scene position
        :type pos: ``QPointF``
        :return: Qt Graphics Item at scene position
        :rtype: ``QGraphicsItem``
        """
        return self.getView().itemAt(pos)      
    
    def addNode(self, node):
        """Add :class:`~GUI.node_creator.NodeConfig` to this `Scene`

        :param node: :class:`~GUI.node_creator.NodeConfig` to be added to this `Scene`
        :type node: :class:`~GUI.node_creator.NodeConfig`
        """
        self.hint = False
        self.nodes.append(node)

    def addEdge(self, edge):
        """Add :class:`~GUI.node_creator.EdgeConfig` to this `Scene`

        :param edge: :class:`~GUI.node_creator.EdgeConfig` to be added to this `Scene`
        :return: :class:`~GUI.node_creator.EdgeConfig`
        """
        self.edges.append(edge)

    def removeNode(self, node):
        """Remove :class:`~GUI.node_creator.NodeConfig` from this `Scene`

        :param node: :class:`~GUI.node_creator.NodeConfig` to be removed from this `Scene`
        :type node: :class:`~GUI.node_creator.NodeConfig`
        """
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            if DEBUG_REMOVE_WARNING: print ("!W", "Scene::removeNode", "wanna remove nodee", node, "from self.nodes but not inside list")
    
    def removeEdge(self,edge):
        """Remove :class:`~GUI.node_creator.EdgeConfig` from this `Scene`

        :param edge: :class:`~GUI.node_creator.EdgeConfig` to be remove from this `Scene`
        :return: :class:`~GUI.node_creator.EdgeConfig`
        """
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNING: print ("!W", "Scene::removeEdge", "wanna remove edge", edge, "from self.edges but not inside list")

    def clear(self):
        """Remove all `Nodes` from this `Scene`. This will also remove all related `Edges`"""
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

    def saveToFile(self, filename):
        """
        Save this `Scene` to the file on disk.

        :param filename: where to save this scene
        :type filename: ``str``
        """
        with open(filename, "w") as file:   # file will close automatically after exec
            file.write(json.dumps(self.serialize(), indent=4)) #convert to json str and spacing 4
            if DEBUG: print ("saving to ", filename," was successfull")

            self.has_been_modified = False

    def loadFromFile(self, filename):
        """
        Load `Scene` from a file on disk

        :param filename: from what file to load the `Scene`
        :type filename: ``str``
        :raises: :class:`~InvalidFile` if there was an error decoding JSON file
        """
        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf-8')
                self.deserialize(data)
                self.has_been_modified = False
            except Exception as e: 
                if DEBUG: print (e)
                raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))

    def getEdgeClass(self):
        """Return the class representing Edge. Override me with custom edge type class if needed"""
        return node_creator.EdgeConfig

    def setNodeClassSelector(self, class_selecting_function):
        """
        Set the function which decides what `Node` class to instantiate when deserializing `Scene`.
        If not set, we will always instantiate :class:`~GUI.node_creator.NodeConfig` for each `Node` in the `Scene`

        :param class_selecting_function: function which returns `Node` class type (not instance) from `Node` serialized ``dict`` data
        :type class_selecting_function: ``function``
        :return: Class Type of `Node` to be instantiated during deserialization
        :rtype: `Node` class type
        """
        # when function self.node_class_selector is set, use different node class
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data):
        """
        Takes `Node` serialized data and determines which `Node Class` to instantiate according the description
        in the serialized Node

        :param data: serialized `Node` object data
        :type data: ``dict``
        :return: Instance of `Node` class to be used in this Scene
        :rtype: `Node` class instance
        """
        return node_creator.NodeConfig if self.node_class_selector is None else self.node_class_selector(data)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        # format: create ordered dictionary class and assign key:value as tuple inside list
        return OrderedDict([    
            ('id', self.id),
            ('scene_width', self.width),
            ('scene_height', self.height),
            ('nodes', nodes),
            ('edges', edges),
        ])
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        hashmap = {}

        if restore_id:
            self.id = data['id']

        # -- deserialize NODES

        ## Instead of recreating all the nodes, reuse existing ones...
        # get list of all current nodes:
        all_nodes = self.nodes[:]   # python 2.7 doesn't support list.copy() use slicing instead

        # go through deserialized nodes:
        for node_data in data['nodes']:
            # can we find this node in the scene?
            found = False
            for node in all_nodes:
                if node.id == node_data['id']:
                    found = node
                    break

            if not found:
                new_node = self.getNodeClassFromData(node_data)(scene=self)
                new_node.deserialize(node_data, hashmap, restore_id)
                new_node.onDeserialized(node_data)
                # print("New node for", node_data['title'])
                
            else:
                found.deserialize(node_data, hashmap, restore_id)
                found.onDeserialized(node_data)
                all_nodes.remove(found)
                # print("Reused", node_data['title'])

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_nodes != []:
            node = all_nodes.pop()
            node.remove()

        # -- deserialize EDGES

        ## Instead of recreating all the edges, reuse existing ones...
        # get list of all current edges:
        all_edges = self.edges[:]   # python 2.7 doesn't support list.copy() use slicing instead


        # go through deserialized edges:
        for edge_data in data['edges']:
            # can we find this node in the scene?
            found = False
            for edge in all_edges:
                if edge.id == edge_data['id']:
                    found = edge
                    break

            if not found:
                new_edge = node_creator.EdgeConfig(self).deserialize(edge_data, hashmap, restore_id)
                # print("New edge for", edge_data)
            else:
                found.deserialize(edge_data, hashmap, restore_id)
                all_edges.remove(found)

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_edges != []:
            edge = all_edges.pop()
            edge.remove()

        return True

# override parent class, watch for function name also is important    
class GraphicsScene(QtWidgets.QGraphicsScene):
    """Class representing Graphic of :class:`~GUI.node_editor.GraphicsScene`"""
    itemSelected = QtCore.Signal()
    itemsDeselected = QtCore.Signal()

    def __init__(self, scene, parent=None):
        """
        :param scene: reference to the :class:`~Scene`
        :type scene: :class:`~Scene`
        :param parent: parent widget
        :type parent: QWidget
        """
        super(GraphicsScene, self).__init__(parent)
        
        self.scene = scene

        # There is an issue when reconnecting edges -> mouseMove and trying to delete/remove them
        # the edges stayed in the scene in Qt, however python side was deleted
        # this caused a lot of troubles...
        #
        # https://bugreports.qt.io/browse/QTBUG-18021
        # https://bugreports.qt.io/browse/QTBUG-50691
        # Affected versions: 4.7.1, 4.7.2, 4.8.0, 5.5.1, 5.7.0
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)      

        # grid settings
        self.grid_size = 30
        self.grid_squares = 4
        
        self.color_background = QtGui.QColor("#303030") # blue color > QtGui.QColor("#222933")
        self.color_light = QtGui.QColor("#606060") # old > QtGui.QColor("#2f2f2f")
        self.color_dark = QtGui.QColor("#151515") # old > QtGui.QColor("#303030")
        
        self.pen_light = QtGui.QPen(self.color_light)
        self.pen_light.setWidthF(0.2)
        self.pen_dark = QtGui.QPen(self.color_dark)
        self.pen_dark.setWidthF(0.75)

        # hint asset
        self._color_hint = QtGui.QColor("#757575")
        self._pen_hint = QtGui.QPen(self._color_hint)
        self._font_hint = QtGui.QFont("Ubuntu", 10)
        
        self.setBackgroundBrush(self.color_background)

    # overriden this dragMoveEvent to allowed drop events inside graphic view
    def dragMoveEvent(self, event):
        """Overriden Qt's dragMoveEvent to enable Qt's Drag Events"""
        pass
    
    def setGraphicScene(self, width, height):
        """Set `width` and `height` of the `Graphics Scene`"""
        self.setSceneRect(-width/2, -height/2, width, height)

    def drawBackground(self, painter, rect):
        """Draw background scene grid"""
        super(GraphicsScene, self).drawBackground(painter, rect)
        
        # calculate line and draw line
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))
        
        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)
        lines_light, lines_dark = [], []

        for x in range(first_left, right, self.grid_size):
            if (x % (self.grid_size*self.grid_squares) != 0): lines_light.append(QtCore.QLine(x, top, x, bottom))
            else: lines_dark.append(QtCore.QLine(x, top, x, bottom))
        
        for y in range(first_top, bottom, self.grid_size):
            if (y % (self.grid_size*self.grid_squares) != 0): lines_light.append(QtCore.QLine(left, y, right, y))
            else: lines_dark.append(QtCore.QLine(left, y, right, y))
            
        painter.setPen(self.pen_light)
        painter.drawLines(lines_light)
        
        painter.setPen(self.pen_dark)
        painter.drawLines(lines_dark)
        
        if self.scene.hint:
            painter.setFont(self._font_hint)
            painter.setPen(self._pen_hint)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            offset = 14
            rect_state = QtCore.QRect(rect.x(), rect.y(), rect.width()+2*offset, rect.height()+2*offset)
            painter.drawText(rect_state, QtCore.Qt.AlignCenter, "Right Click to create a node")
    
        '''
        for x in range(first_left, right, self.grid_size):
            for y in range(first_top, bottom, self.grid_size):
                painter.drawPoint(x,y)
        '''

# manage navigation inside editor and GUI display
class GraphicsView(QtWidgets.QGraphicsView):
    """Class representing NodeEditor's `Graphics View`"""
    scenePosChanged = QtCore.Signal(int, int)

    def __init__(self, scene_graphic, parent=None):
        """
        :param scene_graphic: reference to the :class:`~GraphicsScene`
        :type scene_graphic: :class:`~GraphicsScene`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **scene_graphic** - reference to the :class:`~GraphicsScene`
        - **mode** - state of the `Graphics View`
        - **zoomInFactor**- ``float`` - zoom step scaling, default 1.25
        - **zoomClamp** - ``bool`` - clamp zooming or limitless zooming
        - **zoom** - current zoom step
        - **zoomStep** - ``int`` - the relative zoom step when zooming in/out
        - **zoomRange** - ``[min, max]``

        """
        super(GraphicsView, self).__init__()
    
        # setup
        self.scene_graphic = scene_graphic
        self.initUI()
        self.setScene(self.scene_graphic)

        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        # edge dragging features
        self.dragging = edge_dragging.EdgeDragging(self)

        # edges re-routing
        self.rerouting = node_features.EdgeRerouting(self)

        # edges snaping
        self.snapping = node_features.EdgeSnapping(self, snapping_radius=EDGE_SNAPPING_RADIUS)
        
        # cutline features
        self.cutline = node_features.CutLine()
        self.scene_graphic.addItem(self.cutline)

        self.last_scene_mouse_position = QtCore.QPoint(0,0)
        self.zoom_in_factor = 1.25
        self.zoom_clamp = True
        self.zoom = 5
        self.zoom_step = 1
        self.zoom_range = [0, 10]

        # listeners 
        self._drag_enter_listeners = []
        self._drop_listeners = []
        self._delete_listeners = []
        self._state_listeners = []

        self.mode = MODE_NO_OPERATION
    
    def initUI(self):
        """Set up this ``QGraphicsView``"""
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setRenderHints(QtGui.QPainter.HighQualityAntialiasing)
        self.setRenderHints(QtGui.QPainter.TextAntialiasing)
        self.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
        
        self.setViewportUpdateMode(GraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        # enable dropping item on view
        self.setAcceptDrops(True)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        for callback in self._state_listeners: callback(value)

    def isSnappingEnabled(self, event=None):
        """Returns ``True`` if snapping is enabled"""
        return EDGE_SNAPPING and (event.modifiers() & QtCore.Qt.CTRL) if event else True

    def resetMode(self):
        """Helper function to reset the graphic view state machine to the default"""
        self.mode = MODE_NO_OPERATION

    def dragEnterEvent(self, event):
        """Trigger our registered `Drag Enter` events"""
        for callback in self._drag_enter_listeners: callback(event)

    def dropEvent(self, event):
        """Trigger our registered `Drop` events"""
        for callback in self._drop_listeners: callback(event)

    def deleteEvent(self, event):
        """Trigger our registered `Delete` events"""
        for callback in self._delete_listeners: callback(event)

    def addDragEnterListener(self, callback):
        """
        Register callback for `Drag Enter` event

        :param callback: callback function
        """
        self._drag_enter_listeners.append(callback)
    
    def addDropListener(self, callback):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self._drop_listeners.append(callback)

    def addDeleteListener(self, callback):
        """
        Register callback for `Delete` event

        :param callback: callback function
        """
        self._delete_listeners.append(callback)
    
    def addStateListener(self, callback):
        """
        Register callback for `Mode changed` event

        :param callback: callback function
        """
        self._state_listeners.append(callback)
    
    def mousePressEvent(self, event):
        """Dispatch Qt's mousePress event to corresponding function below"""
        if event.button() == QtCore.Qt.MiddleButton:
            self.middleMouseButtonPressEvent(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonPressEvent(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressEvent(event)
        else:
            super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Dispatch Qt's mouseRelease event to corresponding function below"""
        if event.button() == QtCore.Qt.MiddleButton:
            self.middleMouseButtonReleaseEvent(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonReleaseEvent(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonReleaseEvent(event)
        else:
            super(GraphicsView, self).mouseReleaseEvent(event)

    def middleMouseButtonPressEvent(self, event):
        """When Middle mouse button was pressed"""
        
        item = self.getItemAtClick(event)

        # debug print out
        if DEBUG_MMB_SCENE_ITEMS: 
            if isinstance(item, node_creator.EdgeGraphics):
                print ("MMB DEBUG: ", item.edge, "\n\t", item.edge.edge_graphic if item.edge.edge_graphic is not None else None)
                return
            
            if isinstance(item, node_creator.SocketGraphics):
                print ("MMB DEBUG: ", item.socket, "socket_type:", item.socket.socket_type,
                       "has edges:", "no" if item.socket.edges == [] else "")
                if item.socket.edges:
                    for edge in item.socket.edges: print("\t", edge)
                return
        
        if DEBUG_MMB_SCENE_ITEMS and (item is None or self.mode == MODE_EDGE_REROUTING):
            print("SCENE:")
            print(" Nodes:")
            for node in self.scene_graphic.scene.nodes: print("\t", node)
            print(" Edges:")
            for edge in self.scene_graphic.scene.edges: print("\t", edge, "\n\t\t edge_graphic:", edge.edge_graphic if edge.edge_graphic is not None else None)

            if event.modifiers() & QtCore.Qt.CTRL:
                print(" Graphic Items in GraphicScene:")
                for item in self.scene_graphic.items():
                    print('     ', item)

        if DEBUG_MMB_LAST_SELECTIONS and event.modifiers() & QtCore.Qt.SHIFT:
            print("Scene _last_Selected_items:", self.scene_graphic.scene._last_selected_items)
            return
                                
        # faking events for enable MMB dragging the scene
        release_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, 
                                       event.localPos(), 
                                       event.screenPos(), 
                                       QtCore.Qt.LeftButton,
                                       QtCore.Qt.NoButton,
                                       event.modifiers())
        super(GraphicsView, self).mouseReleaseEvent(release_event)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        fake_event = QtGui.QMouseEvent(event.type(),
                                       event.localPos(),
                                       event.screenPos(),
                                       QtCore.Qt.MiddleButton,
                                       event.buttons() or QtCore.Qt.LeftButton,
                                       event.modifiers())
        super(GraphicsView, self).mousePressEvent(release_event)
        
    def middleMouseButtonReleaseEvent(self, event):
        """When Middle mouse button was released"""
        fake_event = QtGui.QMouseEvent(event.type(),
                                       event.localPos(),
                                       event.screenPos(),
                                       QtCore.Qt.LeftButton,
                                       event.buttons() and QtCore.Qt.LeftButton,
                                       event.modifiers())
        super(GraphicsView, self).mouseReleaseEvent(fake_event)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
    
    def leftMouseButtonPressEvent(self, event):
        """When Left  mouse button was pressed"""
        # get item which user clicked on
        item = self.getItemAtClick(event)
        self.last_item_clicked = item

        #if DEBUG: print ("LMB Click on", item, self.debug_modifiers(event))
        
        if hasattr(item, "node") or isinstance(item, node_creator.EdgeGraphics) or item is None:
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, 
                                              event.localPos(),
                                              event.screenPos(),
                                              QtCore.Qt.LeftButton,
                                              event.buttons() | QtCore.Qt.LeftButton,
                                              event.modifiers() | QtCore.Qt.ControlModifier)
                super(GraphicsView,self).mousePressEvent(fakeEvent)
                return

        # support for start drag by snapping ,even tho mouse is not overlap with socket
        if self.isSnappingEnabled(event):
            if DEBUG_STATE: print ("snapping highlight")
            item = self.snapping.getSnappedSocketItem(event)
            self.last_item_clicked = item

        if isinstance(item, node_creator.SocketGraphics):
            if self.mode == MODE_NO_OPERATION and event.modifiers() & QtCore.Qt.CTRL:
                socket = item.socket
                if socket.hasAnyEdge():
                    if DEBUG_STATE: print ("found edge, start rerouting")
                    self.mode = MODE_EDGE_REROUTING
                    self.rerouting.startRerouting(socket)
                    return

            if self.mode == MODE_NO_OPERATION:
                if DEBUG_STATE: print ("start drag")
                self.mode = MODE_EDGE_DRAG
                self.dragging.edgeDragStart(item)
                return  # stop mouse event, so it doesn't include upper level obj (ex. node)

        if self.mode == MODE_EDGE_DRAG:
            if DEBUG_STATE: print ("Debug catch")
            result = self.dragging.edgeDragEnd(item)
            if result: return

        if item is None:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                if DEBUG_STATE: print ("cutline")
                self.mode = MODE_EDGE_CUT
                fakeEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                              event.localPos(),
                                              event.screenPos(),
                                              QtCore.Qt.LeftButton,
                                              QtCore.Qt.NoButton,
                                              event.modifiers())
                super(GraphicsView, self).mouseReleaseEvent(fakeEvent)
                self.setCursor(QtCore.Qt.CrossCursor)
                #QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
                return
            else:
                if DEBUG_STATE: print ("rubber selection")
                self.rubberBandDraggingRectangle = True

        super(GraphicsView, self).mousePressEvent(event)

    def leftMouseButtonReleaseEvent(self, event):
        """When Left  mouse button was released"""
        # get item which user released on
        item = self.getItemAtClick(event)

        try:
            if hasattr(item, "node") or isinstance(item, node_creator.EdgeGraphics) or item is None:
                if event.modifiers() & QtCore.Qt.ShiftModifier:
                    event.ignore()
                    fakeEvent = QtGui.QMouseEvent(event.type(), 
                                                event.localPos(),
                                                event.screenPos(),
                                                QtCore.Qt.LeftButton,
                                                QtCore.Qt.NoButton,
                                                event.modifiers() | QtCore.Qt.ControlModifier)
                    super(GraphicsView,self).mouseReleaseEvent(fakeEvent)
                    return

            if self.mode == MODE_EDGE_DRAG:
                if id(item) != id(self.last_item_clicked):
                    if self.isSnappingEnabled(event):
                        item = self.snapping.getSnappedSocketItem(event)

                    result = self.dragging.edgeDragEnd(item)
                    if result: return
                else:
                    if DEBUG: print("Try connecting to same socket > not valid!")
                    result = self.dragging.edgeDragEnd(item)
                    if result: return
                # self.mode = MODE_NO_OPERATION (edgeDragEnd already resetmode)
            
            if self.mode == MODE_EDGE_REROUTING:
                if self.isSnappingEnabled(event):
                    item = self.snapping.getSnappedSocketItem(event)

                if not EDGE_REROUTING_UE:
                    # version 2 -- more consistent with the node editor?
                    if not self.rerouting.first_mb_release:
                        # for confirmation of first mouse button release
                        self.rerouting.first_mb_release = True
                        # skip any rerouting until first MB was released
                        return
                    
                self.rerouting.stopRerouting(item.socket if isinstance(item, node_creator.SocketGraphics) else None)
                        
                self.mode = MODE_NO_OPERATION

            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdge()
                self.cutline.line_points = []
                self.cutline.update()
                self.setCursor(QtCore.Qt.ArrowCursor)
                #QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor) # sometime 1 line don't evaluate? bug?
                self.mode = MODE_NO_OPERATION
                return

            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.scene_graphic.selectedItems()
                
                if current_selected_items != self.scene_graphic.scene._last_selected_items:
                    if current_selected_items == []:
                        self.scene_graphic.itemsDeselected.emit()
                    else:
                        self.scene_graphic.itemSelected.emit()
                    self.scene_graphic.scene._last_selected_items = current_selected_items
                
                # the rubber band rectangle doesn't dissapear without handling the event (when mouse static after dragging)
                super(GraphicsView, self).mouseReleaseEvent(event)
                return

            # otherwise deselect everything
            if item is None:
                self.scene_graphic.itemsDeselected.emit()
            
        except Exception as e: print("ERROR: ", e)

        super(GraphicsView, self).mouseReleaseEvent(event)

    def rightMouseButtonPressEvent(self, event):
        """When Right mouse button was pressed"""
        super(GraphicsView, self).mousePressEvent(event)

    def rightMouseButtonReleaseEvent(self, event):
        """When Right mouse button was release"""

        ## cannot be because with dragging RMB we spawn create new node context menu
        ## However, can be used if you want to cancel with RMB
        # if self.mode == MODE_EDGE_DRAG:
        #     self.dragging.edgeDragEnd(None)
        #     return

        super(GraphicsView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Overriden Qt's ``mouseMoveEvent`` handling Scene/View logic"""
        scenepos = self.mapToScene(event.pos())

        try:
            modified = self.setSocketHighlights(scenepos, highlighted=False, radius=EDGE_SNAPPING_RADIUS+100)   # bigger radius so it detect far enough socket
            if self.isSnappingEnabled(event) and self.mode != MODE_EDGE_CUT:
                # scenepos will overwrite scenepos value of mouse movement to nearest socket
                # therefore when flow continue to next condition (if self.mode == MODE_EDGE_DRAG), it have snap effect
                _, scenepos = self.snapping.getSnappedToSocketPosition(scenepos)    # notice underscore variable before scenepos
            if modified: self.update()  # force graphic view to redraw every time socket highlight by distance triggered

            if self.mode == MODE_EDGE_DRAG:
                self.dragging.updateDestination(scenepos.x(), scenepos.y())

            if self.mode == MODE_EDGE_REROUTING:
                self.rerouting.updateScenePos(scenepos.x(), scenepos.y())

            if self.mode == MODE_EDGE_CUT and self.cutline is not None:
                self.cutline.line_points.append(scenepos)
                self.cutline.update()
                
        except Exception as e: print(e)

        self.last_scene_mouse_position = scenepos

        self.scenePosChanged.emit(int(scenepos.x()), int(scenepos.y()))

        super(GraphicsView, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        """
        .. note::
            This overridden Qt's method was used for handling key shortcuts, before we implemented proper
            ``QWindow`` with Actions and Menu. Still the commented code serves as an example on how to handle
            key presses without Qt's framework for Actions and shortcuts. There is also an example on
            how to solve the problem when a Node contains Text/LineEdit and we press the `Delete`
            key (also serving to delete `Node`)

        :param event: Qt's Key event
        :type event: ``QKeyEvent``
        :return:
        """
        #super(GraphicsView,self).keyPressEvent(event)  # called this can transfer key press to maya app (not wanted)

        if event.key() == QtCore.Qt.Key_A and event.modifiers() & QtCore.Qt.ShiftModifier:
            items = [item for item in self.scene_graphic.scene.getSelectedItems() if isinstance(item, node_creator.NodeGraphics)]
            if len(items)>1:
                minimum_x = min([item.node.pos.x() for item in items])
                for item in items: 
                    item.node.setPos(minimum_x, item.node.pos.y())
                    item.node.updateConnectedEdges()
                self.scene_graphic.scene.history.storeHistory("align nodes to the left", setModified=True)

        if event.key() == QtCore.Qt.Key_D and event.modifiers() & QtCore.Qt.ShiftModifier:
            items = [item for item in self.scene_graphic.scene.getSelectedItems() if isinstance(item, node_creator.NodeGraphics)]
            if len(items)>1:
                maximum_x = max([item.node.pos.x() for item in items])
                for item in items: 
                    item.node.setPos(maximum_x, item.node.pos.y())
                    item.node.updateConnectedEdges()
                self.scene_graphic.scene.history.storeHistory("align nodes to the right", setModified=True)

    def cutIntersectingEdge(self):
        """Compare which `Edges` intersect with current `Cut line` and delete them safely"""
        for i in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[i]
            p2 = self.cutline.line_points[i + 1]

            for edge in self.scene_graphic.scene.edges:
                if edge.edge_graphic.intersectsWith(p1, p2):
                    edge.remove()
        self.scene_graphic.scene.history.storeHistory("delete edges", setModified=True)

    def setSocketHighlights(self, scenepos, highlighted, radius):
        """set/disable socket highlights in scene area defined by `scenepos` and `radius"""
        scan_rect = QtCore.QRectF(scenepos.x()-radius ,scenepos.y()-radius, radius*2, radius*2)
        items = self.scene_graphic.items(scan_rect)
        items = list(filter(lambda x: isinstance(x, node_creator.SocketGraphics), items))
        for socket_graphic in items: socket_graphic.isHighlighted = highlighted
        return items

    def deleteSelected(self):
        """Shortcut for safe deleting every object selected in the `Scene`."""
        for item in self.scene_graphic.selectedItems():
            if isinstance(item, node_creator.EdgeGraphics):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
                self.deleteEvent(item.node)

        self.scene_graphic.scene.history.storeHistory("delete selection", setModified=True)

    def debug_modifiers(self, event):
        """Helper function get string if we hold Ctrl, Shift or Alt modifier keys"""
        out = "modifier: "
        if event.modifiers() & QtCore.Qt.ShiftModifier: out += "Shift "
        if event.modifiers() & QtCore.Qt.ControlModifier: out += "Control "
        if event.modifiers() & QtCore.Qt.AltModifier: out += "Alt "
        return out 

    def getItemAtClick(self, event):
        """Return the object on which we've clicked/release mouse button

        :param event: Qt's mouse or key event
        :type event: ``QEvent``
        :return: ``QGraphicsItem`` which the mouse event happened or ``None``
        """
        # return object on which user clicked/release 
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
    
    def wheelEvent(self, event):  
        """overridden Qt's ``wheelEvent``. This handles zooming""" 
        zoom_out_factor = 1/self.zoom_in_factor
        
        # calculate zoom
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step
        
        clamped = False
        if self.zoom < self.zoom_range[0]: self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]: self.zoom, clamped = self.zoom_range[1], True
        
        if not clamped or self.zoom_clamp == False:
            self.scale(zoom_factor, zoom_factor)

class NodeEditorWidget(QtWidgets.QWidget):
    """The ``NodeEditorWidget`` class"""
    Scene_class = Scene
    GraphicsView_class = GraphicsView
    
    def __init__(self, parent=None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **filename** - currently graph's filename or ``None``
        """
        super(NodeEditorWidget ,self).__init__()

        self.file_name = None

        self.initUI()

    def initUI(self):
        """Set up this ``NodeEditorWidget`` with its layout,  :class:`~Scene` and
        :class:`~GraphicsView`"""
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        # create graphic scene
        self.scene = self.__class__.Scene_class()

        # create graphics view
        self.view = self.__class__.GraphicsView_class(self.scene.scene_graphic)
        self.layout.addWidget(self.view)
        
        # early bug fix > fix before video reach the solution, might need modified (kinda lame)
        self.scene.history.storeHistory("")
        # DEBUG
        #self.add_debug_content()
    
    def isModified(self):
        """Has the `Scene` been modified?

        :return: ``True`` if the `Scene` has been modified
        :rtype: ``bool``
        """
        return self.scene.isModified()

    def isFilenameSet(self):
        """Do we have a graph loaded from file or are we creating a new one?

        :return: ``True`` if filename is set. ``False`` if it is a new graph not yet saved to a file
        :rtype: ''bool''
        """
        return self.file_name is not None
    
    def getSelectedItems(self):
        """Shortcut returning `Scene`'s currently selected items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.scene.getSelectedItems()

    def hasSelectedItems(self):
        """Is there something selected in the :class:`Scene`?

        :return: ``True`` if there is something selected in the `Scene`
        :rtype: ``bool``
        """
        return self.getSelectedItems() != []
    
    def canUndo(self):
        """Can Undo be performed right now?

        :return: ``True`` if we can undo
        :rtype: ``bool``
        """
        return self.scene.history.canUndo()
    
    def canRedo(self):
        """Can Redo be performed right now?

        :return: ``True`` if we can redo
        :rtype: ``bool``
        """
        return self.scene.history.canRedo()
    
    def getUserFriendlyFilename(self):
        """Get user friendly filename (cut directory path). Used in the window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.file_name) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "") 
    
    def fileNew(self):
        """Empty the scene (create new file)"""
        self.scene.clear()
        self.file_name = None
        # clear history
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename):
        """Load serialized graph from JSON file

        :param filename: file to load
        :type filename: ``str``
        """
        self.setCursor(QtCore.Qt.WaitCursor)
        #QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.file_name = filename
            # clear history
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except InvalidFile as e:
            if DEBUG: print (e)
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.warning(self, "Error loading %s" %os.path.basename(filename), str(e))
            return False
        finally: 
            self.setCursor(QtCore.Qt.ArrowCursor)
            #QtWidgets.QApplication.restoreOverrideCursor()
    
    def fileSave(self, filename=None):
        """Save serialized graph to JSON file. When called with an empty parameter, we won't store/remember the filename.

        :param filename: file to store the graph
        :type filename: ``str``
        """
        # when called with empty argument, don't store filename
        if filename is not None: self.file_name = filename
        self.setCursor(QtCore.Qt.WaitCursor)
        #QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.scene.saveToFile(self.file_name)
        self.setCursor(QtCore.Qt.ArrowCursor)
        #QtWidgets.QApplication.restoreOverrideCursor()
        return True

    def add_debug_content(self):
        """Testing method to put random QGraphicsItems and elements into QGraphicsScene"""
        green_brush = QtGui.QBrush(QtCore.Qt.green)
        outline_pen =  QtGui.QPen(QtCore.Qt.black)
        outline_pen.setWidth(2)
        
        rect = self.scene_graphic.addRect(4000, 4000, 100, 100, outline_pen, green_brush)
        rect.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

# main window to hold all GUI element
class NodeEditorWindow(QtWidgets.QMainWindow):
    """Class representing NodeEditor's Main Window"""
    NodeEditorWidget_class = NodeEditorWidget

    def __init__(self, parent=None):
        """
        :Instance Attributes:

        - **name_company** - name of the company, used for permanent profile settings
        - **name_product** - name of this App, used for permanent profile settings
        """
        super(NodeEditorWindow ,self).__init__(parent)

        # create custom clipboard (different from desktop clipboard)
        self.clipboard = "" # early bug fix > search self.clipboard for other changes (inside this class only not including inside scene class)

        self.initUI()

    def initUI(self):
        """Set up this ``QMainWindow``. Create :class:`~GUI.node_editor.NodeEditorWidget`, Actions and Menus"""
        self.createActions()
        self.createMenus()

        # create node editor widget
        self.node_editor = self.__class__.NodeEditorWidget_class(self)
        self.node_editor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.node_editor)
        
        self.createStatusBar()

        # set window properties
        self.setTitle()

    def sizeHint(self):
        """Override function, suggest Qt widget using specific qsize below"""
        return QtCore.QSize(800, 600)   # appear with given size, in middle of screen

    def createStatusBar(self):
        """Create Status bar and connect to `Graphics View` scenePosChanged event"""
        self.statusBar().showMessage("")
        self.status_mouse_pos = QtWidgets.QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        # scenePosChanged (pyside2 custom signal function) will trigger the connected function
        self.node_editor.view.scenePosChanged.connect(self.onScenePosChanged)

    def createActions(self):
        """Create basic `File` and `Edit` actions"""
        self.actNew = QtWidgets.QAction('New', self, shortcut='Ctrl+N', statusTip='Create new graph',  triggered=self.onFileNew)
        self.actOpen = QtWidgets.QAction('Open', self, shortcut='Ctrl+O', statusTip='Open Graph', triggered=self.onFileOpen)
        self.actSave = QtWidgets.QAction('Save', self, shortcut='Ctrl+S', statusTip='Save Graph', triggered=self.onFileSave)
        self.actSaveAs = QtWidgets.QAction('Save As...', self, shortcut='Ctrl+Shift+S', statusTip='Save Graph As', triggered=self.onFileSaveAs)
        self.actExit = QtWidgets.QAction('Exit', self, shortcut='Ctrl+Q', statusTip='Exit Editor', triggered=self.close)

        self.actUndo = QtWidgets.QAction('Undo', self, shortcut='Ctrl+Z', statusTip='Undo Last Operation', triggered=self.onEditUndo)
        self.actRedo = QtWidgets.QAction('Redo', self, shortcut='Ctrl+Shift+Z', statusTip='Redo Last Operation', triggered=self.onEditRedo)
        self.actCut = QtWidgets.QAction('Cut', self, shortcut='Ctrl+X', statusTip='Cut to clipboard', triggered=self.onEditCut)
        self.actCopy = QtWidgets.QAction('Copy', self, shortcut='Ctrl+C', statusTip='Copy to clipboard', triggered=self.onEditCopy)
        self.actPaste = QtWidgets.QAction('Paste', self, shortcut='Ctrl+V', statusTip='Paste to clipboard', triggered=self.onEditPaste)
        self.actDelete = QtWidgets.QAction('Delete', self, shortcut='Del', statusTip='Delete selected items', triggered=self.onEditDelete)

    def createMenus(self):
        """Create Menus for `File` and `Edit`"""
        self.createFileMenu()
        self.createEditMenu()

    def createFileMenu(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")
        self.file_menu.addAction(self.actNew)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actOpen)
        self.file_menu.addAction(self.actSave)
        self.file_menu.addAction(self.actSaveAs)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actExit)

    def createEditMenu(self):
        menubar = self.menuBar()
        self.edit_menu = menubar.addMenu("Edit")
        self.edit_menu.addAction(self.actUndo)
        self.edit_menu.addAction(self.actRedo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actCut)
        self.edit_menu.addAction(self.actCopy)
        self.edit_menu.addAction(self.actPaste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actDelete)

    def setTitle(self):
        """Function responsible for setting window title"""
        title = "Zeno Node Editor - "   
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)

    def closeEvent(self, event):
        """Handle close event. Ask before we loose work"""
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        """Has current :class:`~Scene` been modified?

        :return: ``True`` if current :class:`~Scene` has been modified
        :rtype: ``bool``
        """
        return self.getCurrentNodeEditorWidget().scene.isModified()
    
    def getCurrentNodeEditorWidget(self):
        """get current :class:`~NodeEditorWidget`

        :return: get current :class:`~NodeEditorWidget`
        :rtype: :class:`~NodeEditorWidget`
        """
        return self.centralWidget()

    def maybeSave(self): 
        """If current `Scene` is modified, ask a dialog to save the changes. Used before
        closing window / mdi child document

        :return: ``True`` if we can continue in the `Close Event` and shutdown. ``False`` if we should cancel
        :rtype: ``bool``
        """
        if not self.isModified():
            return True

        result = QtWidgets.QMessageBox.warning(self, 
                                               "Save Node Scene?",
                                               "The Editor has beed modified.\n Do you want to save your changes?",
                                               QtWidgets.QMessageBox.Save | 
                                               QtWidgets.QMessageBox.Discard | 
                                               QtWidgets.QMessageBox.Cancel
                                               )

        if result == QtWidgets.QMessageBox.Save:
            return self.onFileSave()
        elif result == QtWidgets.QMessageBox.Cancel:
            return False
        return True

    def onScenePosChanged(self, x, y):
        """Handle event when cursor position changed on the `Scene`

        :param x: new cursor x position
        :type x:
        :param y: new cursor y position
        :type y:
        """
        self.status_mouse_pos.setText("Scene Pos: [ %d, %d]"%(x, y))

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''
    
    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def onFileNew(self):
        """Hande File New operation"""
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().scene.clear()
            self.getCurrentNodeEditorWidget().file_name = None
            self.setTitle()

    def onFileOpen(self):
        """Handle File Open operation"""
        if self.maybeSave():
            fname, filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())
            if fname == '':
                return
            if os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)

    def onFileSave(self):
        """Handle File Save operation"""
        current_node_editor = self.getCurrentNodeEditorWidget()
        if current_node_editor is not None: 
            if not current_node_editor.isFilenameSet(): return self.onFileSaveAs()

            current_node_editor.fileSave()
            self.statusBar().showMessage("Successfully saved %s" %current_node_editor.file_name, 5000)
           
            # support for MDI app
            if hasattr(current_node_editor, "setTitle"): current_node_editor.setTitle()
            else: self.setTitle()
            return True

    def onFileSaveAs(self):
        """Handle File Save As operation"""
        current_node_editor = self.getCurrentNodeEditorWidget()
        if current_node_editor is not None:
            fname, filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(), self.getFileDialogFilter())
            if fname == '': return False

            current_node_editor.fileSave(fname)
            self.statusBar().showMessage("Successfully saved as %s" %current_node_editor.file_name, 5000)
            
            # support for MDI app (if)
            if hasattr(current_node_editor, "setTitle"): current_node_editor.setTitle()
            else: self.setTitle()
            return True

    def onEditUndo(self):
        """Handle Edit Undo operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        """Handle Edit Redo operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        """Handle Delete Selected operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self):
        """Handle Edit Cut to clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            # QtWidgets.QApplication.instance().clipboard.setText(str_data)
            self.clipboard = str_data

    def onEditCopy(self):
        """Handle Edit Copy to clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            # QtWidgets.QApplication.instance().clipboard().setText(str_data)
            self.clipboard = str_data

    def onEditPaste(self):
        """Handle Edit Paste from clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            #raw_data = QtWidgets.QApplication.instance().clipboard().text()
            raw_data = self.clipboard

            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Pasting of not valid json data!", e)
                return
            
            # check if json data valid 
            if 'nodes' not in data:
                print("JSON does not contain any nodes!")
                return

            return self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        """Read the permanent profile settings for this app"""
        settings = QtCore.QSettings(self.author, self.product_name)
        pos = settings.value('pos', QtCore.QPoint(200, 200))
        size = settings.value('size', QtCore.QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        """Write the permanent profile settings for this app"""
        settings = QtCore.QSettings(self.author, self.product_name)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
    
class SceneHistory():
    """Class contains all the code for undo/redo operations"""
    def __init__(self, scene):
        """
        :param scene: Reference to the :class:`~GUI.node_editor.Scene`
        :type scene: :class:`~GUI.node_editor.Scene`

        :Instance Attributes:

        - **scene** - reference to the :class:`~GUI.node_editor.Scene`
        - **history_limit** - number of history steps that can be stored
        """
        self.scene = scene

        self.clear()
        self.history_limit = 50

        self.undo_selection_has_changed = False

        # listeners
        self._history_modified_listeners = []
        self._history_stored_listeners = []
        self._history_restored_listeners = []

    def clear(self):
        """Reset the history stack"""
        self.history_stack = []
        self.history_current_step = -1

    def storeInitialHistoryStamp(self):
        """Helper function usually used when new or open file requested"""
        self.storeHistory("Initial History Stamp")

    def addHistoryModifiedListener(self, callback):
        """
        Register callback for `HistoryModified` event

        :param callback: callback function
        """
        self._history_modified_listeners.append(callback)

    def addHistoryStoredListener(self, callback):
        """
        Register callback for `HistoryStored` event

        :param callback: callback function
        """
        self._history_stored_listeners.append(callback)

    def addHistoryRestoredListener(self, callback):
        """
        Register callback for `HistoryRestored` event

        :param callback: callback function
        """
        self._history_restored_listeners.append(callback)

    def canUndo(self):
        """Return ``True`` if Undo is available for current `History Stack`

        :rtype: ``bool``
        """
        return self.history_current_step > 0
    
    def canRedo(self):
        """
        Return ``True`` if Redo is available for current `History Stack`

        :rtype: ``bool``
        """
        return self.history_current_step + 1 < len(self.history_stack)

    def undo(self):
        """Undo operation"""

        if self.canUndo():
            self.history_current_step -=1
            self.restoreHistory("undo... current step %d(%d)"%(self.history_current_step, len(self.history_stack)))
            self.scene.has_been_modified = True

    def redo(self):
        """Redo operation"""

        if self.canRedo():
            self.history_current_step += 1
            self.restoreHistory("redo... current step %d(%d)"%(self.history_current_step, len(self.history_stack)))
            self.scene.has_been_modified = True

    def restoreHistory(self, operation):
        """
        Restore `History Stamp` from `History stack`.

        Triggers:

        - `History Modified` event
        - `History Restored` event
        """
        if DEBUG: print("Restoring history",
                        ".... current step: %d" %self.history_current_step,
                        "(%d)" % len(self.history_stack))
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])   
        for callback in self._history_modified_listeners: callback(operation) 
        for callback in self._history_restored_listeners: callback() 

    def storeHistory(self, desc, setModified=False):
        """
        Store History Stamp into History Stack

        :param desc: Description of current History Stamp
        :type desc: ``str``
        :param setModified: if ``True`` marks :class:`~nodeeditor.node_scene.Scene` with `has_been_modified`
        :type setModified: ``bool``

        Triggers:

        - `History Modified`
        - `History Stored`
        """
        if setModified:
            self.scene.has_been_modified = True
        
        # if the pointer (history_current_step) is not at the end of history stack
        if self.history_current_step+1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step+1]

        # history is outside of the limit
        if self.history_current_step+1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        history_stamp = self.createHistoryStamp(desc)

        self.history_stack.append(history_stamp)
        self.history_current_step+=1
        if DEBUG: print(" -- setting step to:", self.history_current_step)

        # always trigger history modified (i.e. updateEditMenu)
        for callback in self._history_modified_listeners: callback("Storing history: " + "%s"%desc +
                                                                " ..... current step: %d" %self.history_current_step +
                                                                "(%d)" % len(self.history_stack)) 
        for callback in self._history_stored_listeners: callback() 

    def captureCurrentSelection(self):
        """Create Dictionary with list of selected nodes and list of selected edges
        :return: ``dict`` `nodes` - list of selected nodes, `edges` - list of selected edges
        :rtype: ``dict``
        """
        sel_obj = {
            'nodes' : [],
            'edges' : [],
        }
        for item in self.scene.scene_graphic.selectedItems():
            if hasattr(item, 'node'): sel_obj['nodes'].append(item.node.id)
            elif hasattr(item, 'edge'): sel_obj['edges'].append(item.edge.id)
        return sel_obj

    def createHistoryStamp(self, desc):
        """
        Create History Stamp. Internally serialize whole scene and the current selection

        :param desc: Descriptive label for the History Stamp
        :return: History stamp serializing state of `Scene` and current selection
        :rtype: ``dict``
        """
        history_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': self.captureCurrentSelection(),
        }
        return history_stamp

    def restoreHistoryStamp(self, history_stamp):
        """
        Restore History Stamp to current `Scene` with selection of items included

        :param history_stamp: History Stamp to restore
        :type history_stamp: ``dict``
        """
        if DEBUG: print("RHS: ", history_stamp['desc'])

        try:
            self.undo_selection_has_changed = False
            previous_selection = self.captureCurrentSelection()
            if  DEBUG_SELECTION: print("selected nodes before restore:", previous_selection['nodes'])

            self.scene.deserialize(history_stamp['snapshot'])

            # restore selection

            # first clear all selection on edges
            for edge in self.scene.edges: edge.edge_graphic.setSelected(False)

            # restore selected edges from history_stamp
            for edge_id in history_stamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edge_id:
                        edge.edge_graphic.setSelected(True)
                        break
            
            # first clear all selection on nodes
            for node in self.scene.nodes: node.node_graphic.setSelected(False)

            # restore selected nodes from history_stamp
            for node_id in history_stamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == node_id:
                        node.node_graphic.setSelected(True)
                        break 

            current_selection = self.captureCurrentSelection()
            if DEBUG_SELECTION: print("Selected nodes after restore:", current_selection['nodes'])

            # reset the last_selected_items, since we're comparing change to the last_selected state
            self.scene._last_selected_items = self.scene.getSelectedItems()

            # if the selection of nodes differ before and after restoration, set flag (can be used for attribute editor like maya, selection changed > update attribute editor UI)
            if current_selection['nodes'] != previous_selection['nodes'] or current_selection['edges'] != previous_selection['edges']:
                if DEBUG_SELECTION: print("\n SCENE: Selection has changed")
                self.undo_selection_has_changed = True

        except Exception as e: print(e)
        
class SceneClipboard():
    """
    Class contains all the code for serialization/deserialization from Clipboard
    """
    def __init__(self, scene):
        """
        :param scene: Reference to the :class:`~GUI.node_editor.Scene`
        :type scene: :class:`~GUI.node_editor.Scene`

        :Instance Attributes:

        - **scene** - reference to the :class:`~GUI.node_editor.Scene`
        """
        self.scene = scene

    def serializeSelected(self, delete=False):
        """
        Serializes selected items in the Scene into ``OrderedDict``

        :param delete: True if you want to delete selected items after serialization. Useful for Cut operation
        :type delete: ``bool``
        :return: Serialized data of current selection in NodeEditor :class:`~Scene`
        """
        if DEBUG: print("-- COPY TO CLIPBOARD --")

        sel_nodes, sel_edges, sel_sockets = [], [], {}

        # sort edges and nodes
        for item in self.scene.scene_graphic.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket
            elif isinstance(item, node_creator.EdgeGraphics):
                sel_edges.append(item.edge)

        # debug
        if DEBUG: 
            print(" NODES\n     ", sel_nodes)
            print(" EDGES\n     ", sel_edges)
            print(" SOCKETS\n     ", sel_sockets)

        # remove all edges which not connect to any node
        edges_to_remove = []
        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                #if DEBUG: print (" edge has connection, preserve graphic")
                pass
            else:
                if DEBUG: print ("edge ", edge, " is not connected with both sides")
                edges_to_remove.append(edge)

        for edge in edges_to_remove: sel_edges.remove(edge)

        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())
        
        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final)
        ])    

        # if cut/delete, then remove selected items
        if delete:
            self.scene.getView().deleteSelected()
            self.scene.history.storeHistory("cut out elements from scene", setModified=True)

        return data
    
    def deserializeFromClipboard(self, data):
        """
        Deserializes data from Clipboard.

        :param data: ``dict`` data for deserialization to the :class:`~Scene`.
        :type data: ``dict``
        """
        if DEBUG_PASTING: print ("dezerializating from clipboard, data:", data)

        hashmap = {}

        # calculate the mouse position - center position (to place where object will placed)
        view = self.scene.getView()
        mouse_scene_pos = view.last_scene_mouse_position

        # calculate selected objects bounding box and center
        minX, maxX, minY, maxY = 10000000, 10000000, 10000000, 10000000
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < minX: minX = x
            if x > maxX: maxX = x
            if y < minY: minY = y
            if y > maxY: maxY = y

        # add width and height of a node
        maxX -= 180
        maxY += 100

        relbboxcenterx = (minX + maxX) / 2 - minX
        relbboxcentery = (minY + maxY) / 2 - minY

        if DEBUG_PASTING:
            print (" *** Paste:")
            print("Copied boundaries:\n\tX:", minX, maxX, "     Y:", minY, maxY)
            print("\tbbox_center:", relbboxcenterx, relbboxcentery)

        # calculate the offset of the newly creating nodes
        mouseX, mouseY = mouse_scene_pos.x(), mouse_scene_pos.y()

        # create each node
        created_nodes = []

        self.scene.setSilentSelectionEvents()

        self.scene.doDeselectItems()

        for node_data in data['nodes']:
            new_node = self.scene.getNodeClassFromData(node_data)(node_data['title'],self.scene)   # get class and immediately initiate it (that's why 2 bracket)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            created_nodes.append(new_node)

            # readjust the new nodeeditor's position

            # new node's current position
            posX, posY = new_node.pos.x(), new_node.pos.y()
            newX, newY = mouseX + posX - minX, mouseY + posY - minY

            new_node.setPos(newX, newY)

            new_node.doSelect()

            if DEBUG_PASTING:
                print("** PASTA SUM:")
                print("\tMouse pos:", mouseX, mouseY)
                print("\tnew node pos:", posX, posY)
                print("\tFINAL:", newX, newY)

        # create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = node_creator.EdgeConfig(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        self.scene.setSilentSelectionEvents(False)

        # store history
        self.scene.history.storeHistory("paste object", setModified=True)

        return created_nodes

# development phase code
if __name__ == "__main__":
    
    try:
        window.close()
        window.deleteLater()    # override inside closeEvent mainWindow
    except:
        pass
    
    window = NodeEditorWindow()
    # create node
    node1 = node_creator.NodeConfig("Node 1", window.node_editor.scene, inputs=[1,2,3],outputs=[1])
    node1.setPos(-350,-150)
    
    node2 = node_creator.NodeConfig("Node 2", window.node_editor.scene, inputs=[1,2,3],outputs=[1])
    node2.setPos(-100,50)

    node3 = node_creator.NodeConfig("Node 3", window.node_editor.scene, inputs=[1,2,3],outputs=[1])
    node3.setPos(100,-200)

    edge1 = node_creator.EdgeConfig(window.node_editor.scene, node1.outputs[0], node2.inputs[0], node_creator.EDGE_TYPE_BEZIER)
    edge2 = node_creator.EdgeConfig(window.node_editor.scene, node2.outputs[0], node3.inputs[2], node_creator.EDGE_TYPE_BEZIER)

    window.node_editor.scene.history.storeInitialHistoryStamp()
    
    window.show()