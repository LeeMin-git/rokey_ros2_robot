# File: navigation_client.py
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav_interfaces.action import Navigate
from rclpy.callback_groups import ReentrantCallbackGroup
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        self.callback_group = ReentrantCallbackGroup()
        self._action_client = ActionClient(
            self,
            Navigate,
            'navigate',
            callback_group=self.callback_group)
        
        self.create_gui()
        
    def create_gui(self):
        self.window = tk.Tk()
        self.window.title("Navigation Action Client")
        self.window.geometry("400x500")
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Location input
        ttk.Label(main_frame, text="Target Location:").grid(row=0, column=0, pady=5)
        self.location_var = tk.StringVar(value="kitchen")
        locations = ['kitchen', 'bedroom', 'living_room', 'office']
        self.location_combo = ttk.Combobox(main_frame, textvariable=self.location_var,
                                         values=locations, state='readonly')
        self.location_combo.grid(row=0, column=1, pady=5)
        
        # Wait time input
        ttk.Label(main_frame, text="Wait Time (seconds):").grid(row=1, column=0, pady=5)
        self.wait_time = ttk.Entry(main_frame)
        self.wait_time.insert(0, "5")
        self.wait_time.grid(row=1, column=1, pady=5)
        
        # Send goal button
        self.send_button = ttk.Button(main_frame, text="Send Goal",
                                    command=self.send_goal)
        self.send_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready to send goal")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Feedback display
        ttk.Label(main_frame, text="Feedback:").grid(row=4, column=0, columnspan=2, pady=5)
        self.feedback_text = tk.Text(main_frame, height=10, width=40)
        self.feedback_text.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Clear button
        ttk.Button(main_frame, text="Clear Log",
                  command=lambda: self.feedback_text.delete(1.0, tk.END)).grid(
                      row=6, column=0, columnspan=2, pady=5)

    def send_goal(self):
        try:
            wait_time = float(self.wait_time.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for wait time")
            return
            
        goal_msg = Navigate.Goal()
        goal_msg.location = self.location_var.get()
        goal_msg.wait_time = wait_time
        
        self._action_client.wait_for_server()
        
        self.send_button.state(['disabled'])
        self.status_var.set("Sending goal...")
        
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.status_var.set("Goal rejected")
            self.send_button.state(['!disabled'])
            return

        self.status_var.set("Goal accepted")
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.status_var.set(f"Result: {result.message}")
        self.feedback_text.insert(tk.END, 
                                f"\nFinal Result:\n"
                                f"Success: {result.success}\n"
                                f"Final Location: {result.final_location}\n"
                                f"Total Time: {result.total_time:.1f}s\n"
                                f"{'='*40}\n")
        self.feedback_text.see(tk.END)
        self.send_button.state(['!disabled'])

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.feedback_text.insert(tk.END, 
                                f"State: {feedback.current_state}\n"
                                f"Location: {feedback.current_location}\n"
                                f"Time Elapsed: {feedback.time_elapsed:.1f}s\n"
                                f"-"*20 + "\n")
        self.feedback_text.see(tk.END)

    def run(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            self.window.update()

def main():
    rclpy.init()
    client = NavigationClient()
    
    try:
        client.run()
    except KeyboardInterrupt:
        pass
    finally:
        client.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()