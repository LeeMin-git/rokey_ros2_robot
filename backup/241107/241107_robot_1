import rclpy
import sys
from rclpy.node import Node
from serving_robot_msgs.action import C2R
from serving_robot.robot import Ui_Form
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget,QApplication

class RosNode(Node):
    def __init__(self,GUI):
        super().__init__('robot')

class Mainwindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui_setting=Ui_Form()
        self.ui_setting.setupUi(self)
        self.setWindowTitle('Robot Status')

def main():
    app=QApplication([])
    window=Mainwindow()
    window.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()




