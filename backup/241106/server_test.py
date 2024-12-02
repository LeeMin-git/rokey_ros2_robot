### 서비스 서버 테스트 코드 
### ros2 service call /test serving_robot_msgs/srv/T2C "{table_number: 12, menu: ['aaa','bbb'],menu_number: [1],price: 111}"
import rclpy
from rclpy.node import Node
from serving_robot_msgs.srv import T2C
'''
int32 table_number
string[] menu
int32[] menu_number
int32 price
'''
class Test(Node):
    def __init__(self):
        super().__init__('service_ser_test')
        self.ser_server=self.create_service(T2C,'/test',self.callback)
    
    def callback(self,request,response):
        self.a=request.table_number
        self.b=request.menu
        self.c=request.menu_number
        self.d=request.price
        response.succeed = True
        self.get_logger().info(self.b[0])
        self.get_logger().info(self.b[1])
        # self.get_logger().info(str(*self.b))
        # self.get_logger().info(str(self.a)+'\n'+str(*self.b)+'\n'+str(*self.c)+'\n'+str(self.d))
        return response
    
def main():
    rclpy.init()
    ttt=Test()
    rclpy.spin(ttt)
    ttt.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    



        