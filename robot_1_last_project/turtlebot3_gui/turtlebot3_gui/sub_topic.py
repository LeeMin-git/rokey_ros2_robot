#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime

class SubscriberGUI(Node):
    def __init__(self):
        super().__init__('subscriber_gui')
        self.subscription = self.create_subscription(
            String,
            'example_topic',
            self.listener_callback,
            10)
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("ROS2 Subscriber GUI")
        self.root.geometry("600x400")  # Set initial window size
        
        # Create and configure the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create status label
        self.status_var = tk.StringVar(value="Waiting for messages...")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, pady=(0, 5), sticky="w")
        
        # Create scrolled text widget for messages
        self.message_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=50,
            height=20
        )
        self.message_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create clear button
        self.clear_button = ttk.Button(
            self.main_frame,
            text="Clear Messages",
            command=self.clear_messages
        )
        self.clear_button.grid(row=2, column=0, pady=(5, 0))
        
        # Initialize message count
        self.message_count = 0
        
    def listener_callback(self, msg):
        # Get current timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Update message count
        self.message_count += 1
        
        # Create formatted message
        formatted_msg = f"[{timestamp}] Message {self.message_count}: {msg.data}\n"
        
        # Schedule the GUI update in the main thread
        self.root.after(0, self.update_display, formatted_msg)
        
        # Update status
        self.root.after(0, self.update_status)
        
        # Log to console
        self.get_logger().info(f'Received: "{msg.data}"')

    def update_display(self, message):
        # Enable text widget for editing
        self.message_display.configure(state='normal')
        
        # Insert new message at the end
        self.message_display.insert(tk.END, message)
        
        # Auto-scroll to the bottom
        self.message_display.see(tk.END)
        
        # Disable text widget for editing
        self.message_display.configure(state='disabled')

    def update_status(self):
        self.status_var.set(f"Received {self.message_count} messages")

    def clear_messages(self):
        # Enable text widget for editing
        self.message_display.configure(state='normal')
        
        # Clear all text
        self.message_display.delete(1.0, tk.END)
        
        # Disable text widget for editing
        self.message_display.configure(state='disabled')
        
        # Reset message count
        self.message_count = 0
        self.update_status()

    def run(self):
        # Create a separate thread for ROS2 spinning
        self.ros_thread = threading.Thread(target=self._spin_ros, daemon=True)
        self.ros_thread.start()
        
        # Start the Tkinter main loop
        self.root.mainloop()

    def _spin_ros(self):
        rclpy.spin(self)

def main(args=None):
    rclpy.init(args=args)
    node = SubscriberGUI()
    
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()