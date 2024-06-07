# -*- coding: utf-8 -*-
"""
This module define all extended features of node editor 
"""

from PySide2 import QtCore,QtWidgets,QtGui

import GUI.node_creator as node_creator

DEBUG_REROUTING = False

class CutLine(QtWidgets.QGraphicsItem):
    """Class representing Cutting Line used for cutting multiple `Edges` with one stroke"""
    def __init__(self, parent=None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``
        """
        super(CutLine,self).__init__(parent)

        self.line_points = []

        self._pen = QtGui.QPen(QtCore.Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()
    
    def shape(self):
        """Calculate the QPainterPath object from list of line points

        :return: shape function returning ``QPainterPath`` representation of Cutting Line
        :rtype: ``QPainterPath``
        """
        poly = QtGui.QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QtGui.QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QtGui.QPainterPath(QtCore.QPointF(0,0))
            path.lineTo(QtCore.QPointF(1,1))

        return path
    
    def paint(self, painter, option, widget):
        """Paint the Cutting Line"""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QtGui.QPolygonF(self.line_points)
        painter.drawPolyline(poly)

class EdgeRerouting:
    def __init__ (self, view_graphic):
        self.view_graphic = view_graphic
        self.start_socket = None            # store where we start rerouting the edges
        self.rerouting_edges = []           # edges respresenting the rerouting (dashed edges)
        self.is_rerouting = False           # state to track if currently rerouting edges or not
        self.first_mb_release = False

    def print_debug(self, *args):
        if DEBUG_REROUTING: print("REROUTING:", args)

    def getEdgeClass(self):
        return self.view_graphic.scene_graphic.scene.getEdgeClass()

    def getAffectedEdges(self):
        if self.start_socket is None:
            return []       # no starting socket assigned, so no edges to hide
        # return edges connected to the socket
        return self.start_socket.edges[:]   # python 2.7 doesn't support list.copy() use slicing instead
    
    def setAffectedEdgesVisible(self, visibility=True):
        for edge in self.getAffectedEdges():
            if visibility: edge.edge_graphic.show()
            else: edge.edge_graphic.hide()

    def resetRerouting(self):
        self.is_rerouting = False
        self.start_socket = None
        self.first_mb_release = False
        # holding all rerouting edges should be empty at this point...
        # self.rerouting_edges = []

    def clearReroutingEdges(self):
        self.print_debug("clean called")
        while self.rerouting_edges != []:
            edge = self.rerouting_edges.pop()
            self.print_debug("\t cleaning:", edge)
            edge.remove(silent=True)

    def updateScenePos(self, x, y):
        if self.is_rerouting:
            for edge in self.rerouting_edges:
                if edge and edge.edge_graphic:
                    edge.edge_graphic.setDestination(x,y)
                    edge.edge_graphic.update()

    def startRerouting(self, socket):
        self.print_debug("start rerouting on", socket)
        self.is_rerouting = True
        self.start_socket = socket

        self.print_debug("numEdges:", len(self.getAffectedEdges()))
        self.setAffectedEdgesVisible(visibility=False)

        start_position = self.start_socket.node.getSocketScenePosition(self.start_socket)

        for edge in self.getAffectedEdges():
            other_socket = edge.getOtherSocket(self.start_socket)

            new_edge = self.getEdgeClass()(self.start_socket.node.scene, edge_type=edge.edge_type)
            new_edge.start_socket = other_socket
            new_edge.edge_graphic.setSource(*other_socket.node.getSocketScenePosition(other_socket))
            new_edge.edge_graphic.setDestination(*start_position)
            new_edge.edge_graphic.update()
            self.rerouting_edges.append(new_edge)

    def stopRerouting(self, target=None):   # target is destination which socket user want to reroute
        self.print_debug("stop rerouting on", target, "no change" if target==self.start_socket else "")

        if self.start_socket is not None:
            # reset start socket highlight
            self.start_socket.socket_graphic.isHighlighted = False

        # collect all affected (node, edge) tuples if successfully reroute
        affected_nodes = []

        if target is None or target == self.start_socket:
            # canceling rerouting (no change)
            self.setAffectedEdgesVisible(visibility=True)
        else:
            # validate edges before doing anything else
            valid_edges, invalid_edges = self.getAffectedEdges(), []
            for edge in self.getAffectedEdges():
                start_sock = edge.getOtherSocket(self.start_socket)
                if not edge.validateEdge(start_sock, target):
                    # not valide edge
                    self.print_debug("This edge rerouting is not valid!", edge)
                    invalid_edges.append(edge)

            # remove the invalidated edges from the list
            for invalid_edge in invalid_edges:
                valid_edges.remove(invalid_edge)

            # reconnect to new socket
            self.print_debug("Should reconnect from:", self.start_socket, "-->", target)

            self.setAffectedEdgesVisible(visibility=True)

            for edge in valid_edges:
                for node in [edge.start_socket.node, edge.end_socket.node]:
                    if node not in affected_nodes:
                        affected_nodes.append((node, edge))

                if target.is_input:     # input is always receive one connection
                    target.removeAllEdges(silent=True)
                
                if edge.end_socket == self.start_socket:    # assign edge to new socket after rerouting done
                    edge.end_socket = target
                else:
                    edge.start_socket = target

                edge.updatePositions()

        # hide and remove rerouting edges (cleanup)
        self.clearReroutingEdges()

        # send notifications for all affected nodes
        for affected_node, edge in affected_nodes:
            affected_node.onEdgeConnectionChanged(edge)
            if edge.start_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.start_socket)
            if edge.end_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.end_socket)

        # store history stamp
        self.start_socket.node.scene.history.storeHistory("rerouted edges", setModified=True)

        # reset variables of this rerouting state (cleanup)
        self.resetRerouting()

class EdgeSnapping:
    def __init__(self, view_graphhic, snapping_radius):
        self.view_graphic = view_graphhic
        self.scene_graphic = self.view_graphic.scene_graphic
        self.edge_snapping_radius = snapping_radius

    def getSnappedSocketItem(self, event):
        scenepos = self.view_graphic.mapToScene(event.pos())
        socket_graphic, pos = self.getSnappedToSocketPosition(scenepos)
        return socket_graphic
    
    def getSnappedToSocketPosition(self, scenepos):
        """Returns socket_graphic and scene position to nearest socket or original position if no nearby socket found

        :param scenepos: scene point to snap (target snap)
        :type scenepos: ``QPointF``
        :return: socket_graphic and scene position to nearest socket
        """

        # scan rectangle according to radius to find nearby graphic item
        # remember QRectF parameter (x,y,w,h) so don't confused with argument below
        scan_rect = QtCore.QRectF(
            scenepos.x() - self.edge_snapping_radius, scenepos.y() - self.edge_snapping_radius,
            self.edge_snapping_radius*2, self.edge_snapping_radius*2
        )
        items = self.scene_graphic.items(scan_rect) # passing scan_rect tell scene_graphic to return items inside rectangle radius
        items = list(filter(lambda x: isinstance(x, node_creator.SocketGraphics), items)) # filter (builtin) out only instance of socket graphic class

        if len(items) == 0:
            return None, scenepos
        
        selected_item = items[0]
        if len(items) > 1:
            # calculate the nearest socket
            nearest = 10000000000
            for grsocket in items:
                grsocket_scenepos = grsocket.socket.node.getSocketScenePosition(grsocket.socket)
                qpdist = QtCore.QPointF(*grsocket_scenepos) - scenepos
                dist = qpdist.x() * qpdist.x() + qpdist.y() * qpdist.y()    # find vector length without sqrt because we just try to find smaller value
                if dist < nearest:
                    nearest, selected_item = dist, grsocket

        selected_item.isHighlighted = True
        selected_item.update()

        calcpos = selected_item.socket.node.getSocketScenePosition(selected_item.socket)

        return selected_item, QtCore.QPointF(*calcpos)