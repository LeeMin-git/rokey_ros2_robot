#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from threading import Thread

class NavigationGUI(Node):
    def __init__(self):
        super().__init__('navigation_gui')
        
        # Create the action client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Navigation Control")
        self.root.geometry("300x200")
        
        # Create and pack buttons
        self.goal0_button = ttk.Button(
            self.root, 
            text="Send Goal 0",
            command=self.send_goal0
        )
        self.goal0_button.pack(pady=20)

        self.goal1_button = ttk.Button(
            self.root, 
            text="Send Goal 1",
            command=self.send_goal1
        )
        self.goal1_button.pack(pady=20)
        
        self.goal2_button = ttk.Button(
            self.root, 
            text="Send Goal 2",
            command=self.send_goal2
        )
        self.goal2_button.pack(pady=20)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Status: Ready")
        self.status_label.pack(pady=20)
        
        # Wait for the action server
        self.nav_client.wait_for_server()

    def send_goal0(self):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        
        # Set position for goal 0
        goal.pose.pose.position.x = 0.0
        goal.pose.pose.position.y = 0.0
        goal.pose.pose.orientation.w = 1.0
        
        self.send_goal(goal, "Goal 0")

    def send_goal1(self):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        
        # Set position for goal 1
        goal.pose.pose.position.x = 1.0
        goal.pose.pose.position.y = 1.0
        goal.pose.pose.orientation.w = 1.0
        
        self.send_goal(goal, "Goal 1")
        
    def send_goal2(self):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        
        # Set position for goal 2
        goal.pose.pose.position.x = 2.0
        goal.pose.pose.position.y = 0.0
        goal.pose.pose.orientation.w = 1.0
        
        self.send_goal(goal, "Goal 2")
        
    def send_goal(self, goal, goal_name):
        self.status_label.config(text=f"Status: Sending {goal_name}")
        
        # Send the goal
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(
            lambda f: self.goal_response_callback(f, goal_name))
        
    def goal_response_callback(self, future, goal_name):
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.status_label.config(
                text=f"Status: {goal_name} rejected")
            return
            
        self.status_label.config(
            text=f"Status: {goal_name} accepted")
            
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda f: self.get_result_callback(f, goal_name))
            
    def get_result_callback(self, future, goal_name):
        result = future.result().result
        self.status_label.config(
            text=f"Status: {goal_name} completed")
            
    def run(self):
        # Create a separate thread for the ROS2 spinner
        spinner_thread = Thread(target=self.ros_spin)
        spinner_thread.daemon = True
        spinner_thread.start()
        
        # Start the Tkinter main loop
        self.root.mainloop()
        
    def ros_spin(self):
        rclpy.spin(self)

def main():
    rclpy.init()
    nav_gui = NavigationGUI()
    nav_gui.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()