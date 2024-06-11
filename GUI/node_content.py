# -*- coding: utf-8 -*-
"""This module containing base class for Node's content graphical representation. It also contains example of overriden
Text Widget which can pass to it's parent notification about currently being modified."""

class NodeContentWidget:
    """Base class: Node's graphics content. This class also provides layout for other widgets inside of :py:class:`~GUI.node_creator.NodeConfig` class"""
    def __init__(self, node): # colon used to specify inside docs what type to pass ("string if u don't want to import/define")
        """

        :param node: reference to :py:class:`~GUI.node_creator.NodeConfig`
        :type node: :py:class:`~GUI.node_creator.NodeConfig`
        :param parent: parent widget
        :type parent: QtWidgets.QWidget
        """
        self.node = node
