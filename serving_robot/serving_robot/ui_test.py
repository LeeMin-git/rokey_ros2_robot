# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# 코드로 실행 하려면 from aaaaa import Ui_Form 가능
'''ros2 run으로 ui 실행 되는 코드'''
from serving_robot.Ui import Ui_Form
from PyQt5.QtWidgets import QWidget,QApplication
import sys
from serving_robot_msgs.srv import T2C #테이블 오더에서 컨트롤러(주방)으로 보내는 메시지
import rclpy
from rclpy.node import Node

t_date = 1106
t_num=1
t_spice=['후라이드','양념','간장']
t_count=[1,2,3]

class Mainwindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui_setup=Ui_Form()
        self.ui_setup.setupUi(self)
        self.setWindowTitle('Kitchen GUI')
        self.a=''
        #self.node=Node('test')
        for i in range(len(t_spice)):
            self.a+=(t_spice[i]+' '+str(t_count[i])+'\n')
        self.ui_setup.textBrowser_table_1.setText(self.a)
        self.show()
        self.node.create_service(T2C,'/test',self.callback)
    
    def callback(self,req,res):
        self.a = req.table_number
        self.b = req.menu
        self.c = req.menu_number
        self.d = req.price

        res.succeed = True
        return res
        

def main():
    rclpy.init()
    app=QApplication(sys.argv)
    window=Mainwindow()
    #window.node.destroy_node()
    #rclpy.shutdown()
    QApplication.processEvents() #이벤트에 대한 루프 처리
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
