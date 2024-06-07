from collections import OrderedDict
from PySide2 import QtCore,QtWidgets,QtGui
from ZCore.ToolsSystem import OUTPUT_INFO, OUTPUT_ERROR, OUTPUT_SUCCESS, OUTPUT_WARNING

import json

import maya.cmds as cmds

import ZCore.ToolsSystem as ToolsSystem

class ZenoTabContainer(QtWidgets.QWidget):
    title = ""
    def __init__(self, app=None):

        super(ZenoTabContainer, self).__init__(app)
        
        self.app = app

        self.initUI()
        self.initInputDialog()

    def initUI(self):
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)

        self.optionsLabel = GraphicButton(ToolsSystem.get_path("Sources","icons","shelf","shelf_options.png"), 
                                          self.onClick, 
                                          QtGui.QColor('white'), 
                                          0.85, 
                                          (15,15))

        self.itemWidget = QtWidgets.QWidget()   # contain flow layout
        self.itemWidget.setContentsMargins(5,5,5,5)

        self.itemLayout = FlowLayout(self.itemWidget)

        self.scrollWidget = QtWidgets.QScrollArea()
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollWidget.setWidget(self.itemWidget)
        self.mainLayout.addWidget(self.optionsLabel)
        self.mainLayout.addWidget(self.scrollWidget)

        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.scrollWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setLayout(self.mainLayout)

    def initInputDialog(self):
        self.customScriptDialog = QtWidgets.QWidget(self.app)
        self.customScriptDialog.setWindowFlags(QtCore.Qt.Window)
        self.customScriptDialog.setWindowTitle("Custom Script")

        self.inputDialogLayout = QtWidgets.QVBoxLayout(self.customScriptDialog)
        self.inputDialogLayout.setContentsMargins(5,5,5,5)

        self.scriptInputEdit = QtWidgets.QPlainTextEdit(self.customScriptDialog)
        self.scriptInputEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.saveScriptBtn = QtWidgets.QPushButton("Save Script", self.customScriptDialog)
        self.saveScriptBtn.clicked.connect(self.onSaveScript)

        self.textLayout = QtWidgets.QHBoxLayout()
        self.iconLabel = QtWidgets.QLabel("Icon :")
        self.iconLineEdit = QtWidgets.QLineEdit()
        self.iconFolderButton = GraphicButton(ToolsSystem.get_path("Sources","icons","shelf","folder.png"), 
                                              self.onFileOpen, 
                                              size=(15,15))

        self.textLayout.addWidget(self.iconLabel)
        self.textLayout.addWidget(self.iconLineEdit)
        self.textLayout.addWidget(self.iconFolderButton)

        self.inputDialogLayout.addWidget(self.scriptInputEdit)
        self.inputDialogLayout.addLayout(self.textLayout)
        self.inputDialogLayout.addWidget(self.saveScriptBtn)

    def onFileOpen(self, event):
        fnames, filter = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open graph from file', '', 'Supported Types (*.bmp *.jpg *.jpeg *.png *.svg);;All files (*)')
        try: self.iconLineEdit.setText(fnames[-1])
        except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)

    def onSaveScript(self):
        new_script_content = self.scriptInputEdit.toPlainText()
        new_script_widget = MayaScriptButton(self.iconLineEdit.text(), new_script_content, tab=self)
        self.itemLayout.addWidget(new_script_widget)
        self.app.user_script.append(new_script_widget)
        self.scriptInputEdit.clear()
        
        with open(ToolsSystem.get_path("Shelf","userPref.json"), "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))

        self.customScriptDialog.close()

    def onClick(self, event):
        self.handleShelfMenu(event)

    def onMouseEnter(self, event):
        self.highlight.setStrength(0.85)

    def onMouseLeave(self, event):
        self.highlight.setStrength(0.0)

    def handleShelfMenu(self, event):
        self.shelf_menu = QtWidgets.QMenu(self)
        self.addScriptAct = self.shelf_menu.addAction("Add Script Shortcut")
        action = self.shelf_menu.exec_(self.mapToGlobal(event.pos()))
        if action == self.addScriptAct:
            self.showInputDialog(event)

    def showInputDialog(self, event):
        self.customScriptDialog.setGeometry(self.mapToGlobal(event.pos()).x(),
                                            self.mapToGlobal(event.pos()).y(),
                                            600, 
                                            self.app.height()-200)
        self.customScriptDialog.show()

    def serialize(self):
        json_list = []
        try:
            for script in self.app.user_script:
                hashmap = OrderedDict([('shelf', script.tab.title),
                                       ('icon', script.icon),
                                       ('command', script.evalString)])
                json_list.append(hashmap)
            return OrderedDict([('user_script', json_list)])

        except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)

class GraphicButton(QtWidgets.QLabel):
    def __init__(self, icon="", callback=None,  color=QtGui.QColor('silver'), strength=0.25, size=(32,32), tab=None):
        super(GraphicButton, self).__init__()

        self.icon = icon
        self.callback = []
        if callback: self.callback.append(callback)
        self.color = color
        self.strength = strength
        self.size = size
        self.tab = tab

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

        # set highlight mouse hover effect
        self.highlight = QtWidgets.QGraphicsColorizeEffect()
        self.highlight.setColor(self.color)
        self.highlight.setStrength(0.0)
        self.setGraphicsEffect(self.highlight)

        self.mousePressEvent = self.onClick
        self.enterEvent = self.onMouseEnter
        self.leaveEvent = self.onMouseLeave

    def onClick(self, event):
        for callback in self.callback: 
            callback(event)

    def onMouseEnter(self, event):
        self.highlight.setStrength(self.strength)

    def onMouseLeave(self, event):
        self.highlight.setStrength(0.0)

class MayaScriptButton(GraphicButton):
    def __init__(self, icon="", callback="",  color=QtGui.QColor('silver'), strength=0.25, size=(32,32), tab=None):
        # we not passing the callback, because this class extend graphic button with different callback execution (using cmds.evalDeffered)
        super(MayaScriptButton, self).__init__(icon, color=color, strength=strength, size=size, tab=tab) 
        self.evalString = callback

    def onClick(self, event):
        cmds.evalDeferred(self.evalString)

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self._item_list = []
        self.tolerance = 22 # tolerance size when next widget push to new row

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x - self.tolerance > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()
