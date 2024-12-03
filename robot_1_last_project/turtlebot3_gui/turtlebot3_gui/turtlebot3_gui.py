import sys
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient, ActionServer
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from serving_robot_msgs.action import C2R

class ROS2Thread(QThread):
    log_signal = pyqtSignal(str)
    arrived_signal = pyqtSignal()  # Signal to indicate arrival at the table

    def __init__(self, x, y, node):
        super().__init__()
        self.x = x
        self.y = y
        self.node = node
        #self._action_client = ActionClient(self.node, NavigateToPose, '/navigate_to_pose')

    def run(self):
        # Wait for the action server to be ready
        #self._action_client.wait_for_server()
        self.log_signal.emit("Connected to navigation server.")

        # Send goal to target location
        self.node.send_goal(self.x, self.y)
        self.log_signal.emit(f"Navigating to target location: ({self.x}, {self.y})")

        # Simulate travel time
        #time.sleep(5)

        # Notify arrival at the target location
        self.arrived_signal.emit()
        self.log_signal.emit("i'm moving")

class SendGoal(Node):
    def __init__(self, positions, gui):
        super().__init__('send_goal_node')
        self.positions = positions  # Dictionary of table and kitchen positions
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.gui = gui  # GUI 객체를 저장
        self.table_number_clicked_signal = pyqtSignal(int)  #

        self.table_number_action_server = ActionServer (
            self,
            C2R,
            '/table_number',
            self.table_number_excute_callback
        )

        self.initial_pose = None
        self.set_initial_pose()  # Set initial pose to kitchen position

    
    def table_number_excute_callback(self, goal_handle):
        self.get_logger().info('Executing action, goal received.')
        table_num = goal_handle.request.table_num

        print(table_num)
        self.gui.table_number_clicked_signal.emit(table_num)  # GUI로 테이블 번호 전달

        #피드백메세지가 없기떄문에 주석
        #feedback_msg = C2R.Feedback()
        #feedback_msg.feedback = 'Processing goal'
        #goal_handle.publish_feedback(feedback_msg)

        result_msg = C2R.Result()
        result_msg.done = True

        goal_handle.succeed()
        self.get_logger().info(f'Action completed, result: {result_msg.done}')

        #받은 테이블 넘버에 해당하는 로봇 보내기

        return result_msg


    def set_initial_pose(self):
        self.initial_pose = PoseStamped()
        kitchen_position = self.positions['kitchen']
        self.initial_pose.pose.position.x = kitchen_position[0]
        self.initial_pose.pose.position.y = kitchen_position[1]
        self.initial_pose.pose.orientation.w = 1.0

    def send_goal(self, target_x, target_y):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = target_x
        goal_msg.pose.pose.position.y = target_y
        goal_msg.pose.pose.orientation.w = 1.0
        self.get_logger().info(f"Sending goal to ({target_x}, {target_y})")
        self._action_client.send_goal_async(goal_msg)

    def return_to_initial_pose(self):
        if self.initial_pose:
            kitchen_position = self.positions['kitchen']
            self.get_logger().info("Returning to the kitchen...")
            self.send_goal(kitchen_position[0], kitchen_position[1])
        else:
            self.get_logger().warn("Kitchen pose not set.")

class GUI(QWidget):
    table_number_clicked_signal = pyqtSignal(int)#테이블 번호 전달
    def __init__(self, ros_node):
        super().__init__()
        self.ros_node = ros_node
        self.setWindowTitle('TurtleBot3 Navigation with PyQt5')
        self.setGeometry(100, 100, 400, 500)
        self.layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

        # Table buttons layout
        button_layout = QHBoxLayout()
        for i in range(1, 10):
            button = QPushButton(f"Table {i}", self)
            button.clicked.connect(lambda _, i=i: self.on_table_button_click(i))
            button_layout.addWidget(button)
        self.layout.addLayout(button_layout)

        # Food pickup button (hidden by default)
        self.food_pickup_button = QPushButton("복귀", self)
        #self.food_pickup_button.setVisible(True)
        self.food_pickup_button.clicked.connect(self.on_food_pickup_button_click)
        self.layout.addWidget(self.food_pickup_button)

        self.setLayout(self.layout)
        self.ros_thread = None
        self.waiting_for_food_pickup = False  # Track if waiting for food pickup
        self.table_number_clicked_signal.connect(self.on_table_button_click)

    def on_table_button_click(self, table_number):
        if self.waiting_for_food_pickup:
            self.log("Waiting for food pickup to complete before moving to a new table.")
            return

        position = self.ros_node.positions.get(f'table{table_number}')
        if position:
            self.log(f"Navigating to Table {table_number} at {position}")
            # Create a thread to navigate to the selected table
            self.ros_thread = ROS2Thread(position[0], position[1], self.ros_node)
            self.ros_thread.log_signal.connect(self.log)
            self.ros_thread.arrived_signal.connect(self.on_arrival_at_table)
            self.ros_thread.start()

    def on_arrival_at_table(self):
        self.waiting_for_food_pickup = True
        #self.food_pickup_button.setVisible(True)  # Show the food pickup button

    def on_food_pickup_button_click(self):
        self.log("Returning to kitchen.")
        #self.food_pickup_button.setVisible(True)  # Hide the food pickup button
        self.waiting_for_food_pickup = False

        # Navigate back to the kitchen
        kitchen_position = self.ros_node.positions['kitchen']
        self.ros_thread = ROS2Thread(kitchen_position[0], kitchen_position[1], self.ros_node)
        self.ros_thread.log_signal.connect(self.log)
        self.ros_thread.start()

    def log(self, message):
        self.log_box.append(message)

class SpinThread(QThread):
    def __init__(self, ros_node):
        super().__init__()
        self.ros_node = ros_node

    def run(self):
        # Spin ROS 2 node in a separate thread to avoid blocking the GUI
        rclpy.spin(self.ros_node)

def main(args=None):
    rclpy.init(args=args)

    # Define positions for kitchen and 9 tables
    positions = {
        'kitchen': (0.0, 0.0),
        'table1': (3.15, 2.15),
        'table2': (3.1, 1.05),
        'table3': (3.14, 0.05),
        'table4': (2.0, 2.2),
        'table5': (2.0, 0.9),
        'table6': (2.0, -0.16),
        'table7': (0.9, 1.9),
        'table8': (0.85, 0.95),
        'table9': (0.94, -0.22)
    }

    # Create ROS 2 node
    #ros_node = SendGoal(positions)

    #spin_thread = SpinThread(ros_node)
    #spin_thread.start()

    # Set up the PyQt5 application
    #app = QApplication(sys.argv)
    #spin_thread = SpinThread(ros_node)
    #spin_thread.start()
    #gui = GUI(ros_node)
    #gui.show()

    '''
    app = QApplication(sys.argv)
    gui = GUI(None)
    ros_node = SendGoal(positions, gui) 
    spin_thread = SpinThread(ros_node)
    spin_thread.start()


    gui.show()
    '''
    '''
    ros_node = SendGoal(positions)
    spin_thread = SpinThread(ros_node)
    spin_thread.start()
    app = QApplication(sys.argv)
    gui = GUI(ros_node)
    gui.show()
    '''


    # Create the GUI
    app = QApplication(sys.argv)
    gui = GUI(None)  # Create GUI without SendGoal for now
    ros_node = SendGoal(positions, gui)  # Pass the GUI object to SendGoal

    # Set the GUI object in the SendGoal class
    gui.ros_node = ros_node  # Set the ros_node inside GUI to SendGoal

    spin_thread = SpinThread(ros_node)
    spin_thread.start()

    # Set up the PyQt5 application
    gui.show()
    

    # Start the PyQt5 event loop
    sys.exit(app.exec_())

    rclpy.shutdown()

if __name__ == '__main__':
    main()
