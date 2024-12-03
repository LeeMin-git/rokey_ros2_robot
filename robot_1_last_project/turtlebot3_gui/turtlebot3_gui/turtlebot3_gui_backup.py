import sys
import threading

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped
from geometry_msgs.msg import PoseWithCovarianceStamped, Pose, Point, Quaternion
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import SetInitialPose
from rclpy.action.client import GoalStatus

class NavigationClient(Node):
    def __init__(self):
        super().__init__('node')
        # setting
        self.len = 3
        self.init_pose = [-2.0, -0.5, 0.0, 1.0] # pose:x,y orient:z,w

        
        # init
        self.goal_poses = [[0,0] for i in range(self.len)]
        self.setting_poses = [False for i in range(self.len)]
        
        # GUI
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.create_gui()
        
        self.publisher = self.create_publisher(String, 'example_topic', 10)
        
        # create Topic Subscriber
        self.clicked_point_subscriber = self.create_subscription(
            PointStamped,
            "clicked_point",
            self.clicked_point_callback,
            10
            )
        
        # create Service Clinet
        self.set_initial_pose_service_client = self.create_client(SetInitialPose, '/set_initial_pose')
        
        # create Action Client
        self.navigate_to_pose_action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        #원점 복귀 액션 클라이언트 생성
        #self.navigate_to_zero_pose_action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        
        # Init function
        while not self.set_initial_pose_service_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service /set_initial_pose not available, waiting again...')
        self.set_initial_pose(*self.init_pose)
        
        
    def create_gui(self):
        self.window.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.window.resize(274, 180 + 40* self.len)
        self.centralwidget = QWidget(self.window)
        self.centralwidget.setObjectName(u"centralwidget")
        
        self.getButtons = [None for i in range(self.len)]
        self.getButtons_geo = [19, 20, 51, 23]
        for i in range(self.len):
            self.getButtons[i] = QPushButton(self.centralwidget)
            self.getButtons[i].setObjectName(f"getButton_{i}")
            self.getButtons[i].setGeometry(QRect(*self.getButtons_geo))
            self.getButtons[i].setText(QCoreApplication.translate("MainWindow", f"get{i}", None))
            self.getButtons[i].clicked.connect(lambda checked, i=i: self.get_button_clicked(i))
            self.getButtons_geo[1] +=40
            
        self.labels = [None for i in range(self.len)]
        self.labels_geo = [90, 20, 131, 23]
        for i in range(self.len):
            self.labels[i] = QLabel(self.centralwidget)
            self.labels[i].setObjectName(f"label_{i}")
            self.labels[i].setGeometry(QRect(*self.labels_geo))
            self.labels[i].setText(QCoreApplication.translate("MainWindow", "x= 0.0, y= 0.0", None))
            self.labels_geo[1] +=40
        
        self.goButtons_geo = [200, 20, 51, 23]
        self.goButtons = [None for i in range(self.len)]
        for i in range(self.len):
            self.goButtons[i] = QPushButton(self.centralwidget)
            self.goButtons[i].setObjectName(f"goButton_{i}")
            self.goButtons[i].setGeometry(QRect(*self.goButtons_geo))
            self.goButtons[i].setText(QCoreApplication.translate("MainWindow", f"go{i}", None))
            self.goButtons[i].clicked.connect(lambda checked, i=i: self.go_button_clicked(i))
            self.goButtons_geo[1] +=40
        #복귀버튼 추가
        '''self.goZeroButtons = QPushButton(self.centralwidget)
        self.goZeroButtons.setObjectName(f"복귀")
        self.goZeroButtons.setGeometry(QRect(*self.goButtons_geo))
        self.goZeroButtons.setText(QCoreApplication.translate("MainWindow", f"복귀", None))
        self.goZeroButtons.clicked.connect(self.go_button_clicked_zero)'''



        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(20, 20 +80 *self.len, 231, 101))

        self.window.setCentralWidget(self.centralwidget)

    def get_button_clicked(self, i):
        self.setting_poses[i] = True

    def go_button_clicked(self, i):
        self.navigate_to_pose_send_goal(i)
        
    def go_button_clicked_zero(self):
        self.navigate_to_zero_pose_send_goal()
    
    # Topic subscriber GET POSE
    def clicked_point_callback(self, msg):
        for i in range(self.len):
            if self.setting_poses[i]:
                x = round(float(msg.point.x),1)
                y = round(float(msg.point.y),1)   
                self.goal_poses[i][0] = x
                self.goal_poses[i][1] = y

                self.labels[i].setText(QCoreApplication.translate(
                    "MainWindow",
                    f"x= {x:.1f}, y= {y:.1f}",
                    None))
                message = f"[GET] table_{i} is x= {x:.1f}, y= {y:.1f}"
                self.textBrowser.append(message)
                
                self.setting_poses[i] = False


    # Service client SET INIT POSE ESTIMATE
    def set_initial_pose(self, x,y,z,w):
        req = SetInitialPose.Request()
        req.pose.header.frame_id = 'map'
        req.pose.pose.pose.position = Point(x=x, y=y, z=0.0)
        req.pose.pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=z, w=w)
        req.pose.pose.covariance = [0.1, 0.0, 0.0, 0.0, 0.0, 0.1,
                              0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                              0.0, 0.0, 0.1, 0.0, 0.0, 0.0,
                              0.0, 0.0, 0.0, 0.01, 0.0, 0.0,
                              0.0, 0.0, 0.0, 0.0, 0.01, 0.0,
                              0.0, 0.0, 0.0, 0.0, 0.0, 0.01]

        future = self.set_initial_pose_service_client.call_async(req)
        
        if future.result() is not None:
            message = "[INFO] Initial pose set successfully"
        else:
            message = "[WARN] Failed to set initial pose"
            
        self.textBrowser.setText(message)
        
        return future.result()

    
    ## Action client NAVIGATE  이것을 이용해야한다.
    def navigate_to_pose_send_goal(self, i):
        wait_count = 1
        while not self.navigate_to_pose_action_client.wait_for_server(timeout_sec=0.1):
            if wait_count > 3:
                message = "[WARN] Navigate action server is not available."
                self.textBrowser.append(message)
                return False
            wait_count += 1
            
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = self.goal_poses[i][0]
        goal_msg.pose.pose.position.y = self.goal_poses[i][1]
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.send_goal_future = self.navigate_to_pose_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.navigate_to_pose_action_feedback)
        self.send_goal_future.add_done_callback(self.navigate_to_pose_action_goal)
        
        return True
    
    ## Action client NAVIGATE  이것을 이용해야한다.
    def navigate_to_zero_pose_send_goal(self):
        wait_count = 1
        while not self.navigate_to_zero_pose_action_client.wait_for_server(timeout_sec=0.1):
            if wait_count > 3:
                message = "[WARN] Navigate action server is not available."
                self.textBrowser.append(message)
                return False
            wait_count += 1
            
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = 0.0
        goal_msg.pose.pose.position.y = 0.0
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.send_goal_future = self.navigate_to_zero_pose_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.navigate_to_pose_action_feedback)
        self.send_goal_future.add_done_callback(self.navigate_to_pose_action_goal)
        
        return True
    
    def navigate_to_pose_action_goal(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            message = "[WARN] Action goal rejected."
            self.textBrowser.append(message)
            return

        message = "[INFO] Action goal accepted."
        self.textBrowser.append(message)
        self.action_result_future = goal_handle.get_result_async()
        self.action_result_future.add_done_callback(self.navigate_to_pose_action_result)

    def navigate_to_pose_action_feedback(self, feedback_msg):
        action_feedback = feedback_msg.feedback
        # self.get_logger().info("Action feedback: {0}".format(action_feedback))

    def navigate_to_pose_action_result(self, future):
        action_status = future.result().status
        action_result = future.result().result
        if action_status == GoalStatus.STATUS_SUCCEEDED:

            message = "[INFO] Action succeeded!."
            self.textBrowser.append(message)

        else:
            message = f"[WARN] Action failed with status: {action_status}"
            self.textBrowser.append(message)
    
        
    def run(self):
        self.ros_thread = threading.Thread(target=self.run_ros, daemon=True)
        self.ros_thread.start()
        
        self.window.show()
        sys.exit(self.app.exec_())
        
        
    def run_ros(self):
        rclpy.spin(self)
        
        
def main():
    rclpy.init()
    node = NavigationClient()
    node.run()
    
    try:
        rclpy.shutdown()
    finally:
        node.destroy_node()
    
if __name__ == '__main__':
    main()