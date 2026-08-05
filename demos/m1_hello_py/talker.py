#!/usr/bin/env python3
# =============================================================================
# talker.py —— 我手写的第一个 ROS2 节点（发布者 / publisher）
# 里程碑：M1 · L3（从"用别人的节点"到"自己造节点"）
#
# 它干嘛：作为一个 ROS2 节点，每 1 秒往 /chatter 话题广播一条字符串消息。
# 怎么跑：
#   rosgo                        # 先激活 ros_humble 环境
#   python talker.py             # 启动本节点
#   # 另开一个终端验证它真在发：
#   ros2 topic echo /chatter     # 偷听 /chatter 的内容
#   ros2 node list               # 应能看到 /talker
#
# 一个节点最少要交代 4 件事（下面代码按这个骨架读）：
#   ① 报到   —— 告诉系统"我是个节点，我叫 talker"
#   ② 发布口 —— 声明"我要往哪个话题、发什么类型的消息"
#   ③ 干活   —— 定时造消息并发出去
#   ④ 转起来 —— 让节点持续存活、按节拍触发（spin）
# =============================================================================

import rclpy                        # ROS2 的 Python 客户端库（ROS Client Library for PYthon）
from rclpy.node import Node         # 节点基类：自己的节点都继承它
from std_msgs.msg import String     # 标准消息类型"字符串"。ROS2 消息是强类型的，发啥得先声明类型


class Talker(Node):                 # 造节点 = 写个类继承 Node（就像 iOS 里 class MyVC: UIViewController）
    def __init__(self):
        super().__init__("talker")  # ① 报到：节点名叫 "talker"，ros2 node list 里就是它

        self.count = 0              # 自己维护的一个计数器，用来给消息编号（Hello ROS2 0/1/2...）

        self.get_logger().info("Hello ROS2")  # ROS2 的日志打印（带时间戳+节点名，比 print 专业）

        # ② 发布口：往 "chatter" 话题发布 String 类型消息
        #    参数依次是：消息类型 / 话题名 / 队列长度(对方来不及收时最多缓存几条)
        #    注意：这行只是"接好水管"，还没发东西——真正发要靠下面的 .publish()
        self.publisher_ = self.create_publisher(String, "chatter", 10)

        # ④ 的一半：创建定时器，每 1.0 秒调用一次 self.publish_message
        #    这就是节点的"心跳"，让它周期性干活
        self.timer_ = self.create_timer(1.0, self.publish_message)

    def publish_message(self):                       # ③ 干活：每次定时器触发都执行这里
        msg = String()                               # 造一个空的 String 消息对象
        msg.data = "Hello ROS2 %d" % self.count      # 往消息里填内容（%d 是整数占位符，把 count 填进去）
        self.publisher_.publish(msg)                 # ★灵魂：真正把消息发到 /chatter，少了这行就是空转
        self.count += 1                              # 编号 +1，下条消息数字就涨了
        self.get_logger().info("Publishing: '%s'" % msg.data)  # 打印一下发了啥，方便肉眼观察


def main(args=None):
    rclpy.init(args=args)       # 启动 ROS2 运行时（一个进程用 ROS2 前必须先 init）
    talker = Talker()           # 造出我们的节点实例
    rclpy.spin(talker)          # ④ 转起来：阻塞在这里持续运行，让定时器不停触发，直到 Ctrl+C
    talker.destroy_node()       # 退出时销毁节点（收尾）
    rclpy.shutdown()            # 关闭 ROS2 运行时（收尾）


if __name__ == "__main__":      # 直接 python talker.py 运行时，才执行 main()
    main()
