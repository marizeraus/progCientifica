from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *
from griddialog import *

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("P1")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("static/fit.png"), "fit", self)
        grid = QAction(QIcon("static/grid.png"), "grid", self)
        tb.addAction(fit)
        tb.addAction(grid)
        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self, a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "grid":
            self.dialog = GridDialog(self)
            self.dialog.show()
