import json
from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from OpenGL.GL import *
from hetool import HeController, HeModel, HeView, Tesselation, Point

class MyCanvas(QtOpenGL.QGLWidget):
    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_w = 0 # width: GL canvas horizontal size
        self.m_h = 0 # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPoint(0.0,0.0)
        self.m_pt1 = QtCore.QPoint(0.0,0.0)
        
        self.tol = 0.1
        self.hemodel = HeModel()
        self.heview = HeView(self.hemodel)
        self.hecontroller = HeController(self.hemodel)

        self.grid = []

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)
    
    def resizeGL(self, _width, _height):
        self.m_w = _width
        self.m_h = _height
        if(self.m_model==None)or(self.m_model.isEmpty()): 
            self.scaleWorldWindow(1.0)
        else:
            self.m_L,self.m_R,self.m_B,self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)
        
        glViewport(0, 0, self.m_w, self.m_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L,self.m_R,self.m_B,self.m_T,-1.0,1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def setModel(self,_model):
        self.m_model = _model
        
    def fitWorldToViewport(self):
        print("fitWorldToViewport")
        if self.hemodel == None:
            return
        self.m_L,self.m_R,self.m_B,self.m_T=self.heview.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()
    
    def scaleWorldWindow(self,_scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w
        
        # Get current window center.
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        
        # Set new window sizes based on scaling factor.
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac
        
        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr
        
        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        
        # Establish the clipping volume by setting up an orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        
    def panWorldWindow(self, _panFacX, _panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)    
    
    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x,y)
    
    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        self.m_pt0 = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        print(self.m_pt0.x(), self.m_pt0.y())
        print(self.m_pt1.x(), self.m_pt1.y())
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        print(pt0_U.x, pt0_U.y, pt1_U.x, pt1_U)
        self.m_model.setCurve(pt0_U.x(),pt0_U.y(),pt1_U.x(),pt1_U.y())
        self.hecontroller.insertSegment([pt0_U.x(),pt0_U.y(),pt1_U.x(),pt1_U.y()], self.tol)
        self.m_buttonPressed = False
        self.m_pt0.setX(0.0)
        self.m_pt0.setY(0.0)
        self.m_pt1.setX(0.0)
        self.m_pt1.setY(0.0)
        self.update()
        self.paintGL()
    
    def genGrid(self, hor, ver):
        self.grid = []
        l, r, b, t = self.heview.getBoundBox()

        hor_size = r-l
        ver_size = t-b
        hDiv = hor_size / float(hor-1)
        vDiv = ver_size / float(ver-1)
        patches = self.heview.getPatches()
        for v in range(ver):
            for h in range(hor):
                px = l + hDiv * h
                py = b + vDiv * v
                for pat in patches:
                    if pat.isPointInside(Point(px, py)):
                        self.grid.append(Point(px, py))
                        break
        
        if len(self.grid) > 0:
            f = open("grid_Points.json", "w")
            point_list = []
            for point in self.grid:
                point_list.append({
                    "x" : point.getX(),
                    "y": point.getY()
                })
            jsonDic = {
                "points": point_list
            }
            json.dump(jsonDic, f, indent=4)

        self.update()
        self.repaint()


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        # if(self.m_model==None)or(self.m_model.isEmpty()): return
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        
        # desenho dos pontos coletados
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()

        if not((self.m_model == None) and (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0) # blue
            glBegin(GL_LINES)
            for curv in curves:
                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()
            
        if not(self.heview.isEmpty()):
            patches = self.heview.getPatches() # retalhos, regioes constru??das automaticamente
            glColor3f(2.0, 0.0, 1.0)

            for pat in patches:
                triangs = Tesselation.tessellate(pat.getPoints())
                for triang in triangs:
                    glBegin(GL_TRIANGLES)
                    for pt in triang:
                        glVertex2d(pt.getX(), pt.getY())
                    glEnd()

            segments = self.heview.getSegments()
            glColor3f(0.0, 1.0, 1.0) #linha
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glBegin(GL_LINES)

                glVertex2f(ptc[0].getX(), ptc[0].getY())
                glVertex2f(ptc[1].getX(), ptc[1].getY())
                
                glEnd()
                
            verts = self.heview.getPoints()
            glColor3f(1.0, 0.0, 0.0)
            glPointSize(1)
            glBegin(GL_POINTS)
            for vert in verts:
                glVertex2f(vert.getX(), vert.getY())
            glEnd()

            glColor3f(0.0, 0.0, 0.0)
            glPointSize(1.5)
            glBegin(GL_POINTS)
            if len(self.grid) > 0:
                for point in self.grid:
                    glVertex2f(point.getX(), point.getY())
            glEnd()
                
        glEndList()

