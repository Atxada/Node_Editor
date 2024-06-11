# -*- coding: utf-8 -*-
"""This module containing base class for Node's content graphical representation. It also contains example of overriden
Text Widget which can pass to it's parent notification about currently being modified."""

from collections import OrderedDict

from PySide2 import QtCore,QtWidgets,QtGui

from GUI.serializable import Serializable

class NodeContentWidget():
    """Base class: Node's graphics content. This class also provides layout for other widgets inside of :py:class:`~GUI.node_creator.NodeConfig` class"""
    def __init__(self, node, parent=None): # colon used to specify inside docs what type to pass ("string if u don't want to import/define")
        """

        :param node: reference to :py:class:`~GUI.node_creator.NodeConfig`
        :type node: :py:class:`~GUI.node_creator.NodeConfig`
        :param parent: parent widget
        :type parent: QtWidgets.QWidget
        """

    def initUI(self):
        """Default layout setup and widgets to be rendered in :py:class:`~GUI.node_creator.NodeGraphics` class"""

    def addWidgetToLayout(self, widgets=[], height=20):
        """Let content create default layout configuration"""
        
    def setEditingFlag(self, value):
        """Helper function which sets editingFlag inside :py:class:`~GUI.node_editor.GraphicsView` class

        This is a helper function to handle editing node's content with ``QLineEdits`` or ``QTextEdits`` (use overriden :py:classs:TextEditOverride)
        and handle ``keyPressEvent`` inside :py:class:`~GUI.node_editor.GraphicsView` class.

        .. note::

            If you are handling KeyPress events by default Qt Window's shortcuts and ``QActions``, you can ignore this method

        :param value: new value for editing flag
        :type value: ``bool``
        """

    def serialize(self):
        return 
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        return True
       
