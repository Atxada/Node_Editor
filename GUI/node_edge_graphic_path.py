import math
from PySide2 import QtCore,QtWidgets,QtGui

DEBUG = False
DEBUG_ITEM = False  # delete later when bezier fixed

EDGE_CP_ROUNDNESS = 100

class EdgePathBaseGraphics:
    """Base Class for calculating the graphics path to draw for an graphics Edge"""

    def __init__(self, owner):
        # keep the reference to owner edge_graphics class
        self.owner = owner

    def calcPath(self):
        """Calculate the Direct line connection

        :return: ``QPainterPath`` of the graphics path to draw
        :rtype: ``QPainterPath`` or ``None``
        """
        return None

class EdgePathDirectGraphics(EdgePathBaseGraphics):
    def calcPath(self):
        path = QtGui.QPainterPath(QtCore.QPointF(self.owner.pos_source[0], self.owner.pos_source[1]))
        path.lineTo(self.owner.pos_destination[0], self.owner.pos_destination[1])
        return path

class EdgePathBezierGraphics(EdgePathBaseGraphics):
    def calcPath(self):
        self.start_socket = self.owner.edge.start_socket.is_input
        dist = math.fabs(self.owner.pos_source[0] - self.owner.pos_destination[0])
        if self.start_socket == True:
            self.input_pos = self.owner.pos_source
            self.output_pos = self.owner.pos_destination
            if self.input_pos[0] < self.output_pos[0] and dist > 300: dist = 300
            path = QtGui.QPainterPath(QtCore.QPointF(self.owner.pos_source[0], self.owner.pos_source[1]))
            path.cubicTo((self.input_pos[0] - dist*0.5), self.input_pos[1], 
                         (self.output_pos[0] + dist*0.5), self.output_pos[1],
                          self.owner.pos_destination[0], self.owner.pos_destination[1])
        else:
            self.input_pos = self.owner.pos_destination
            self.output_pos = self.owner.pos_source
            if self.input_pos[0] < self.output_pos[0] and dist > 300: dist = 300
            path = QtGui.QPainterPath(QtCore.QPointF(self.owner.pos_source[0], self.owner.pos_source[1]))
            path.cubicTo((self.output_pos[0] + dist*0.5), self.output_pos[1],
                         (self.input_pos[0] - dist*0.5), self.input_pos[1],      
                          self.owner.pos_destination[0], self.owner.pos_destination[1])
        return path

'''
    def calcPath(self):
        s = self.owner.pos_source
        d = self.owner.pos_destination
        dist = (d[0] - s[0] * 0.5)*0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.owner.edge.start_socket is not None:
            ssin = self.owner.edge.start_socket.is_input
            ssout = self.owner.edge.start_socket.is_output

            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                    (s[1] -  d[1]) / math.fabs(
                        (s[1] - d[1]) if (s[1] -  d[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS

                cpy_s = (
                    (d[1] -  s[1]) / math.fabs(
                        (d[1] - s[1]) if (d[1] -  s[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS

        path = QtGui.QPainterPath(QtCore.QPointF(self.owner.pos_source[0], self.owner.pos_source[1]))
        path.cubicTo((s[0] + cpx_s), (s[1] + cpy_s), (d[0] + cpx_d), (d[1] + cpy_d),
                     self.owner.pos_destination[0], self.owner.pos_destination[1])

        if DEBUG_ITEM:
            if self.ctrl_pt1 == None:
                self.ctrl_pt1 = DebugItem((s[0] + cpx_s), (s[1] + cpy_s), 10, 10, QtCore.Qt.white)
                self.ctrl_pt2 = DebugItem((d[0] + cpx_d), (d[1] + cpy_d), 10, 10, QtCore.Qt.black)
                self.owner.edge.scene.scene_graphic.addItem(self.ctrl_pt1)
                self.owner.edge.scene.scene_graphic.addItem(self.ctrl_pt2)
            else:
                self.ctrl_pt1.setPos((s[0] + cpx_s), (s[1] + cpy_s))
                self.ctrl_pt2.setPos((d[0] + cpx_d), (d[1] + cpy_d))        

        return path
'''
    
# https://stackoverflow.com/questions/52728462/pyqt-add-rectangle-in-qgraphicsscene
class DebugItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, color=QtCore.Qt.red):
        super(DebugItem,self).__init__(x, y, w, h)
        self.color = color

    def paint(self, painter, option, widget=None):
        super(DebugItem, self).paint(painter, option, widget)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(self.color)
        painter.drawEllipse(option.rect)
        painter.restore()