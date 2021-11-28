from PyQt5.QtWidgets import *

class GridDialog(QWidget):
    
  def __init__(self, window):

    super().__init__()
    self.window = window
    self.setGeometry(200, 200, 200, 200)
    self.setWindowTitle('Grade')
    self.vbox = QVBoxLayout()

    text = QLabel('Gerar grade de pontos')

    horLabel = QLabel('Divisões horizontais')
    self.horEdit = QLineEdit()
    verLabel = QLabel('Divisões verticais')
    self.verEdit = QLineEdit()
    button = QPushButton('Gerar')

    self.vbox.addWidget(text)

    self.vbox.addWidget(horLabel)
    self.vbox.addWidget(self.horEdit)
    self.vbox.addWidget(verLabel)
    self.vbox.addWidget(self.verEdit)
    self.vbox.addWidget(button)

    self.setLayout(self.vbox)
    self.submitted = False    
    button.clicked.connect(self.genGrid)

  def genGrid(self):
    horizontal = int(self.horEdit.text())
    vertical = int(self.verEdit.text())

    self.window.canvas.genGrid(horizontal, vertical)
    self.close()
