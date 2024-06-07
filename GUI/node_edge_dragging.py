import GUI.node_creator as node_creator

DEBUG = False

class EdgeDragging:
    def __init__(self, view_graphic):
        self.view_graphic = view_graphic
        # initializing these variable to know we're using them in this class...
        self.drag_edge = None
        self.drag_start_socket = None

    def getEdgeClass(self):
        """Helper function to get the edge class. Using what Scene class provides"""
        return self.view_graphic.scene_graphic.scene.getEdgeClass()
    
    def updateDestination(self, x, y):
        """ update the end point of our dragging edge

        :param x: new x scene position
        :type x: ``float``
        :param y: new y scene position
        :type y: ``float``
        """
        # according to sentry: 'NoneType' object has no attribute 'edge_graphic'
        if self.drag_edge is not None and self.drag_edge.edge_graphic is not None:
            self.drag_edge.edge_graphic.setDestination(x, y)
            self.drag_edge.edge_graphic.update()
        else:
            if DEBUG: print(">>> trying to update self.drag_edge edge_graphic, ignored. value is None!")
  
    def edgeDragStart(self, item):
        """Code handling the start of a dragging an `Edge` operation"""
        if DEBUG: print ("View:edgeDragStart - start dragging edge")
        if DEBUG: print ("View:edgeDragStart - assign Start socket to", item.socket)
        #self.previousEdge = item.socket.edge
        self.drag_start_socket = item.socket
        self.drag_edge = self.getEdgeClass()(item.socket.node.scene, 
                                                item.socket, 
                                                None, 
                                                node_creator.EDGE_TYPE_BEZIER)
        self.drag_edge.edge_graphic.makeUnselectable()
        if DEBUG: print ("View:edgeDragStart - drag_edge", self.drag_edge)


    def edgeDragEnd(self, item):
        """Code handling the end of the dragging an `Edge` operation. If this code returns True then skip the
        rest of the mouse event processing. Can be called with ``None`` to cancel the edge dragging mode

        :param item: Item in the `Graphics Scene` where we ended dragging an `Edge`
        :type item: ``QGraphicsItem``
        """
        # if clicked on something else than socket
        if not isinstance(item, node_creator.SocketGraphics):
            self.view_graphic.resetMode()
            if DEBUG: print ("View:edgeDragEnd - end dragging edge early")
            self.drag_edge.remove(silent=True)  # don't notify sockets about removing drag_edge
            self.drag_edge = None

        # clicked on socket
        if isinstance(item, node_creator.SocketGraphics):
            
            # check if edge would be valid
            if not self.drag_edge.validateEdge(self.drag_start_socket, item.socket):
                #print("NOT VALID CONNECTION")
                ## if you want behavior when u click on socket and release the drag edge is dissapear
                # self.view_graphic.resetMode()
                # if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
                # self.drag_edge.remove(silent=True)
                # self.drag_edge = None
                #
                return False

            # regular processing of drag edge
            self.view_graphic.resetMode()
            if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
            self.drag_edge.remove(silent=True)
            self.drag_edge = None

            try:
                if item.socket != self.drag_start_socket:
                    # if we released dragging on a socket (other then the beginning socket)

                    ## First remove old edges / send notifications
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                # print("removing SILENTLY edges from input socket (is_input and !is_multi_edges) [DragStart]:", item.socket.edges)
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)
                    
                    # create new edge
                    new_edge = self.getEdgeClass()(item.socket.node.scene, 
                                                    self.drag_start_socket, 
                                                    item.socket, 
                                                    edge_type=node_creator.EDGE_TYPE_BEZIER)
                    if DEBUG: print("View:edgeDragEnd - created new edge:", new_edge, "connecting", new_edge.start_socket, "<--->", new_edge.end_socket)
                    
                    # send notifications for the new edge
                    for socket in (self.drag_start_socket, item.socket):
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input: socket.node.onInputChanged(socket)

                    self.view_graphic.scene_graphic.scene.history.storeHistory("connect edge", setModified=True)
                    return True
            except Exception as e: print ("ERROR Edge Drag End: %s"%e)
        
        #if DEBUG: print ("View:edgeDragEnd - about to set socket to previous edge", self.previousEdge)
        #if self.previousEdge is not None:
        #    self.previousEdge.start_socket.edge = self.previousEdge

        if DEBUG: print ("View:edgeDragEnd - everything done...")
        return False