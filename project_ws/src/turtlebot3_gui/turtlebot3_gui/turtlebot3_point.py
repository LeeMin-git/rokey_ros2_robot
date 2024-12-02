import sys
import rclpy
import threading
from rclpy.node import Node
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue

from PyQt5.QtWidgets import QApplication,QGridLayout,  QMainWindow, QTextEdit, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, pyqtSignal

from std_msgs.msg import String
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from rclpy.action.client import GoalStatus
from geometry_msgs.msg import PointStamped

class GuiNode(Node):
    """ROS2 노드 클래스"""
    def __init__(self,GUI):
        super().__init__("gui_node")
        self.GUI = GUI

        # Subscriber 생성
        self.clicked_point_subscriber = self.create_subscription(PointStamped,"clicked_point",self.clicked_point_callback,10)
        
        # Action Client 생성
        self.navigate_to_pose_action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        # Service Cline 생성
        self.set_yaw_goal_tolerance_client = self.create_client(SetParameters, "/controller_server/set_parameters")

        # Init
        self.set_yaw_goal_tolerance("general_goal_checker.yaw_goal_tolerance", 7.0)
        self.position = [0.0, 0.0]


    # TOPIC SUBSCRIBER GOAL SETTING
    def clicked_point_callback(self, msg):
        if self.GUI.setting_position:
            
            self.position[0] = round(float(msg.point.x),1)
            self.position[1] = round(float(msg.point.y),1)

            message = f"[COMPLETE] Goal is {self.position[0]}, {self.position[1]}"
            self.GUI.update_signal.emit(message)

            name = f"Move to {self.position[0]}, {self.position[1]}"
            self.GUI.change_button_name(name)

            self.GUI.setting_position = False
    
        
    ## ACTION CLIENT NAVIGATE      
    def navigate_to_pose_send_goal(self):
        wait_count = 1
        while not self.navigate_to_pose_action_client.wait_for_server(timeout_sec=0.1):
            if wait_count > 3:
                message = "[WARN] Navigate action server is not available."
                self.GUI.update_signal.emit(message)
                return False
            wait_count += 1


        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = self.position[0]
        goal_msg.pose.pose.position.y = self.position[1]
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

    def navigate_to_pose_action_goal(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            message = "[WARN] Action goal rejected."
            self.GUI.update_signal.emit(message)
            return

        message = "[INFO] Action goal accepted."
        self.GUI.update_signal.emit(message)
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
            self.GUI.update_signal.emit(message)

        else:
            message = f"[WARN] Action failed with status: {action_status}"
            self.GUI.update_signal.emit(message)

    # SERVICE CLIENT SET PARAMETER
    def set_yaw_goal_tolerance(self, parameter_name, value):
        request = SetParameters.Request()
        parameter = ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=value)
        request.parameters = [Parameter(name=parameter_name, value=parameter)]
        service_client = self.set_yaw_goal_tolerance_client
        return self.call_service(service_client, request, "yaw_goal_tolerance parameter")


    def call_service(self, service_client, request, service_name):
        wait_count=1
        while not service_client.wait_for_service(timeout_sec=0.1):
            if wait_count > 10:
                message = f"[WARN] {service_name} service is not available"
                self.GUI.update_signal.emit(message)
                return False
            wait_count += 1

        message = f"[INIT] Set to have no yaw goal"
        self.GUI.update_signal.emit(message)
        service_client.call_async(request)

        return True


class GUI(QMainWindow):
    update_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_signal.connect(self.update_display)

        rclpy.init()
        self.node = GuiNode(self)
        self.thread_spin = threading.Thread(target=rclpy.spin, args=(self.node, ))
        self.thread_spin.start()

        #init
        self.setting_position = False

    def init_ui(self):
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        
        self.button1 = QPushButton(f"Move to 0.0, 0.0")
        self.button2 = QPushButton("Goal setting")

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)

        self.button1.clicked.connect(self.on_button_click_1)
        self.button2.clicked.connect(self.on_button_click_2)

        self.received_label = QLabel("Received Messages:")
        self.layout.addWidget(self.received_label)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.layout.addWidget(self.message_display)

    def on_button_click_1(self):
        self.node.navigate_to_pose_send_goal()

    def on_button_click_2(self):
        self.setting_position = True
        message = "[REQUEST] Publish point in Rviz "
        self.message_display.append(message)

    def change_button_name(self, name):
        self.button1.setText(f"{name}")

    def update_display(self, message):
        self.message_display.append(str(message))


def main():
    app = QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()