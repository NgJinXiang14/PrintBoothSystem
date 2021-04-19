import cups
import qpageview.cupsprinter
from time import sleep
import RPi.GPIO as GPIO
import math
import sys
import qpageview
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QPushButton, QWidget, QTreeView, QFileSystemModel, QVBoxLayout, QSpinBox, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt, QSize, QModelIndex, QDir, QSortFilterProxyModel, QRegExp, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QMovie, QPainter, QPixmap, QIcon, QFont

GPIO.setmode(GPIO.BCM)
counterPin=26
GPIO.setup(counterPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
file = ""
pagecount = 0
total = 0.00
coin = 0.0
option = ""
copies = "1"
colormode = ""
page= ""
vendoState = True

class Coin(QThread) :
    coinenter = pyqtSignal(float)
    def run(self) :
        while vendoState :
            input_state = GPIO.input(counterPin)
            
            if input_state == True :
                global coin
                coin+=0.10
                sleep(0.12)
                print('RM',f"{coin:.2f}")
                enabler = True
                self.coinenter.emit(coin)
               
def round_decimals_up(number:float, decimals:int=1):
    if not isinstance(decimals, int):
        raise TypeError()
    elif decimals < 0:
        raise ValueError()
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals
    return math.ceil(number * factor) / factor

class MainWindow(QMainWindow):
    my_signal = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        global file,pagecount,total,enabler,option
        file = ""
        pagecount = 0
        total=0.0
        option=""
        

        self.setWindowTitle("Printing Booth Systems")
        self.movie = QMovie("menu.gif")
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()
        self.btn = QPushButton('Touch here to Begin',self)
        self.btn.setGeometry(200, 230, 400, 100)
        self.btn.setFont(QFont('Arial',30))
        self.btn.clicked.connect(self.slot_btn_function)
        
    def paintEvent(self, event):
        currentFrame = self.movie.currentPixmap()
        frameRect = currentFrame.rect()
        frameRect.moveCenter(self.rect().center())
        if frameRect.intersects(event.rect()):
            painter = QPainter(self)
            painter.drawPixmap(frameRect.left(), frameRect.top(), currentFrame)
        
    def slot_btn_function(self):
        self.fs = FileSelect() 
        self.fs.showFullScreen()
        self.movie.stop()
        self.hide()
       
class FileSelect(QMainWindow,QWidget):
    
    def __init__(self):
        super(FileSelect, self).__init__()
        self.setWindowTitle("Printing Booth Systems")
        global file,pagecount,total,enabler,copies,colormode,page
        file = ""
        pagecount = 0
        total =0.0
        copies = "1"
        colormode = ""
        page= ""
        
        widget = QWidget()
        layout = QVBoxLayout()
        self.index= QModelIndex()
        self.model = QFileSystemModel()
        self.tree =  QTreeView()
        self.model.setRootPath(QDir.currentPath()) #ignore
        self.model.setNameFilters(["*.pdf"])
        
        idx = self.model.index("/media/pi/") 
      
        self.tree.setModel(self.model)
        self.tree.setRootIndex(idx)
        self.tree.setColumnWidth(0, 250)
        self.tree.setAlternatingRowColors(True)

        layout.addWidget(self.tree)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        widget.setFixedWidth(600)
        self.tree.setFont(QFont('Arial',25))
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.clicked.connect(self.on_treeView_clicked)
        
        self.btn1 = QPushButton('Select', self)
        self.btn1.setGeometry(620, 120, 150, 90)
        self.btn1.clicked.connect(self.slot_btn1_function)
        
        self.btn2 = QPushButton('Cancel', self)
        self.btn2.setGeometry(620, 300, 150, 90)
        self.btn2.clicked.connect(self.slot_btn2_function)
    
    def slot_btn1_function(self):
        if file.lower().endswith('.pdf') :
            self.p = Preview()
            self.p.showFullScreen()
            self.hide()
        else :  
            pass
        
    def slot_btn2_function(self):
        self.mw = MainWindow()
        self.mw.showFullScreen()
        self.hide()
    
    def on_treeView_clicked(self, index):
        global file
        indexItem = self.model.index(index.row(), 0, index.parent())        
        filePath = self.model.filePath(indexItem)
        file = filePath
        
class Preview(QMainWindow):
    
    def __init__(self):
        super(Preview, self).__init__()
        self.setWindowTitle("Printing Booth Systems")
        global pagecount,total,enabler
        
        total =0.0
     
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.view = qpageview.View()
        doc = self.view.loadPdf(file)
        
        self.view.setViewMode(qpageview.FitWidth) 
        layout.addWidget(self.view)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        widget.setFixedWidth(600)
        pagecount = self.view.pageCount()
        pageshow ="   " + str(pagecount) + " page(s)"
        
        self.L1 = QLabel(self)
        self.L1.setFont(QFont('Arial',17))
        self.L1.setFixedSize(160,50)
        self.L1.setText(pageshow)
        self.L1.move(620, 30)
        self.L1.setStyleSheet("""background-color: white;""")
        
        self.btn1 = QPushButton('Confirm', self)
        self.btn1.setGeometry(620, 120, 150, 90)
        self.btn1.clicked.connect(self.slot_btn1_function)
        
        self.btn2 = QPushButton('Cancel', self)
        self.btn2.setGeometry(620, 300, 150, 90)
        self.btn2.clicked.connect(self.slot_btn2_function)
    
    def slot_btn1_function(self):
        self.o = Option()
        self.o.showFullScreen()
        self.hide()
        
    def slot_btn2_function(self):
        self.fs = FileSelect()
        self.fs.showFullScreen()
        self.hide()
        
class Option(QMainWindow):
    def __init__(self):
        super(Option, self).__init__()
        self.setWindowTitle("Printing Booth Systems")
       
        global total,option
        self.mode = 0
        self.coin_en = Coin()
    
        self.L1 = QLabel(self)
        self.L2 = QLabel(self)
        self.L3 = QLabel(self)
        self.L4 = QLabel(self)
        self.L5 = QLabel(self)
        self.L6 = QLabel(self)
        self.L7 = QLabel(self)
        self.L8 = QLabel(self)
        self.L9 = QLabel(self)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_coincheck)
        self.timer.start(1)
        
        self.spin = QSpinBox(self)
        
        self.check1 = QCheckBox('',self)
        self.check2 = QCheckBox('',self)
        
        self.L1.setFont(QFont('Arial',17))
        self.L2.setFont(QFont('Arial',17))
        self.L3.setFont(QFont('Arial',17))
        self.L4.setFont(QFont('Arial',17))
        self.L5.setFont(QFont('Arial',17))
        self.L6.setFont(QFont('Arial',17))
        self.L7.setFont(QFont('Arial',17))
        self.L8.setFont(QFont('Arial',17))
        self.L9.setFont(QFont('Arial',17))
        self.spin.setFont(QFont('Arial',25))
        
        self.L1.setFixedSize(300,50)
        self.L2.setFixedSize(300,50)
        self.L3.setFixedSize(300,50)
        self.L4.setFixedSize(300,40)
        self.L5.setFixedSize(300,40)
        self.L6.setFixedSize(10,40)
        self.L7.setFixedSize(300,50)
        self.L8.setFixedSize(10,40)
        self.L9.setFixedSize(300,40)
        self.spin.setFixedSize(300,135)
        self.check1.setFixedSize(40,40)
        self.check2.setFixedSize(40,40)
        
        self.L6.setText(":")
        self.L1.setText("Grand Total Cost")
        self.L2.setText("Starting Page              : ")
        self.L3.setText("Inserted Coins Values : ")
        self.L4.setText("")
        self.L7.setText("Total After Deduction")
        self.L8.setText(":")
        self.L9.setText("")
        
        self.L1.move(50, 30)
        self.L2.move(50, 80)
        self.L3.move(50, 230)
        self.L4.move(300, 35)
        self.L5.move(300, 230)
        self.L6.move(279, 35)
        self.L7.move(50, 280)
        self.L8.move(279, 285)
        self.L9.move(300, 285)
        self.spin.move(300, 85)
        self.check1.move(115, 440)
        self.check2.move(365, 440)
        
        self.spin.setAlignment(Qt.AlignCenter)
        
        self.check1.setEnabled(False)
        self.check2.setEnabled(False)
        
        self.L4.setStyleSheet("""background-color: white;""")
        self.L5.setStyleSheet("""background-color: white;""")
        self.L9.setStyleSheet("""background-color: white;""")
        self.spin.setStyleSheet("""
}

QSpinBox::up-button  {
  subcontrol-origin: margin;
  subcontrol-position: center right;

  right: 10px;
  height: 100px;
  width: 100px;
}

QSpinBox::down-button  {
  subcontrol-origin: margin;
  subcontrol-position: center left;

  left: 10px;
  height: 100px;
  width: 100px;
}""")
        
        self.spin.setMinimum(1)
        self.spin.setMaximum(pagecount)

        self.btn1 = QPushButton('Print', self)
        self.btn1.setGeometry(620, 150, 150, 170)
        self.btn1.clicked.connect(self.slot_btn1_function)

        self.btn2 = QPushButton('Cancel', self)
        self.btn2.setGeometry(620, 30, 150, 90)
        self.btn2.clicked.connect(self.slot_btn2_function)
        
        self.btn5 = QPushButton('Colour', self)
        self.btn5.setGeometry(50, 340, 150, 90)
        self.btn5.clicked.connect(self.slot_colour_function)
        self.btn6 = QPushButton('Black White', self)
        self.btn6.setGeometry(300, 340, 150, 90)
        self.btn6.clicked.connect(self.slot_bw_function)
  
    def slot_btn1_function(self):
        global coin
        
        self.h = qpageview.cupsprinter.handle()
        page = str(self.spin.value())+"-"+str(pagecount)
        print(copies)
        print(colormode)
        print(page)
        
        if self.h:
            self.h.printFile(file ,'None', {'copies' : copies ,'print-color-mode' : colormode,'page-ranges' : page})
        coin = 0.0
        self.fs = MainWindow()
        self.fs.showFullScreen()
        self.hide()
        
    def slot_btn2_function(self):
        self.fs = FileSelect()
        self.fs.showFullScreen()
        self.hide()
    
    def slot_colour_function(self):
        self.check1.setChecked(True)
        self.check2.setChecked(False)
        global pagecount, total,colormode
        
        colormode = ""
        spinvalue = self.spin.value() - 1
        total = ((pagecount - spinvalue )*0.25)
        self.L4.setText("RM" + "{:.1f}".format(round_decimals_up(total))+"0")
    
    def slot_bw_function(self):
        self.check2.setChecked(True)
        self.check1.setChecked(False)
        global pagecount, total,colormode
        
        colormode="monochrome"
        spinvalue = self.spin.value() - 1
        total = ((pagecount - spinvalue)*0.12)
        self.L4.setText("RM" + "{:.1f}".format(round_decimals_up(total))+"0")
          
    def refresh_coincheck(self):
        global pagecount, total,coin
        
        self.L5.setText("RM" + "{:.1f}".format(round_decimals_up(coin))+"0")
        
        if self.check1.isChecked() == True:
            spinvalue = self.spin.value() - 1
            total = ((pagecount - spinvalue )*0.25)
            self.L4.setText("RM" + "{:.1f}".format(round_decimals_up(total))+"0")
            self.L9.setText("RM" + "{:.1f}".format(round_decimals_up(total-coin))+"0")
            #option = '{"page-range": "'+str(self.spin.value())+","+str(pagecount)+'"}'
            #print (option)
        elif self.check2.isChecked() == True :
            
            spinvalue = self.spin.value() - 1
            total = ((pagecount - spinvalue)*0.12)
            self.L4.setText("RM" + "{:.1f}".format(round_decimals_up(total))+"0")
            self.L9.setText("RM" + "{:.1f}".format(round_decimals_up(total-coin))+"0")
        else :
            pass
        
        if coin >= total :
            if coin != 0 and total != 0:
                self.btn1.setEnabled(True)
            else :
                self.btn1.setEnabled(False)
        else :
            self.btn1.setEnabled(False)
    
worker = Coin()
worker.start()

def main():
    
    app = QApplication(sys.argv)
    QApplication.processEvents()
    w = MainWindow()
    w.showFullScreen()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
