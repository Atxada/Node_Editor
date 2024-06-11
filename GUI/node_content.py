# -*- coding: utf-8 -*-
"""This module containing base class for Node's content graphical representation. It also contains example of overriden
Text Widget which can pass to it's parent notification about currently being modified."""

class NodeContentWidget(QtWidgets.QWidget, Serializable):
    """Base class: Node's graphics content. This class also provides layout for other widgets inside of :py:class:`~GUI.node_creator.NodeConfig` class"""
    def __init__(self, node, parent=None): # colon used to specify inside docs what type to pass ("string if u don't want to import/define")
        """

        :param node: reference to :py:class:`~GUI.node_creator.NodeConfig`
        :type node: :py:class:`~GUI.node_creator.NodeConfig`
        :param parent: parent widget
        :type parent: QtWidgets.QWidget
        """
        self.node = node
        super(NodeContentWidget,self).__init__(parent)
        self.nodeLayout = QtWidgets.QVBoxLayout(self)
        self.nodeLayout.setContentsMargins(7.5,0,0,0)
        self.nodeLayout.setSpacing(0)
        self.nodeLayout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.setStyleSheet("background: transparent;")  # override maya default background color for QWidget
        self.initUI()

    def initUI(self):
        """Default layout setup and widgets to be rendered in :py:class:`~GUI.node_creator.NodeGraphics` class"""
        self.label = QtWidgets.QLabel("Content Label")
        self.text_edit = TextEditOverride("Content Edit")

        # modify widget
        self.addWidgetToLayout([self.label, self.text_edit], 40)

    def addWidgetToLayout(self, widgets=[], height=20):
        """Let content create default layout configuration"""
        for item in widgets:
            item.setFixedHeight(height)
            self.nodeLayout.addWidget(item)

        # delete if spacer item exist within layout, it should be last
        for index in range(self.nodeLayout.count()):
            item = self.nodeLayout.itemAt(index)
            if isinstance(item, QtWidgets.QSpacerItem):
                self.nodeLayout.removeItem(item)

        self.nodeLayout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))
        
    def setEditingFlag(self, value):
        """Helper function which sets editingFlag inside :py:class:`~GUI.node_editor.GraphicsView` class

        This is a helper function to handle editing node's content with ``QLineEdits`` or ``QTextEdits`` (use overriden :py:classs:TextEditOverride)
        and handle ``keyPressEvent`` inside :py:class:`~GUI.node_editor.GraphicsView` class.

        .. note::

            If you are handling KeyPress events by default Qt Window's shortcuts and ``QActions``, you can ignore this method

        :param value: new value for editing flag
        :type value: ``bool``
        """
        self.node.scene.getView().editingFlag = value

    def serialize(self):
        return OrderedDict([    
        ])
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        return True
        
class TextEditOverride(QtWidgets.QTextEdit):
    """Overriden ``QTextEdit`` which sends notification about being edited to parent widget :py:class:`NodeContentWidget`
    
        .. note::

            This class is example of ``QTextEdit`` modification to be able to handle `Delete` key with overriden
            Qt's ``keyPressEvent`` (when not using ``QActions`` in menu or toolbar)
    """
    def focusInEvent(self, event):
        """Example of overriden focusInEvent to mark the start of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        super(TextEditOverride,self).focusInEvent(event)
        self.parentWidget().setEditingFlag(True)
    
    def focusOutEvent(self, event):
        """Example of overriden focusOutEvent to mark the end of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        super(TextEditOverride,self).focusOutEvent(event)
        self.parentWidget().setEditingFlag(False)
