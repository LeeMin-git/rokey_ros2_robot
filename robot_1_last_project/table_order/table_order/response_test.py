import rclpy
from rclpy.node import Node
from table_order_interface.srv import SetOrder

class OrderClient(Node):
    def __init__(self):
        super().__init__('order_client')
        # Create the client for the SetOrder service
        self.cli = self.create_client(SetOrder, 'SetOrder')
        # Wait for the service to be available
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

    def send_request(self, table_number, menu, menu_number, price):
        # Create the request message
        request = SetOrder.Request()
        request.table_number = table_number
        request.menu = menu
        request.menu_number = menu_number
        request.price = price

        # Call the service asynchronously
        future = self.cli.call_async(request)
        
        # Wait for the result to be available
        rclpy.spin_until_future_complete(self, future)
        
        # Check the result and log success or failure
        if future.result() is not None:
            self.get_logger().info(f'Service response: Success = {future.result().success}')
        else:
            self.get_logger().error('Service call failed')

def main(args=None):
    # Initialize the ROS 2 client library
    rclpy.init(args=args)

    try:
        # Create the client node and send a request
        order_client = OrderClient()

        # Example data to send in the request
        table_number = 5
        menu = ['Burger', 'Fries', 'Drink']
        menu_number = [2, 1, 3]  # quantities
        price = 35

        # Send the request to the service
        order_client.send_request(table_number, menu, menu_number, price)

    except Exception as e:
        # If any exception occurs, log it
        print(f"An error occurred: {e}")

    finally:
        # Shut down rclpy and clean up
        rclpy.shutdown()

if __name__ == '__main__':
    main()
