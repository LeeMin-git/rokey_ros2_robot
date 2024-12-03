# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys
import rclpy
import threading
from serving_robot.Ui import Ui_Form
from PyQt5.QtWidgets import QWidget,QApplication
from PyQt5.QtCore import QTimer
from serving_robot_msgs.srv import T2C
from serving_robot_msgs.action import C2R
from serving_robot_msgs.msg import RobotState
from serving_robot_msgs.msg import TotalPrice2C
from rclpy.node import Node
from PyQt5.QtCore import pyqtSignal
from rclpy.action import ActionClient
from rclpy.action.client import GoalStatus

class Rosnode(Node):
    def __init__(self,gui):
        super().__init__('controller')
        self.gui=gui
        self.oder_server=self.create_service(T2C,'T2C',self.callback)
        self.goal_client=ActionClient(self,C2R,'/table_number')
        self.total_price_sub = self.create_subscription(TotalPrice2C,'total_price',self.total_price_sub_callback,10)
        self.robot_state_sub=self.create_subscription(RobotState,'/state',self.ch_robot_state,10)

        #새로 추가한 부분
        self.tatal_data_dict = {} #테이블 별 매뉴 기록
        self.total_price=0

    def ch_robot_state(self,msg):
        a = msg.state
        self.gui.btn_update_signal.emit(a)

    def total_price_sub_callback(self, msg):
        self.total_price = msg.price
        self.gui.menu_update_signal.emit(self.table_number,self.tatal_data,self.price,self.total_price)
    #새로 추가한 부분

    def callback(self,req,res):
        self.table_number = req.table_number
        self.menu = req.menu
        self.menu_number = req.menu_number
        self.price = req.price
        self.get_logger().info(str(self.table_number))
        #변경 부분
        #table_number를 받아서 각 테이블 별로 주문 내역을 기록하여 gui에 표시
        if self.table_number in self.tatal_data_dict:
            self.tatal_data = self.tatal_data_dict[self.table_number]  # Get existing order for this table
        else:
            self.tatal_data = ''  # No previous orders, initialize with an empty string
        #변경 부분
        for i in range(len(self.menu)):
            self.tatal_data+=(self.menu[i]+' '+str(self.menu_number[i])+'\n')

        self.tatal_data_dict[self.table_number] = self.tatal_data

        res.succeed = True
        self.gui.robot_move_state = True
        return res

    def send_goal(self):
        wait_count=1
        while not self.goal_client.wait_for_server(timeout_sec=0.1):
            if wait_count>5:
                self.get_logger().info('Robot goal server is not avaliable')
                return False
            wait_count += 1
        goal_num = C2R.Goal()
        goal_num.table_num = self.table_num

        print(goal_num)
        self.send_goal_future=self.goal_client.send_goal_async(
            goal_num
            )
        self.send_goal_future.add_done_callback(self.change_robot_state)
        return True

    def test(self,feedback):
        pass

    def send_goal_table_num(self,n):
        wait_count=1
        while not self.goal_client.wait_for_server(timeout_sec=0.1):
            if wait_count>5:
                self.get_logger().info('Robot goal server is not avaliable')
                return False
            wait_count += 1
        goal_num = C2R.Goal()
        goal_num.table_num = n
        print(n)
        print(goal_num)
        self.send_goal_future=self.goal_client.send_goal_async(
            goal_num
            )
        self.send_goal_future.add_done_callback(self.change_robot_state)
        return True

    def test(self,feedback):
        pass

    def change_robot_state(self,future):
        goal_handle=future.result()
        if not goal_handle.accepted:
            self.get_logger().info('goal rejected')
            return
        self.action_result=goal_handle.get_result_async()
        self.action_result.add_done_callback(self.result)

    def result(self,future):
        action_state=future.result().status
        action_result=future.result().result
        if action_state==GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("succeed!!!")
        else:
            self.get_logger().info("fail...")

class Mainwindow(QWidget):
    menu_update_signal=pyqtSignal(int,str,int,int)
    btn_update_signal=pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.ui_setup=Ui_Form()
        self.ui_setup.setupUi(self)
        self.setWindowTitle('Kitchen GUI')
        self.menu_update_signal.connect(self.display)
        self.btn_update_signal.connect(self.btn)
        self.robot_move_state = True
        self.table_widgets = {
            1: (self.ui_setup.textBrowser_table_1, self.ui_setup.label_price_1),
            2: (self.ui_setup.textBrowser_table_2, self.ui_setup.label_price_2),
            3: (self.ui_setup.textBrowser_table_3, self.ui_setup.label_price_3),
            4: (self.ui_setup.textBrowser_table_4, self.ui_setup.label_price_4),
            5: (self.ui_setup.textBrowser_table_5, self.ui_setup.label_price_5),
            6: (self.ui_setup.textBrowser_table_6, self.ui_setup.label_price_6),
            7: (self.ui_setup.textBrowser_table_7, self.ui_setup.label_price_7),
            8: (self.ui_setup.textBrowser_table_8, self.ui_setup.label_price_8),
            9: (self.ui_setup.textBrowser_table_9, self.ui_setup.label_price_9),
        } #테이블 번호에 따른 mapping 데이터

        rclpy.init()
        self.node = Rosnode(self)
        self.thread = threading.Thread(target=rclpy.spin, args=(self.node, ))
        self.thread.start()
        self.blink_timer = None
        self.table_num = 0

    def display(self,table_number,msg,price,total):
        text_browser, label_price = self.table_widgets.get(table_number, (None, None))
        if text_browser and label_price:
            text_browser.setText(msg)
            label_price.setText(str(price))
            self.start_blinking(text_browser)
        self.ui_setup.label_revenue_val.setText(str(total))

    def btn(self,state):
        if state:
            self.ui_setup.btn_send_food.setEnabled(True)

    def start_blinking(self, text_browser):
        # 점멸 효과 시작
        if self.blink_timer is not None and self.blink_timer.isActive():
            self.blink_timer.stop()
        blink_count = 0

        def toggle_color():
            nonlocal blink_count
            if blink_count < 6:  # 3회 점멸
                if blink_count % 2 == 0:
                    text_browser.setStyleSheet("background-color: red;")
                else:
                    text_browser.setStyleSheet("")
                blink_count += 1
            else:
                # 3회 점멸 후 정지
                text_browser.setStyleSheet("")  # 색갈 되돌리기

        # 500ms로 점멸 시간 설정
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(toggle_color)
        self.blink_timer.start(500)  # 500ms마다 점멸

    def send_table_num(self, n):
        print(n)
        self.node.send_goal_table_num(n)

def main():
    app=QApplication([])
    window=Mainwindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
