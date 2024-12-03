import os
import sys
import rclpy
from rclpy.node import Node
from PyQt5.QtWidgets import QFrame, QApplication, QWidget, QSpinBox, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from table_order_interface.srv import SetOrder
from serving_robot_msgs.srv import T2C
import threading  # GUI와 ROS 이벤트 루트 동시 처리를 위해 추가
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
class CombineClient(Node):
    def __init__(self):
        super().__init__('CombineClient')
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE, #ROS 2는 메시지가 지연되거나 재시도가 필요한 경우에도 메시지가 전달되도록 보장
            history=HistoryPolicy.KEEP_LAST, #가장 최근의 메시지만(depth만큼) 저장
            depth=10
        )
        self.client_set_order = self.create_client(SetOrder, 'SetOrder')
        self.client_t2c = self.create_client(T2C, 'T2C', qos_profile=qos_profile)

        while not self.client_set_order.wait_for_service(timeout_sec=1.0) and not self.client_t2c.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('database not available, waiting...')

    def sendTableOrderClient(self, tableNumber, menu, menuNumber, totalPrice):
        request = SetOrder.Request()
        request.table_number = tableNumber
        request.menu = list(menu)
        request.menu_number = list(menuNumber)
        request.price = totalPrice

        future = self.client_set_order.call_async(request)
        future.add_done_callback(self.callback_set_order)

    def callback_set_order(self, future):
        try:
            response = future.result()
            if response.succeed:
                print("Successfully sent to database")
            else:
                print("Failed to send database")
        except Exception as e:
            print(f"Service call failed: {e}")

#    def exec_event_loop(self):
#        while rclpy.ok():
#            #QApplication.processEvents()  # PyQt5 event processing
#            rclpy.spin_once(self)  # Process ROS2 node events

    def sendTableInfo(self, tableNumber, menu, menuNumber, totalPrice):
        request = T2C.Request()
        request.table_number = tableNumber
        request.menu = menu
        request.menu_number = menuNumber
        request.price = totalPrice
        future = self.client_t2c.call_async(request)
        future.add_done_callback(self.callback_t2c)

    def callback_t2c(self, future):
        try:
            response = future.result()
            print(f"Response from controller: {response.succeed}")
            if response.succeed:
                print("Successfully sent to controller")
            else:
                print("Failed to send table info to controller")
        except Exception as e:
            print(f"Service call failed: {e}")

    def exec_event_loop(self):
        while rclpy.ok():
            #QApplication.processEvents()  # PyQt5 event processing
            rclpy.spin_once(self)  # Process ROS2 node events


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.totalPriceInt = 0
        self.TotalPriceForRequest = {}
        self.client = CombineClient()

        # 이미지 추가
        resource_dir = os.path.join(os.getenv('HOME'), 'rokey_c_2_ws', 'src', 'table_order', 'resource')
        self.pixmap1 = QPixmap(os.path.join(resource_dir, 'pride_chicken.jpeg'))
        self.pixmap1 = self.pixmap1.scaled(200, 150, Qt.IgnoreAspectRatio)
        self.pixmap2 = QPixmap(os.path.join(resource_dir, 'yangnum_chicken.jpeg'))
        self.pixmap2 = self.pixmap2.scaled(200, 150, Qt.IgnoreAspectRatio)
        self.pixmap3 = QPixmap(os.path.join(resource_dir, 'soi_chicken.jpeg'))
        self.pixmap3 = self.pixmap3.scaled(200, 150, Qt.IgnoreAspectRatio)

        self.prideChickenImg = QLabel()
        self.prideChickenImg.setPixmap(self.pixmap1)
        self.sourcedChickenImg = QLabel()
        self.sourcedChickenImg.setPixmap(self.pixmap2)
        self.soiSourcedChickenImg = QLabel()
        self.soiSourcedChickenImg.setPixmap(self.pixmap3)

        self.setWindowTitle("테이블 오더")
        self.setGeometry(800, 400, 400, 300)

        self.layout = QVBoxLayout()

        # Table number input
        self.tableLayout = QHBoxLayout()
        self.tableNumberLabel = QLabel("테이블 번호  ")
        self.tableLayout.addWidget(self.tableNumberLabel)
        self.tableNumberBox = QSpinBox(self)
        self.tableNumberBox.setMinimum(1)
        self.tableNumberBox.setMaximum(9)
        self.tableLayout.addWidget(self.tableNumberBox)
        self.tableNumberBox.valueChanged.connect(self.tableChanged)
        self.layout.addLayout(self.tableLayout)

        # Chicken menu inputs
        self.prideChickenLayout = QHBoxLayout()
        self.prideChickenLayout.addWidget(self.prideChickenImg)
        self.prideChickenLabel = QLabel("후라이드 치킨 (20,000)")
        self.prideChickenLayout.addWidget(self.prideChickenLabel)
        self.prideChickenNumberBox = QSpinBox(self)
        self.prideChickenNumberBox.setMinimum(0)
        self.prideChickenLayout.addWidget(self.prideChickenNumberBox)
        self.prideChickenNumberBox.valueChanged.connect(self.orderChanged)
        self.layout.addLayout(self.prideChickenLayout)

        self.sourcedChickenLayout = QHBoxLayout()
        self.sourcedChickenLayout.addWidget(self.sourcedChickenImg)
        self.sourcedChickenLabel = QLabel("양념 치킨 (21,000)")
        self.sourcedChickenLayout.addWidget(self.sourcedChickenLabel)
        self.sourcedChickenNumberBox = QSpinBox(self)
        self.sourcedChickenNumberBox.setMinimum(0)
        self.sourcedChickenNumberBox.valueChanged.connect(self.orderChanged)
        self.sourcedChickenLayout.addWidget(self.sourcedChickenNumberBox)
        self.layout.addLayout(self.sourcedChickenLayout)

        self.soiSourcedChickenLayout = QHBoxLayout()
        self.soiSourcedChickenLayout.addWidget(self.soiSourcedChickenImg)
        self.soiSourcedChickenLabel = QLabel("간장 치킨 (21,000)")
        self.soiSourcedChickenLayout.addWidget(self.soiSourcedChickenLabel)
        self.soiSourcedChickenNumberBox = QSpinBox(self)
        self.soiSourcedChickenNumberBox.setMinimum(0)
        self.soiSourcedChickenNumberBox.valueChanged.connect(self.orderChanged)
        self.soiSourcedChickenLayout.addWidget(self.soiSourcedChickenNumberBox)
        self.layout.addLayout(self.soiSourcedChickenLayout)

        # Total price display
        self.totalPriceLayout = QHBoxLayout()
        self.totalPriceLabel = QLabel("총 금액 ")
        self.totalPriceLayout.addWidget(self.totalPriceLabel)
        self.totalPrice = QLabel("")
        self.totalPrice.setNum(self.totalPriceInt)
        self.totalPriceLayout.addWidget(self.totalPrice)

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLayout(self.totalPriceLayout)  # Add layout to frame
        self.layout.addWidget(frame)

        # Bottom button layout
        self.bottomLayout = QHBoxLayout()
        self.initButton = QPushButton("초기화", self)
        self.initButton.setFixedWidth(130)
        self.initButton.clicked.connect(self.tableChanged)
        self.orderButton = QPushButton("주문", self)
        self.orderButton.setFixedWidth(130)
        self.orderButton.clicked.connect(self.sendTableOrder)
        self.bottomLayout.addWidget(self.initButton)
        self.bottomLayout.addWidget(self.orderButton)
        self.layout.addLayout(self.bottomLayout)

        self.setLayout(self.layout)

    def orderChanged(self):
        totalPrice = 20000 * self.prideChickenNumberBox.value() + 21000 * self.sourcedChickenNumberBox.value() + 21000 * self.soiSourcedChickenNumberBox.value()
        self.totalPrice.setNum(totalPrice)
        self.totalPriceInt = totalPrice

    def tableChanged(self):
        self.prideChickenNumberBox.setValue(0)
        self.sourcedChickenNumberBox.setValue(0)
        self.soiSourcedChickenNumberBox.setValue(0)

    def sendTableOrder(self):
        if self.totalPriceInt > 0:
            tableNumber = self.tableNumberBox.value()
            listOrderMenu = []
            listOrderNumber = []

            prideChickenNumber = self.prideChickenNumberBox.value()
            sourcedChickenNumber = self.sourcedChickenNumberBox.value()
            soiSourcedChickenNumber = self.soiSourcedChickenNumberBox.value()

            if tableNumber not in self.TotalPriceForRequest:
                self.TotalPriceForRequest[tableNumber] = 0

            # Add the current total price to the table number's existing value
            self.TotalPriceForRequest[tableNumber] += self.totalPriceInt
            totalPrice = self.totalPriceInt #메뉴판 GUI에 현재 담은 장바구니의 총 가격 저장
            print(self.TotalPriceForRequest)
            if prideChickenNumber > 0:
                listOrderMenu.append('후라이드')
                listOrderNumber.append(prideChickenNumber)

            if sourcedChickenNumber > 0:
                listOrderMenu.append('양념')
                listOrderNumber.append(sourcedChickenNumber)

            if soiSourcedChickenNumber > 0:
                listOrderMenu.append('간장')
                listOrderNumber.append(soiSourcedChickenNumber)

            print(f"{tableNumber} / {listOrderMenu} / {listOrderNumber} / {totalPrice}")

            self.client.sendTableOrderClient(tableNumber, listOrderMenu, listOrderNumber, totalPrice) #DB로 데이터 전송하는 친구
            self.client.sendTableInfo(tableNumber, listOrderMenu, listOrderNumber, self.TotalPriceForRequest[tableNumber]) #관제로 데이터 보내는 친구
        else:
            QMessageBox.warning(self, "주문 오류", "주문 금액이 0원입니다. 메뉴를 추가해주세요.")

    def closeEvent(self, event):
        rclpy.shutdown()
        event.accept()


def main():
    rclpy.init()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    ros_thread1 = threading.Thread(target=window.client.exec_event_loop)
    ros_thread1.start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
