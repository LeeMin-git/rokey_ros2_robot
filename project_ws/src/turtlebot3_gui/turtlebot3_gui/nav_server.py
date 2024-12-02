# File: navigation_server.py
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from nav_interfaces.action import Navigate
import time

class NavigationServer(Node):
    def __init__(self):
        super().__init__('navigation_server')
        self._action_server = ActionServer(
            self,
            Navigate,
            'navigate',
            self.execute_callback)
        
        self.initial_location = 'home'
        self.current_location = self.initial_location
        self.get_logger().info('Navigation Server is ready')

    async def execute_callback(self, goal_handle):
        self.get_logger().info(f'Executing goal to location: {goal_handle.request.location}')
        
        # Initialize feedback and result
        feedback_msg = Navigate.Feedback()
        result = Navigate.Result()
        
        start_time = time.time()
        
        # Simulate moving to target location
        feedback_msg.current_state = 'MOVING_TO_TARGET'
        feedback_msg.current_location = self.current_location
        
        # Simulate movement time (3 seconds)
        for i in range(3):
            feedback_msg.time_elapsed = time.time() - start_time
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1.0)
        
        # Update current location
        self.current_location = goal_handle.request.location
        feedback_msg.current_location = self.current_location
        
        # Wait at target location
        feedback_msg.current_state = 'WAITING_AT_TARGET'
        wait_time = goal_handle.request.wait_time
        
        for _ in range(int(wait_time)):
            feedback_msg.time_elapsed = time.time() - start_time
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1.0)
        
        # Return to initial location
        feedback_msg.current_state = 'RETURNING_HOME'
        
        # Simulate return movement time (3 seconds)
        for i in range(3):
            feedback_msg.time_elapsed = time.time() - start_time
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1.0)
        
        # Update location to initial position
        self.current_location = self.initial_location
        
        # Set result
        total_time = time.time() - start_time
        result.success = True
        result.message = 'Successfully completed navigation task'
        result.final_location = self.current_location
        result.total_time = total_time
        
        goal_handle.succeed()
        return result
    
def main(args=None):
    rclpy.init(args=args)
    
    navigation_server = NavigationServer()
    
    try:
        rclpy.spin(navigation_server)
    except KeyboardInterrupt:
        pass
    finally:
        navigation_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()