#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
        QPoint, pyqtProperty, pyqtSignal, QEasingCurve, QObject,
        QParallelAnimationGroup, QPointF, QPropertyAnimation, qrand, QRectF,
        QState, QStateMachine, Qt, QTimer)
from PyQt5.QtGui import (QColor, QDrag, QPainter, QPixmap, QCursor, QBrush, QLinearGradient, QPainterPath)
from PyQt5.QtWidgets import *

# Draggable Cards' Widget
class DragWidget(QWidget):
    def __init__(self):
        super(DragWidget, self).__init__()
        self.setAcceptDrops(True)

# Draggable Cards
        c2 = QLabel(self)
        c2.setPixmap(QPixmap('sol-images/c2.png'))
        c2.move(78, 2)
        c2.show()

        h5 = QLabel(self)
        h5.setPixmap(QPixmap('sol-images/h5.png'))
        h5.move(-1, 2)
        h5.show()

        c6 = QLabel(self)
        c6.setPixmap(QPixmap('sol-images/c6.png'))
        c6.move(162, 2)
        c6.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'): # drags and drops in field
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        itemData = event.mimeData().data('application/x-dnditemdata')
        dataStream = QDataStream(itemData, QIODevice.ReadOnly)

        pixmap = QPixmap()
        offset = QPoint()
        dataStream >> pixmap >> offset

# Makes card visible in its new position
        newIcon = QLabel(self)
        newIcon.setPixmap(pixmap)
        newIcon.move(event.pos() - offset)
        newIcon.show()
        newIcon.setAttribute(Qt.WA_DeleteOnClose)

        event.source() == self
        event.setDropAction(Qt.MoveAction)
        event.accept()

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            return

        pixmap = QPixmap(child.pixmap())

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << pixmap << QPoint(event.pos() - child.pos())

        mimeData = QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos())

        tempPixmap = QPixmap(pixmap)
        painter = QPainter()
        painter.begin(tempPixmap)
        painter.fillRect(pixmap.rect(), QColor(127, 127, 127, 127))
        painter.end()

        child.setPixmap(tempPixmap)

        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
            child.setPixmap(pixmap)

# Window with animation
class Pixmap(QObject):
    def __init__(self, pix):
        super(Pixmap, self).__init__()
        self.pixmap_item = QGraphicsPixmapItem(pix)
        self.pixmap_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def _set_pos(self, pos):
        self.pixmap_item.setPos(pos)

    pos = pyqtProperty(QPointF, fset=_set_pos)

class Button(QGraphicsWidget):
    pressed = pyqtSignal()

    def __init__(self, pixmap, parent=None):
        super(Button, self).__init__(parent)
        self._pix = pixmap
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setAcceptDrops(True)

    def boundingRect(self):
        return QRectF(-65, -65, 130, 130)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())

        return path

    def paint(self, painter, option, widget):
        down = option.state & QStyle.State_Sunken
        r = self.boundingRect()

        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        painter.drawPixmap(-self._pix.width() / 2, -self._pix.height() / 2,
        self._pix)

    def mousePressEvent(self, ev):
        self.pressed.emit()
        self.update()

    def mouseReleaseEvent(self, ev):
        self.update()

class View(QGraphicsView):
    def resizeEvent(self, event):
        super(View, self).resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

if __name__ == '__main__':

    import sys
    import math
    app = QApplication(sys.argv)

    kineticPix = QPixmap("sol-images/palm.png")
    bgPix = QPixmap()
    app.setStyleSheet("""
        QGraphicsView {
          background-image: url('sol-images/still_background2.png');
          background-repeat: no-repeat;
          background-position: center center;
    }
    """)
    scene = QGraphicsScene(-310, -240, 625, 450)

    items = []
    for i in range(64):
        item = Pixmap(kineticPix)
        item.pixmap_item.setOffset(-kineticPix.width() / 2,
                -kineticPix.height() / 2)
        item.pixmap_item.setZValue(i)
        items.append(item)
        scene.addItem(item.pixmap_item)
        item.pixmap_item.setPos(-70, 170)

    # Cards as buttons
    buttonParent = QGraphicsRectItem()
    moveButton = Button(QPixmap('sol-images/s4.png'), buttonParent)
    centeredButton = Button(QPixmap('sol-images/palm.png'), buttonParent)

    moveButton.setPos(74, 40)
    centeredButton.setPos(-186, -102)

    scene.addItem(buttonParent)
    buttonParent.setPos(-73, -40) #positions groups of buttons
    buttonParent.setZValue(65)

    rootState = QState()
    moveState = QState(rootState)
    centeredState = QState(rootState)

    for i, item in enumerate(items):
        # move
        moveState.assignProperty(item, 'pos',
                QPointF(-500 + qrand() % 500, -400 + qrand() % 500)) #how big the effects are
        # centered
        centeredState.assignProperty(item, 'pos', QPointF())

    # interface
    view = View(scene)
    view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
    view.setBackgroundBrush(QBrush(bgPix))
    view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    view.setWindowFlags(Qt.FramelessWindowHint)
    view.show()

    states = QStateMachine()
    states.addState(rootState)
    states.setInitialState(rootState)
    rootState.setInitialState(centeredState)

    group = QParallelAnimationGroup()
    for i, item in enumerate(items):
        anim = QPropertyAnimation(item, b'pos')
        anim.setDuration(750 + i * 25)
        anim.setEasingCurve(QEasingCurve.InOutBack)
        group.addAnimation(anim)

    trans = rootState.addTransition(moveButton.pressed, moveState)
    trans.addAnimation(group)

    trans = rootState.addTransition(centeredButton.pressed, centeredState)
    trans.addAnimation(group)

    timer = QTimer()
    timer.start(125)
    timer.setSingleShot(True)
    trans = rootState.addTransition(timer.timeout, centeredState)
    trans.addAnimation(group)

    states.start()

# Draggable Cards' Window
    mainWidget = QWidget()
    horizontalLayout = QHBoxLayout()
    horizontalLayout.addWidget(DragWidget())

    mainWidget.setLayout(horizontalLayout)
    mainWidget.setGeometry(400, 348, 285, 300)
    mainWidget.setAttribute(Qt.WA_TranslucentBackground)
    mainWidget.setWindowFlags(Qt.FramelessWindowHint)

    mainWidget.show()

sys.exit(app.exec_())
