[241109 토]
<241109_robot>
-> 버튼 옆에 테이블 번호 입력란 추가
-> 번호를 입력하지 않거나 숫자를 크게 하는 경우 경고 문구 발생
-> robot 코드와 연동하여 버튼 활성화 되는거 확인 완료

<241109_robot>
-> 주방(controller)에서 선택한 테이블 번호로 로봇을 이동하며 3초 대기후 다시 주방으로 이동함
+ topic으로 주방의 버튼 활성화

[241108 금]
<241108_robot>
-> ros2 action send_goal /table_num serving_robot_msgs/action/C2R "{table_num: 7}"를 보내면 GUI에 log와 테이블 넘버가 표시되며 로봇이 동작함

[241107 목]
<241107_robot_1>
-> robot이 이동할 table 번호와 log를 표시할 gui 생성

<241107_4>
-> 241107_3 + publish로 로봇 도착 상태 받았을때 버튼 활성화 완성
-> ros2 service call /test serving_robot_msgs/srv/T2C '{table_number: 12,menu: ['후','간','양'],menu_number: [1,2,3],price: 11110}'
*** topic으로 구현한 로봇 도착 신호를 다른 걸로 바꿔야함

<241107_3>
-> service로 데이터 받아오는거 action으로 테이블 번호 날려주는거 확인 완료

<241107_2>
-> 이 코드에서 코드 개발 시작

<241107_1>
-> 강사님께서 주신 자료(zip내부의 turtlebot3_point.py)를 토대로 service를 통해 받은 데이터를 gui에 표시하도록 구현
-------------------------------
[241106 수]
<service_test>
-> CLI에서 service call을 통해 날려준 정보를 CLI에 표시할 수 있는지 확인하는 코드

<241106>
-> GUI를 vscode에서 실행 할수 있도록 만든 코드

-> vscode에서 실행되는 코드는 ros2 run으로 실행이 안되고 ros2 run으로 실행이 가능한 코드는 vscode에서 실행이 안됨
