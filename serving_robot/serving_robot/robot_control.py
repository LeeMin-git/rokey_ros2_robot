import rclpy
import sys
import threading
import time
from rclpy.node import Node
from rclpy.action import ActionServer,ActionClient
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from serving_robot_msgs.action import C2R
from serving_robot_msgs.msg import RobotState
from serving_robot.robot import Ui_Form
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget,QApplication

class RosNode(Node):
    def __init__(self,GUI):
        super().__init__('robot')
        self.gui=GUI
        self.table_pos = [[-2.0,-0.5],
                          [1.12,1.53],[1.12,0.44],[1.12,-0.62],
                          [0.0,1.53],[0.0,0.44],[0.0,-0.62],
                          [-1.0,1.53],[-1.0,0.44],[-1.0,-0.62]                          
                          ] # 0~9까지의 테이블 번호 0 = 주방

        self.cur_table_num = 0 # 받아온 테이블 번호 저장
        self.logger='' # log 표시할 함수
        # self.cur_pos_goal = [0,0] # 현재 목표 위치 저장

        self.action_ser_table = ActionServer(self,C2R,'/table_num',self.table_callback)
        self.action_cli_send_goal = ActionClient(self,NavigateToPose,"navigate_to_pose")
        self.robot_state_pub = self.create_publisher(RobotState,'/state',10)
    
    def table_callback(self,goal_handle):
        #관제에서 로봇으로 테이블 번호를 받아서 실행
        self.cur_table_num = goal_handle.request.table_num
        self.cur_pos_goal = self.table_pos[self.cur_table_num]
        result=C2R.Result()
        result.done=True
        goal_handle.succeed()
        self.send_table_goal(self.cur_pos_goal[0],self.cur_pos_goal[1])
        return result
    
    def send_table_goal(self,pos_x,pos_y):
        wait_cnt=1
        while not self.action_cli_send_goal.wait_for_server(timeout_sec=0.1):
            if wait_cnt > 3:
                self.get_logger().info('[robot] nav action server is not avaliable')
                wait_cnt+=1
                return False
            wait_cnt+=1

        goal_msg=NavigateToPose.Goal()
        goal_msg.pose.header.frame_id='map'
        goal_msg.pose.pose.position.x=pos_x
        goal_msg.pose.pose.position.y=pos_y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0
        goal_msg.pose.pose.orientation.w=1.0

        self.send_goal_future=self.action_cli_send_goal.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.get_action_goal)
        return True
    
    def get_action_goal(self,future):
        goal_handle=future.result()
        if not goal_handle.accepted:
            self.get_logger().info('[robot] goal send rejected')
            return
        self.logger += '%d번 테이블로 이동 중...\n'%self.cur_table_num
        self.gui.log_signal.emit(str(self.cur_table_num),self.logger)
        self.get_logger().info(self.logger)
        self.result_future = goal_handle.get_result_async()
        self.result_future.add_done_callback(self.get_action_result)
    
    def get_action_result(self,future):
        action_state=future.result().status
        if action_state == GoalStatus.STATUS_SUCCEEDED:
            self.logger += '%d번 테이블 도착!!!\n'%self.cur_table_num
            self.gui.log_signal.emit(str(self.cur_table_num),self.logger)
            self.get_logger().info("[robot] 도착")
            ### 목적지까지 갔다가 주방으로 다시 돌아오게 하기 위해
            if self.cur_table_num != 0:
                time.sleep(3)
                self.cur_table_num = 0
                self.cur_pos_goal = self.table_pos[self.cur_table_num]
                self.send_table_goal(self.cur_pos_goal[0],self.cur_pos_goal[1])
            else:
                robot_state = RobotState()
                robot_state.state = True
                self.robot_state_pub.publish(robot_state)
        else:
            self.get_logger().warning('[robot] 도착 못함')

class Mainwindow(QWidget):
    log_signal=pyqtSignal(str,str)
    def __init__(self):
        super().__init__()
        self.ui_setting=Ui_Form()
        self.ui_setting.setupUi(self)
        self.setWindowTitle('Robot Status')
        self.log_signal.connect(self.display_update)

        rclpy.init()
        self.node=RosNode(self)
        self.thread = threading.Thread(target=rclpy.spin,args=(self.node,))
        self.thread.start()

    def display_update(self,num,log):
        self.ui_setting.textBrowser_table_num.setText(num)
        self.ui_setting.textBrowser_log.setText(log)

def main():
    app=QApplication([])
    window=Mainwindow()
    window.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()




