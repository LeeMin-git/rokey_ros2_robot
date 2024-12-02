import rclpy
from serving_robot_msgs.action import C2R
from serving_robot_msgs.msg import RobotState
from rclpy.node import Node
from rclpy.action import ActionServer
from nav2_msgs.action import NavigateToPose

class Action_test(Node):
    def __init__(self):
        super().__init__('action_test')
        self.action_server=ActionServer(self,C2R,'/table_num',self.callback)
        # self.test = ActionServer(self,NavigateToPose,"/navigate_to_pose",self.test)
        self.robot_state=self.create_publisher(RobotState,'/state',10)

    def callback(self,goal_handle):
        a=goal_handle.request.table_num
        self.get_logger().info(str(a))
        goal_handle.succeed()
        result = C2R.Result()
        result.done = True
        a=RobotState()
        a.state=result.done
        # self.robot_state.publish(a)
        return result
    
    def test(self,handle):
        self.get_logger().info(str(handle.request.pose.pose.postion.x))
        return True
    
def main():
    rclpy.init()
    node=Action_test()
    rclpy.spin(node)
    node.action_server.destroy()
    node.destroy_node()
    rclpy.shutdown()

    
if __name__=='__main__':
    main()
