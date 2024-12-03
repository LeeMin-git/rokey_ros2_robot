import sys
import rclpy
from rclpy.node import Node
from PyQt5.QtWidgets import QFrame, QApplication, QWidget, QSpinBox, QPushButton, QVBoxLayout, QLabel,QHBoxLayout,QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from table_order_interface.srv import SetOrder
from serving_robot_msgs.srv import T2C
import threading #GUI와 ROS 이벤트 루트 동시 처리를 위해 추가

class tableOrderClient(Node):
    def __init__(self):
        #테이블 노드 초기화. 클라이언트로 생성하는 부분
        super().__init__('tableOrderClient')
        self.client = self.create_client(SetOrder, 'SetOrder')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('table order not available, waiting...')

    def sendTableOrderClient(self, tableNumber, menu, menuNumber,totalPrice):
        #테이블의 주문을 관제로 보내는 함수
        request = SetOrder.Request()
        request.table_number = tableNumber
        request.menu = list(menu)
        request.menu_number = list(menuNumber)
        request.price = totalPrice

        future = self.client.call_async(request)
        future.add_done_callback(self.callback)

    def callback(self, future):
        try:
            response = future.result()
            if response.succeed:
                print("Successfully sent to database")
            else:
                print("Failed to send database")
        except Exception as e:
            print(f"Service call failed: {e}")


    def callback(self, future):
        try:
            response = future.result()
            if response.success:
                print("Successfully sent to table order")
            else:
                print("Failed to send table order")
        except Exception as e:
            print(f"Service call failed : {e}")

    def exec_event_loop(self):
        while rclpy.ok():
            QApplication.processEvents()  # PyQt5 event processing
            rclpy.spin_once(self)  # Process ROS2 node events

class T2CClient(Node):
    def __init__(self):
        super().__init__('T2CClient')
        self.client = self.create_client(T2C, 'T2C')

    def sendTableInfo(self, tableNumber, menu, menuNumber, totalPrice):
        request = T2C.Request()
        request.table_number = tableNumber
        request.menu = menu
        request.menu_number = menuNumber
        request.price = totalPrice
        future = self.client.call_async(request)
        future.add_done_callback(self.callback)

    def callback(self, future):
        try:
            response = future.result()
            if response.succeed:
                print("Successfully sent to controller")
            else:
                print("Failed to send table info to controller")
        except Exception as e:
            print(f"Service call failed: {e}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.totalPriceInt = 0
        self.client = tableOrderClient()
        self.T2CClient = T2CClient()
        ########이미지 추가
        self.pixmap1 = QPixmap('/home/g1/rokey_c2_ws/src/table_order/resource/pride_chicken.jpeg')
        self.pixmap1 = self.pixmap1.scaled(200, 150, Qt.IgnoreAspectRatio)
        self.pixmap2 = QPixmap('/home/g1/rokey_c2_ws/src/table_order/resource/yangnum_chicken.jpeg')
        self.pixmap2 = self.pixmap2.scaled(200, 150, Qt.IgnoreAspectRatio)
        self.pixmap3 = QPixmap('/home/g1/rokey_c2_ws/src/table_order/resource/soi_chicken.jpeg')
        self.pixmap3 = self.pixmap3.scaled(200, 150, Qt.IgnoreAspectRatio)

        self.prideChickenImg = QLabel()
        self.prideChickenImg.setPixmap(self.pixmap1)
        self.sourcedChickenImg = QLabel()
        self.sourcedChickenImg.setPixmap(self.pixmap2)
        self.soiSourcedChickenImg = QLabel()
        self.soiSourcedChickenImg.setPixmap(self.pixmap3)
        ######이미지 추가
        self.setWindowTitle("테이블 오더")
        self.setGeometry(800, 400, 400, 300)

        self.layout = QVBoxLayout()

        self.tableLayout = QHBoxLayout()
        self.tableNumberLabel = QLabel("테이블 번호  ")
        self.tableLayout.addWidget(self.tableNumberLabel)
        self.tableNumberBox = QSpinBox(self)
        self.tableNumberBox.setMinimum(1)
        self.tableNumberBox.setMaximum(9)
        self.tableLayout.addWidget(self.tableNumberBox)
        self.tableNumberBox.valueChanged.connect(self.tableChanged)
        self.layout.addLayout(self.tableLayout)


        self.prideChickenLayout = QHBoxLayout()
        self.prideChickenLayout.addWidget(self.prideChickenImg) #이미지 추가
        self.prideChickenLabel = QLabel("후라이드 치킨 (20,000)")
        self.prideChickenLayout.addWidget(self.prideChickenLabel)
        self.prideChickenNumberBox = QSpinBox(self)
        self.prideChickenNumberBox.setMinimum(0)
        self.prideChickenLayout.addWidget(self.prideChickenNumberBox)
        self.prideChickenNumberBox.valueChanged.connect(self.orderChanged)
        self.layout.addLayout(self.prideChickenLayout)

        self.sourcedChickenLayout = QHBoxLayout()
        self.sourcedChickenLayout.addWidget(self.sourcedChickenImg) #이미지 추가
        self.sourcedChickenLabel = QLabel("양념 치킨 (21,000)")
        self.sourcedChickenLayout.addWidget(self.sourcedChickenLabel)
        self.sourcedChickenNumberBox = QSpinBox(self)
        self.sourcedChickenNumberBox.setMinimum(0)
        self.sourcedChickenNumberBox.valueChanged.connect(self.orderChanged)
        self.sourcedChickenLayout.addWidget(self.sourcedChickenNumberBox)
        self.layout.addLayout(self.sourcedChickenLayout)


        self.soiSourcedChickenLayout = QHBoxLayout()
        self.soiSourcedChickenLayout.addWidget(self.soiSourcedChickenImg) #이미지 추가
        self.soiSourcedChickenLabel = QLabel("간장 치킨 (21,000)")
        self.soiSourcedChickenLayout.addWidget(self.soiSourcedChickenLabel)
        self.soiSourcedChickenNumberBox = QSpinBox(self)
        self.soiSourcedChickenNumberBox.setMinimum(0)
        self.soiSourcedChickenNumberBox.valueChanged.connect(self.orderChanged)
        self.soiSourcedChickenLayout.addWidget(self.soiSourcedChickenNumberBox)
        self.layout.addLayout(self.soiSourcedChickenLayout)

        self.totalPriceLayout = QHBoxLayout()
        self.totalPriceLabel = QLabel("총 금액 ")
        self.totalPriceLayout.addWidget(self.totalPriceLabel)
        self.totalPrice = QLabel("")
        self.totalPrice.setNum(self.totalPriceInt)
        self.totalPriceLayout.addWidget(self.totalPrice)
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)  # You can choose other shapes like QFrame.Box
        frame.setFrameShadow(QFrame.Raised)  # Set shadow style for the frame (optional)

        frame.setLayout(self.totalPriceLayout)  # Set the totalPriceLayout as the layout for the frame

        # Add the frame to the main layout
        self.layout.addWidget(frame)
        self.layout.addLayout(self.totalPriceLayout)

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
        totalPrice = 20000 * self.prideChickenNumberBox.value() + 21000 * self.sourcedChickenNumberBox.value() +  21000 * self.soiSourcedChickenNumberBox.value() 
        self.totalPrice.setNum(totalPrice)
        self.totalPriceInt = totalPrice

    def tableChanged(self):#초기화 버튼에서도 사용하는 함수
        self.prideChickenNumberBox.setValue(0)
        self.sourcedChickenNumberBox.setValue(0)
        self.soiSourcedChickenNumberBox.setValue(0)

    def sendTableOrder(self):
        # 주문 버튼을 눌렀을때 호출되는 함수
        # DB로 리퀘스트하는 부분. 관제로 리퀘스트하는 부분.  두 파트.
        # 여기 수정하세요!!!!!!!!!!!!!
        ''' 
        서비스 인터페이스
        # Request
        # 날짜는 db에서 생성하여 입력
        int32 table_number # 테이블 번호
        string[] menu # 주문 메뉴
        int32[] menu_number # 주문한 메뉴의 갯수
        int32 price # 총 주문 가격
        ---
        # Response
        bool success
        '''
        if self.totalPriceInt > 0:
            tableNumber = self.tableNumberBox.value()#테이블 번호

            listOrderMenu = []#메뉴 리스트
            listOrderNumber = []#메뉴 갯수 리스트

            prideChickenNumber = self.prideChickenNumberBox.value()
            sourcedChickenNumber = self.sourcedChickenNumberBox.value()
            soiSourcedChickenNumber = self.soiSourcedChickenNumberBox.value()

            totalPrice = self.totalPriceInt#총 가격

            #리스트 생성
            if prideChickenNumber > 0:
                listOrderMenu.append('후라이드')
                listOrderNumber.append(prideChickenNumber)

            if sourcedChickenNumber > 0:
                listOrderMenu.append('양념')
                listOrderNumber.append(sourcedChickenNumber)

            if soiSourcedChickenNumber > 0:
                listOrderMenu.append('간장')
                listOrderNumber.append(soiSourcedChickenNumber)

            #보내는 값을 확인하는 print
            print(f"{tableNumber} / {listOrderMenu} / {listOrderNumber} / {totalPrice}")

            # DB에 값을 보내는 부분

            # 관제에 값을 보내는 부분
            #print(f"Seding table order : {tableNumber}, {prideChickenNumber}, {sourcedChickenNumber}, {soiSourcedChickenNumber}")
            self.client.sendTableOrderClient(tableNumber, listOrderMenu, listOrderNumber, totalPrice) #G1 server로 전송할 데이터 변경함
            self.T2CClient.sendTableInfo(tableNumber, listOrderMenu, listOrderNumber, totalPrice)  # Send to T2C
        else :
            msg = QMessageBox()
            msg.setWindowTitle("주문")
            msg.setText("주문 내역이 없습니다.")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.exec_()

    def exec_event_loop(self):
        while rclpy.ok():  # ROS2 이벤트 루프
            QApplication.processEvents()  # PyQt5 이벤트 처리
            rclpy.spin_once(self.client)  # ROS2 노드의 이벤트 처리
            rclpy.spin_once(self.T2CClient)


def main():
    rclpy.init()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #이벤트 루프 스래드 처리
    """
    ros_thread = threading.Thread(target=window.client.exec_event_loop)
    ros_thread.start()
    
    ros_thread2 = threading.Thread(target=window.T2CClient.exec_event_loop)
    ros_thread2.start()
    """
    ros_thread = threading.Thread(target=window.exec_event_loop)
    ros_thread.start()
    app.exec()
    rclpy.shutdown()

if __name__ == '__main__':
    main()