import rclpy
from rclpy.node import Node
from mysql.connector import connect, Error
from table_order_interface.srv import SetOrder  # 추가된 서비스 임포트
from serving_robot_msgs.msg import TotalPrice2C
from datetime import datetime
import threading

class OrderSaver(Node):
    def __init__(self):
        super().__init__('order_saver')
        self.connection = self.create_connection()
        # 주문 서비스 설정
        self.srv = self.create_service(SetOrder, 'SetOrder', self.handle_order)
        self.publisher = self.create_publisher(TotalPrice2C,'total_price',10)
        # 총 매출 서비스 설정
        #self.sales_srv = self.create_service(GetTotalSales, 'get_total_sales', self.handle_get_total_sales)

    def create_connection(self):
        """MySQL 데이터베이스와 연결을 생성하는 메서드"""
        try:
            connection = connect(
                host='192.168.123.7',  # MySQL 서버 IP
                user='jwchoi0017',    # MySQL 사용자
                password='1234',      # MySQL 비밀번호
                database='orders_db'  # 데이터베이스 이름
            )
            if connection.is_connected():
                self.get_logger().info("MySQL 데이터베이스에 연결되었습니다.")
                return connection
        except Error as e:
            self.get_logger().error(f"연결 오류: {e}")
            return None

    def handle_order(self, request, response):
        """주문 요청을 처리하는 메서드"""
        table_number = request.table_number
        items = request.menu
        quantities = request.menu_number
        total_price = request.price

        self.get_logger().info(f"주문 접수됨: 테이블 {table_number}, 총 가격 {total_price}")
        self.get_logger().info(f"주문 항목: {list(zip(items, quantities))}")  # 메뉴 항목과 수량 출력
        threading.Thread(target=self.process_order, args=(table_number, items, quantities, total_price, response)).start()
        response.succeed =True
        return response

    def process_order(self, table_number, items, quantities, total_price, response):
        # 주문 정보를 DB에 저장
        
        order_id = self.save_order_to_db(table_number, total_price)
        if order_id:
            # 메뉴 항목과 수량을 DB에 저장
            for item, quantity in zip(items, quantities):
                # 가격은 각 항목의 가격 * 수량으로 처리해야 할 수 있습니다.
                self.save_item_to_db(order_id, item, quantity)  # 여기에 'total_price'를 항목 가격에 맞게 처리
            self.publish_total_price(datetime.now().strftime('%Y-%m-%d'))


    def save_order_to_db(self, table_number, total_price):
        """주문 정보를 MySQL 데이터베이스에 저장하는 메서드"""
        try:
            cursor = self.connection.cursor()
            # 1. orders 테이블에 주문 정보를 저장
            query = "INSERT INTO orders (table_number, total_price) VALUES (%s, %s)"
            cursor.execute(query, (table_number, total_price))  # total_price는 각 항목의 가격 합으로 설정
            self.connection.commit()

            # 2. 새로 저장된 주문의 ID 가져오기
            order_id = cursor.lastrowid
            #self.get_logger().info(f"주문이 저장되었습니다: {table_number}, 총 가격 {total_price}")
            return order_id
        except Error as e:
            self.get_logger().error(f"주문 저장 오류: {e}")
            return None
        finally:
            cursor.close()

    def save_item_to_db(self, order_id, menu_item, quantity):
        """주문 항목 정보를 MySQL 데이터베이스에 저장하는 메서드"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO order_items (order_id, menu_item, quantity) VALUES (%s, %s, %s)"
            cursor.execute(query, (order_id, menu_item, quantity))
            self.connection.commit()
            #self.get_logger().info(f"항목 저장됨: 주문 ID {order_id}, 메뉴 {menu_item}, 수량 {quantity}")
        except Error as e:
            self.get_logger().error(f"항목 저장 오류: {e}")
        finally:
            cursor.close()

    def publish_total_price(self, date):
        """Publish the order status to a topic"""
        total_sales = self.get_total_sales_from_db(date)
        msg = TotalPrice2C()
        msg.price = int(total_sales)
        self.publisher.publish(msg)
        self.get_logger().info(f"Published total sales for: {msg.price}")


    def get_total_sales_from_db(self, date):
        #특정 날짜의 총 매출을 MySQL에서 조회하는 메서드
        try:
            cursor = self.connection.cursor()
            query = "SELECT SUM(total_price) AS total_sales FROM orders WHERE DATE(order_time) = %s"
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0.0
        except Error as e:
            self.get_logger().error(f"총 매출 조회 오류: {e}")
            return 0.0
        finally:
            cursor.close()


def main(args=None):
    rclpy.init(args=args)
    order_saver = OrderSaver()
    rclpy.spin(order_saver)
    order_saver.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
