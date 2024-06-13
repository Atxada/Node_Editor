'''
--------------------------------------- Problem --------------------------------------- 
# there is still hard coded path (QSS_PATH) try research os.path.join, etc

'''

#---------------------------------------- Temp Main -----------------------------------------------
import sys
import maya.cmds as cmds 
sys.dont_write_bytecode = True  # prevent by bytecode python being generated (.pyc)

print ("ZCore package initialized"),
#--------------------------------------------------------------------------------------------------

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore,QtWidgets,QtGui
from shiboken2 import wrapInstance, getCppPointer

from GUI.utils import loadStylesheet, pp
from ZCore.WorkspaceControl import WorkspaceControl
from ZCore.Commands import ZenoCommand

import json
import os

# import maya.cmds as cmds
import maya.OpenMayaUI as omui

import GUI.node_creator as node_creator
import GUI.node_editor as node_editor
import ZCore.Config as Config           # import this will initiate node and shelf item registration
import ZCore.ShelfBase as ShelfBase
import ZCore.ToolsSystem as ToolsSystem

# Enabling edge validators
from GUI.node_edge_validators import (edge_validator_debug, 
                                      edge_cannot_connect_two_outputs_or_two_inputs, 
                                      edge_cannot_connect_input_and_output_of_same_node, 
                                      edge_cannot_connect_input_and_output_of_different_type)

#node_creator.EdgeConfig.registerEdgeValidator(edge_validator_debug)
node_creator.EdgeConfig.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
node_creator.EdgeConfig.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
node_creator.EdgeConfig.registerEdgeValidator(edge_cannot_connect_input_and_output_of_different_type)

DEBUG = False
DEBUG_CONTEXT = False

#QSS_PATH = 'C:\Users\\atxad\Desktop\Maya Scripts Draft\\1st Album EPILOGUE\Face Tools\ZenoRig\ZCore\Sources\style\\nodestyle.qss'
QSS_PATH = ToolsSystem.get_path("Sources","style","nodestyle.qss")

# boilerplate code, return maya main window
def maya_main_window():
    # Return the maya main window widget as a python object
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class ZenoMainWindow(node_editor.NodeEditorWindow):

    WINDOW_TITLE = "Zeno Editor"
    UI_NAME = "ZenoEditor"

    ui_instance = None

    @classmethod
    def display(cls):
        if cls.ui_instance:
            cls.ui_instance.show_workspace_control()
        else:
            cls.ui_instance = ZenoMainWindow()

    @classmethod
    def get_workspace_control_name(cls):
        return "%sWorkspaceControl"%cls.UI_NAME

    def __init__(self):
        super(ZenoMainWindow, self).__init__(maya_main_window())
        ToolsSystem.zeno_window = self   # set window instance to tool system
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowIcon(QtGui.QIcon(ToolsSystem.get_path("Sources","icons","zeno_key_rig.png")))
        # self.create_workspace_control() # toggle on/off to revert to undockable or dockable via workspace ctrl

    def initUI(self):
        self.author = 'Atxada'
        self.product_name = 'Zeno Rig'

        # Style config
        #self.stylesheet_filename = os.path.join(os.path.dirname(__file__),'Sources/style/nodestyle.qss') ERROR FILE NOT DEFINED
        self.stylesheet_filename =  QSS_PATH
        loadStylesheet(self, self.stylesheet_filename)

        self.empty_icon = QtGui.QIcon(".")  # remove maya icon

        if DEBUG:
            '''print("Registered nodes: ")
            pp(Config.ZENO_NODES)'''

        self.tab_widget = []
        self.user_script = []  # containing custom script widget 

        # mdiArea widget and setup
        self.mdiArea = QtWidgets.QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)
        #self.setCorner(QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtWidgets.QWidget].connect(self.setActiveSubWindow)

        # init all sub-window
        self.createNodesDock()
        self.createLogDock()
        self.createShelfDock()


        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Zeno Editor")

    def create_workspace_control(self):
        self.workspace_control = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control.exists():
            if DEBUG: print ("workspace control exist, trying to restore")
            self.workspace_control.restore(self)
            self.workspace_control.set_visible(True)
        else:
            if DEBUG: print ("workspace control doesn't exist create one")
            self.workspace_control.create(self.WINDOW_TITLE, self, ui_script="import sys\nimport maya.cmds as cmds\nsys.path.insert(0, 'C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig')\nsys.dont_write_bytecode = True\nfrom ZCore.UI import ZenoMainWindow\nZenoMainWindow.display()")

    def show_workspace_control(self):
        self.workspace_control.set_visible(True)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            # PyQt 5.14 error when closed (hack fix)
            # import sys
            # sys.exit(0)

    def createActions(self):
        super(ZenoMainWindow,self).createActions()

        self.actClose = QtWidgets.QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QtWidgets.QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QtWidgets.QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QtWidgets.QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QtWidgets.QAction("Ne&xt", self, shortcut=QtGui.QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QtWidgets.QAction("Pre&vious", self, shortcut=QtGui.QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QtWidgets.QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QtWidgets.QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def getCurrentNodeEditorWidget(self):
        # returning active node editor widget
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        sub_window = self.createMdiChild()
        sub_window.show()
        return sub_window
    
    def onFileOpen(self):
        fnames, filter = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                        self.outputLogInfo("File %s already exists! set as active window" %fname, ToolsSystem.OUTPUT_WARNING)
                    else:
                        # create new sub window and open the file
                        node_editor = ZenoNodeEditorWindow(self)
                        if node_editor.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" %fname, 5000)
                            self.outputLogInfo("File %s loaded" %fname, ToolsSystem.OUTPUT_SUCCESS)
                            node_editor.setTitle()
                            sub_window = self.createMdiChild(node_editor)
                            sub_window.show()
                        else:
                            node_editor.close()
        except Exception as e: self.outputLogInfo(e, ToolsSystem.OUTPUT_ERROR)
                

    def about(self):
        QtWidgets.QMessageBox.about(self, "About Zeno Rig",
                                    "The <b>Zeno Rig</b> is a tool to simplify rigging process "
                                    "document interface applications using Pyside2 and NodeEditor. For more author information visit: "
                                    "<a href='https://id.linkedin.com/in/aldo-aldrich-962975220'>www.linkedin.com</a>")

    def createMenus(self):
        super(ZenoMainWindow,self).createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)

        self.edit_menu.aboutToShow.connect(self.updateEditMenu)

    def updateMenus(self):
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)  # bool: determine if there is active mdi child

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setEnabled(hasMdiChild)

        self.updateEditMenu()

    def updateEditMenu(self, *args):    # receive *args cuz we borrow history modified listener for outputLogInfo
        try:
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)  # bool: determine if there is active mdi child

            self.actPaste.setEnabled(hasMdiChild)

            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())

        except Exception as e: self.outputLogInfo(e, ToolsSystem.OUTPUT_ERROR)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        # add action based of mdi sub window widget, to let user switch between graph 
        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def outputLogInfo(self, text, status=ToolsSystem.OUTPUT_INFO, log_detail=True):
        text = str(text)
        if status==ToolsSystem.OUTPUT_INFO:
            self.outputLogWidget.logViewer.appendPlainText(text)
            return
        if status==ToolsSystem.OUTPUT_SUCCESS:
            self.outputLogWidget.logViewer.appendHtml("<p style=\"color:SpringGreen;white-space:pre\">" + text + "</p>")
            return
        if status==ToolsSystem.OUTPUT_ERROR:
            if log_detail: text = "ERROR:: " + text
            self.outputLogWidget.logViewer.appendHtml("<p style=\"color:red;white-space:pre\">" + text + "</p>")
            return
        if status==ToolsSystem.OUTPUT_WARNING:
            if log_detail: text = "WARNING:: " + text
            self.outputLogWidget.logViewer.appendHtml("<p style=\"color:yellow;white-space:pre\">" + text + "</p>")
            return

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def createToolBars(self):
        pass

    def createNodesDock(self):
        self.nodesListWidget = ZenoDragListBox()

        self.nodesDock = QtWidgets.QDockWidget("Outliner")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.nodesDock)

    def createShelfDock(self):
        self.shelfWidget = QtWidgets.QTabWidget()
        self.shelfWidget.setMinimumHeight(70)

        # init factory script/context/etc
        keys = list(Config.SHELF_TAB.keys())
        keys.sort()
        for key in keys:
            widget = Config.get_tab_from_opcode(key)(self)
            self.tab_widget.append(widget)
            self.shelfWidget.addTab(widget, widget.title)

        # init custom user script
        # Check if userPref.json present, and then check the data to deserialize, if not ignore
        try:
            with open(ToolsSystem.get_path("Shelf","userPref.json"), "r") as file:
                raw_data = file.read()
                data = json.loads(raw_data, encoding='utf-8')
                self.deserializeCustomScript(data)
                
        except Exception as e: pass

        self.shelfDock = QtWidgets.QDockWidget("Shelf")
        self.shelfDock.setFloating(False)
        self.shelfDock.setWidget(self.shelfWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.shelfDock)

    def createLogDock(self):
        self.outputLogWidget = ZenoOutputLog(self)
        
        self.logDock = QtWidgets.QDockWidget("Output Log")
        self.logDock.setFloating(False)
        self.logDock.setWidget(self.outputLogWidget)

        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)

    def deserializeCustomScript(self, data):
        for script in data['user_script']:
            for tab in self.tab_widget:
                if script["shelf"] == tab.title:
                    item = ShelfBase.MayaScriptButton(script['icon'], 
                                                      script['command'],
                                                      tab=tab)
                    tab.itemLayout.addWidget(item)
                    self.user_script.append(item)
                    break

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
        #self.status_mouse_pos = QtWidgets.QLabel("")
        #self.statusBar().addPermanentWidget(self.status_mouse_pos)

    def createMdiChild(self, child_widget=None):
        node_editor = child_widget if child_widget is not None else ZenoNodeEditorWindow(self)
        sub_window = self.mdiArea.addSubWindow(node_editor)
        sub_window.setWindowIcon(self.empty_icon)
        node_editor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        node_editor.scene.history.addHistoryModifiedListener(self.outputLogInfo)
        node_editor.addCloseEventListener(self.onSubWndClose)
        return sub_window
    
    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.file_name)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiChild(self, fname):
        for window in self.mdiArea.subWindowList():
            if window.widget().file_name == fname:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

class ZenoNodeEditorWindow(node_editor.NodeEditorWidget):
    def __init__(self, window):
        super(ZenoNodeEditorWindow, self).__init__()

        self.main_window = window

        self.setTitle()

        self.initNewNodeactions()
        self.initDebugWidget()

        # listeners and signal fetch
        self.view.scenePosChanged.connect(self.onScenePosChanged)    # emit scenePosChanged signal
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.history.addHistoryModifiedListener(self.updateDebugInfo)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)
        self.view.addDeleteListener(self.onDeleteNode)

        self._close_event_listeners = []

    def initDebugWidget(self):
        self.debug_widget = DebugWidget(self.view)
        #self.debug_widget.setVisible(False)
        self.debug_widget.setMinimumWidth(250)
        self.vertical_column = QtWidgets.QVBoxLayout(self.debug_widget)
        #self.debug_widget.setStyleSheet("background-color : yellow")

        self._Heading1_font = QtGui.QFont('Ubuntu', 20)
        self._Heading2_font = QtGui.QFont('Ubuntu', 12)
        self._Heading3_font = QtGui.QFont('Ubuntu', 8)
        
        # debug detail widgets
        self.state_label = DebugLabel("No Operation")
        self.state_label.setFont(self._Heading1_font)
        self.view.addStateListener(self.onStateChanged)
    
        self.selected_label = DebugLabel("selected items: %s"%(len(self.scene.getSelectedItems())))
        self.selected_label.setStyleSheet("QLabel {color : #ffff80;}")
        self.selected_label.setFont(self._Heading2_font)

        self.nodes_label = DebugLabel("total nodes: %s"%len(self.scene.nodes))
        self.edges_label = DebugLabel("total edges: %s"%len(self.scene.edges))

        self.mouse_pos_label = DebugLabel("mouse coordinate (-, -)")

        # parent widget to layout
        self.vertical_column.addWidget(self.state_label)
        self.vertical_column.addWidget(self.selected_label)
        self.vertical_column.addWidget(self.nodes_label)
        self.vertical_column.addWidget(self.edges_label)
        self.vertical_column.addWidget(self.mouse_pos_label)
        self.vertical_column.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def addNode(self, node_code, nameID=None):
        """Create `Nodes` inside scene with given nameID (testing purpose)"""
        
        try:
            if nameID: node = Config.get_class_from_opcode(node_code)(nameID, self.scene)
            else: node = Config.get_class_from_opcode(node_code)(scene=self.scene)
            x, y = self.scene.getView().width()/2, self.scene.getView().height()/2
            scenepos = self.scene.getView().mapToScene(x, y)
            node.setPos(scenepos.x(), scenepos.y())
            self.scene.history.storeHistory("Create Node: %s"%node.__class__.__name__)  # get only short name of class 
            return node
        except Exception as e: self.main_window.outputLogInfo(e, ToolsSystem.OUTPUT_ERROR)

    def getNodeClassFromData(self, data):
        if 'op_code' not in data: return node_creator.NodeConfig
        return Config.get_class_from_opcode(data['op_code'])

    def doEvalOutputs(self):
        # eval all output nodes in scene
        for node in self.scene.nodes:
            if node.__class__.__name__ == "ZenoNode_Output":
                node.eval() 
    
    def onHistoryRestored(self):
        self.doEvalOutputs()

    def fileLoad(self, filename):
        if super(ZenoNodeEditorWindow, self).fileLoad(filename):
            self.doEvalOutputs()
            return True

        return False
    
    def initNewNodeactions(self):
        self.node_actions = {}
        keys = list(Config.ZENO_NODES.keys())
        keys.sort()
        for key in keys:
            node = Config.ZENO_NODES[key]
            self.node_actions[node.op_code] = QtWidgets.QAction(QtGui.QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)
 
    def initNodesContextMenu(self):
        context_menu = QtWidgets.QMenu(self)
        keys = list(Config.ZENO_NODES.keys())
        keys.sort() # sort dict because we convert it to list from dict
        for key in keys: context_menu.addAction(self.node_actions[key])
        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners: callback(self, event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(Config.LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(Config.LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(Config.LISTBOX_MIMETYPE)
            dataStream = QtCore.QDataStream(eventData, QtCore.QIODevice.ReadOnly)
            pixmap = QtGui.QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt16()
            text = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.scene_graphic.views()[0].mapToScene(mouse_position)

            if DEBUG: self.main_window.outputLogInfo("Node detail: [%d] '%s'"%(op_code, text) + "mouse: " + str(mouse_position) + "scene: " + str(scene_position))

            try:
                node = Config.get_class_from_opcode(op_code)(scene=self.scene) # get_class_from_opcode return class and initiate it immediately with scene argument (that's why 2 brackets)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Create Node: %s"%node.__class__.__name__)  # get only short name of class 
            except Exception as e: print(e)

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            #print("... drop ignored, not requested format '%s'"% Config.LISTBOX_MIMETYPE)
            event.ignore()

    def onDeleteNode(self, event):
        try:    # remove maya related obj and toolsystem data
            cmds.delete(event.title)
            ToolsSystem.spline_node.remove(event.title)
        except:
            cmds.warning("object '%s' not found inside scene" %event.title)

    def onScenePosChanged(self, x, y):
        """Optional signal to use for mouse node editor position"""
        self.mouse_pos_label.setText("mouse coordinate (%s, %s)"%(x,y))

    def onStateChanged(self, value):
        if value == 1:
            self.state_label.setText("No Operation")
        elif value == 2:
            self.state_label.setText("Dragging Mode")
        elif value == 3:
            self.state_label.setText("Cutting Mode")
        elif value == 4:
            self.state_label.setText("Rerouting Mode")

    def updateDebugInfo(self, *args):
        self.selected_label.setText("selected items: %s"%(len(self.scene.getSelectedItems())))
        self.nodes_label.setText("total nodes: %s"%len(self.scene.nodes))
        self.edges_label.setText("total edges: %s"%len(self.scene.edges))

    def contextMenuEvent(self,event):
        try:
            item = self.scene.getItemAt(event.pos())
            if DEBUG_CONTEXT: print (item)

            if type(item) == QtWidgets.QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            else:
                self.handleNewNodeContextMenu(event)

            return super(ZenoNodeEditorWindow, self).contextMenuEvent(event)
        except Exception as e: print (e)

    def handleNodeContextMenu(self, event):
        if DEBUG_CONTEXT: print('CONTEXT: NODE')
        context_menu = QtWidgets.QMenu(self)
        markDirtyAct = context_menu.addAction("Mark Dirty")
        markDescendantsDirtyAct = context_menu.addAction("Mark Descendant Dirty")
        markInvalidAct = context_menu.addAction("Mark Invalid")
        unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        evalAct = context_menu.addAction("Eval")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        
        selected = None
        item = self.scene.getItemAt(event.pos())
        if type(item) == QtWidgets.QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if DEBUG_CONTEXT: print("got item:", selected)
        if selected and action == markDirtyAct: selected.markDirty()
        if selected and action == markDescendantsDirtyAct: selected.markDescendantsDirty()
        if selected and action == markInvalidAct: selected.markInvalid()
        if selected and action == unmarkInvalidAct: selected.markInvalid(False)
        if selected and action == evalAct:
            val = selected.eval()
            if DEBUG_CONTEXT: print("EVALUATED:", val)

    def handleEdgeContextMenu(self, event):
        if DEBUG_CONTEXT: print('CONTEXT: EDGE')
        context_menu = QtWidgets.QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        
        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = node_creator.EDGE_TYPE_BEZIER
        if selected and action == directAct: selected.edge_type = node_creator.EDGE_TYPE_DIRECT

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_zeno_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_zeno_node.inputs) > 0: target_socket = new_zeno_node.inputs[0]
        else:
            if len(new_zeno_node.outputs) > 0: target_socket = new_zeno_node.outputs[0]
        return target_socket
    
    def finish_new_node_state(self, new_zeno_node):
        self.scene.doDeselectItems()
        new_zeno_node.node_graphic.doSelect(True)
        new_zeno_node.node_graphic.onSelected()

    def handleNewNodeContextMenu(self, event):
        if DEBUG_CONTEXT: print('CONTEXT: EMPTY SPACE')
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_zeno_node = Config.get_class_from_opcode(action.data())(scene=self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_zeno_node.setPos(scene_pos.x(),scene_pos.y())
            if DEBUG_CONTEXT: print ("Selected node", new_zeno_node)

            if self.scene.getView().mode == node_editor.MODE_EDGE_DRAG:
                # if dragging edge...
                target_socket = self.determine_target_socket_of_node(self.scene.getView().dragging.drag_start_socket.is_output, new_zeno_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.socket_graphic)
                    self.finish_new_node_state(new_zeno_node)
            
            else:
                self.scene.history.storeHistory("Created %s" % new_zeno_node.__class__.__name__)

# helper UI Class
class ZenoDragListBox(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(ZenoDragListBox, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QtCore.QSize(32,32))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection) # When the user selects an item, any already-selected item becomes unselected
        self.setDragEnabled(True)

        self.addMyItems()

    # addItems already inherited from QListWidget(parent) class, so changed name to addMyItems
    def addMyItems(self):
        keys = list(Config.ZENO_NODES.keys())
        keys.sort() # sort the op_code number [1,2,3,..]
        for key in keys:
            node = Config.get_class_from_opcode(key)
            self.addMyItem(node.op_title, node.icon, node.op_code)

    def addMyItem(self, name, icon=None, op_code=0):
        item = QtWidgets.QListWidgetItem(name, self) # can be (icon, text, parent, <int> type)
        pixmap = QtGui.QPixmap(icon if icon is not None else ".")
        item.setIcon(QtGui.QIcon(pixmap))
        item.setSizeHint(QtCore.QSize(32,32))

        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)

        # setup data
        item.setData(QtCore.Qt.UserRole, pixmap)  # tell qt what is the data type of item (this case the image)
        item.setData(QtCore.Qt.UserRole+1, op_code)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            op_code = item.data(QtCore.Qt.UserRole+1)

            pixmap = QtGui.QPixmap(item.data(QtCore.Qt.UserRole))

            itemData = QtCore.QByteArray()
            dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
            dataStream << pixmap    # pass pixmap data to data stream operator
            dataStream.writeInt16(op_code)
            dataStream.writeQString(item.text())

            mimeData = QtCore.QMimeData()
            mimeData.setData(Config.LISTBOX_MIMETYPE, itemData)

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QtCore.QPoint(pixmap.width()/1.5, pixmap.height()/1.5)) # set cursor position with pximap
            drag.setPixmap(pixmap)

            drag.exec_(QtCore.Qt.MoveAction)

        except Exception as e: print(e)

class ZenoOutputLog(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ZenoOutputLog, self).__init__(parent)
        
        self._parent = parent
        self.zoom = 9
        self._font = QtGui.QFont("Consolas") # consolas seems the most stable for fixed width character

        self.initUI()
    
    def initUI(self):
        self.interpreter = ZenoCommand(self._parent)

        self.logViewer = QtWidgets.QPlainTextEdit()
        self.logViewer.setFont(self._font)
        self.logViewer.zoomIn(9)
        self.logViewer.setReadOnly(True)

        self.completer = QtWidgets.QCompleter(self.interpreter.command_list, 
                                              self, 
                                              caseSensitivity=QtCore.Qt.CaseInsensitive)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self.dummyCompleter = QtWidgets.QCompleter()

        self.commandLine = QtWidgets.QLineEdit()
        self.commandLine.setPlaceholderText("Enter Command")
        self.commandLine.setCompleter(self.completer)
        self.commandLine.returnPressed.connect(self.onEnterCommand)

        self.completer.activated.connect(self.onActive)

        self.logLayout = QtWidgets.QVBoxLayout()
        self.logLayout.addWidget(self.logViewer)
        self.logLayout.addWidget(self.commandLine)
        self.setLayout(self.logLayout)

    def onActive(self):
        self.commandLine.setCompleter(self.dummyCompleter)
        self.commandLine.setCompleter(self.completer)

    def onEnterCommand(self):
        input = self.commandLine.text()
        self.commandLine.clear()
        self.interpreter.onecmd(input)

class DebugWidget(QtWidgets.QWidget):
    """this class just passing the event it receive to node editor"""
    def __init__(self, parent=None):
        super(DebugWidget, self).__init__(parent)
        self.view = parent
        self.setAcceptDrops(True)
        self.setMouseTracking(True) # this enable mouseMoveEvent called without requiring any key to be pressed

    def dropEvent(self, event):
        self.view.dropEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(Config.LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)

    def mousePressEvent(self, event):
        self.view.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.view.mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.view.mouseMoveEvent(event)

    def wheelEvent(self, event):
        self.view.wheelEvent(event)

class DebugLabel(QtWidgets.QLabel):
    """this class just passing the event it receive to node editor"""
    def __init__(self, parent=None):
        super(DebugLabel, self).__init__(parent)
        self.setMouseTracking(True) # this enable mouseMoveEvent called without requiring any key to be pressed

if __name__ == "__main__":
    '''
    workspace_control_name = ZenoMainWindow.get_workspace_control_name()
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)   # only for floating window, if docked might not detected (create possible error like additional ui on same window)
    
    try:
        print ("try")
        zeno_rig_window.setParent(None) # unparent from workspace control
        zeno_rig_window.deleteLater()   # after that delete it
    except:
        print ("can't try")
        pass 
    '''
    try:
        zeno_rig_window.close()
        zeno_rig_window.deleteLater()
    except:
        pass
    
    zeno_rig_window = ZenoMainWindow()
    zeno_rig_window.show()

    # Step to toggle on workspace control
    # 1. leave init ZenoMainWindow arguments blank
    # 2. uncommand self.create_workspace_control inside ZenoMainWindow
    # 3. for development phase: uncommand checking cmds.window(workspace_control_name) [delete if exists and setparent and deleteLater]
