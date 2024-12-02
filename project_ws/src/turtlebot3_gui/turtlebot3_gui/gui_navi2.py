### thread 사용한 강사님 자료
import sys
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit

class ROS2Thread(QThread):
    # Define signals to communicate with the main GUI thread
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str)

    def __init__(self, x, y, node):
        super().__init__()
        self.x = x
        self.y = y
        self.node = node
        self._action_client = ActionClient(self.node, NavigateToPose, '/navigate_to_pose')

    def run(self):
        # Wait for the action server to be ready
        self._action_client.wait_for_server()
        self.log_signal.emit("Connected to navigation server.")

        # Send goal to target location
        self.node.send_goal(self.x, self.y)

        # Wait for 5 seconds
        self.log_signal.emit("Waiting for 5 seconds...")
        time.sleep(5)

        # Return to the initial location
        self.node.return_to_initial_pose()

        self.result_signal.emit("Mission complete!")

class SendGoal(Node):
    def __init__(self):
        super().__init__('send_goal_node')

        # Action client to communicate with the Navigation server
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

        # Initialize the initial pose (starting position)
        self.initial_pose = None
        self.set_initial_pose()

    def set_initial_pose(self):
        # Assume the robot starts at (0.0, 0.0) position
        self.initial_pose = PoseStamped()
        self.initial_pose.pose.position.x = 0.0
        self.initial_pose.pose.position.y = 0.0
        self.initial_pose.pose.orientation.w = 1.0

    def send_goal(self, target_x, target_y):
        # Create the goal message to send to the navigation server
        goal_msg = NavigateToPose.Goal()

        goal_msg.pose.header.frame_id = "map"  # Ensure the frame is "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = target_x
        goal_msg.pose.pose.position.y = target_y
        goal_msg.pose.pose.orientation.w = 1.0  # Assuming no rotation for simplicity

        self.get_logger().info(f"Sending goal to ({target_x}, {target_y})")

        # Send the goal asynchronously and wait for it to finish
        self._action_client.send_goal_async(goal_msg)

    def return_to_initial_pose(self):
        if self.initial_pose:
            self.get_logger().info("Returning to the initial pose...")
            self.send_goal(self.initial_pose.pose.position.x, self.initial_pose.pose.position.y)
        else:
            self.get_logger().warn("Initial pose not set.")

class GUI(QWidget):
    def __init__(self, ros_node):
        super().__init__()

        self.ros_node = ros_node

        # Set up the PyQt5 window
        self.setWindowTitle('TurtleBot3 Navigation with PyQt5')
        self.setGeometry(100, 100, 400, 300)

        # Set up layout and widgets
        self.layout = QVBoxLayout()

        self.x_input = QLineEdit(self)
        self.x_input.setPlaceholderText("Enter target X position (meters)")
        self.layout.addWidget(self.x_input)

        self.y_input = QLineEdit(self)
        self.y_input.setPlaceholderText("Enter target Y position (meters)")
        self.layout.addWidget(self.y_input)

        self.go_button = QPushButton("Go", self)
        self.go_button.clicked.connect(self.on_go_button_click)
        self.layout.addWidget(self.go_button)

        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

        self.setLayout(self.layout)

        # Set up the ROS 2 thread for communication
        self.ros_thread = None

    def on_go_button_click(self):
        # Get the input positions
        try:
            target_x = float(self.x_input.text())
            target_y = float(self.y_input.text())
        except ValueError:
            self.log("Invalid input. Please enter valid numbers for X and Y.")
            return

        # Create a thread for sending goal and handle results
        self.log(f"Sending goal to ({target_x}, {target_y})...")
        self.ros_thread = ROS2Thread(target_x, target_y, self.ros_node)
        self.ros_thread.log_signal.connect(self.log) #coneect to method()
        self.ros_thread.result_signal.connect(self.show_result) #coneect to method()
        self.ros_thread.start()

    def log(self, message):
        self.log_box.append(message)

    def show_result(self, message):
        self.log(message)

def main(args=None):
    rclpy.init(args=args)

    # Create ROS 2 node for navigation
    ros_node = SendGoal()

    # Set up the PyQt5 application
    app = QApplication(sys.argv)
    gui = GUI(ros_node)
    gui.show()

    # Start the PyQt5 event loop
    sys.exit(app.exec_())

    rclpy.shutdown()

if __name__ == '__main__':
    main()