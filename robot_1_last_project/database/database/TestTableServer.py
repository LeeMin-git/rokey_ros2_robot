import rclpy
from rclpy.node import Node
from table_order_interface.srv import SetOrder

class TableOrderServer(Node):
    def __init__(self):
        super().__init__('table_order_server')
        self.srv = self.create_service(SetOrder, 'SetOrder', self.handle_table_order)
        self.get_logger().info("Table Order Server Ready")

    def handle_table_order(self, request, response):
        # Print out the details of the received order
        self.get_logger().info(f"Received order for Table {request.table_number}:")
        self.get_logger().info(f"Menu: {request.menu}")
        self.get_logger().info(f"Quantity: {request.menu_number}")
        self.get_logger().info(f"Total Price: {request.price}")

        # Set the response success to True and send it back to the client
        response.success = True
        return response

def main():
    rclpy.init()
    node = TableOrderServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
