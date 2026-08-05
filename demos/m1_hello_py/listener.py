#!/usr/bin/env python3
# =============================================================================
# listener.py —— 我手写的第二个 ROS2 节点（订阅者 / subscriber）
# 里程碑：M1 · L3（自己造节点，这次是"收"的一端）
#
# 它干嘛：作为一个 ROS2 节点，订阅 /chatter 话题，每收到一条消息就打印出来。
# 怎么跑：
#   rosgo                        # 先激活 ros_humble 环境
#   python listener.py           # 启动本节点（趴着等消息）
#   # 另开一个终端跑发布者，它俩就对上话了：
#   python talker.py
#
# 和 talker 对照记（同样是 4 件事，但②③不同）：
#   ① 报到   —— 一样，告诉系统"我叫 listener"
#   ② 订阅口 —— talker 是"发布口 create_publisher"，这里是"订阅口 create_subscription"
#   ③ 回调   —— talker 是"定时器主动发"，这里是"消息来了被动触发回调"（不用定时器）
#   ④ 转起来 —— 一样用 spin，但含义变成"趴着等消息"而非"定时被唤醒"
# =============================================================================

import rclpy                        # ROS2 的 Python 客户端库
from rclpy.node import Node         # 节点基类
from std_msgs.msg import String     # 消息类型：必须和 talker 发的类型一致，否则收不到


class Listener(Node):               # 造节点 = 继承 Node（和 talker 同款套路）
    def __init__(self):
        super().__init__("listener")            # ① 报到：节点名 "listener"

        self.get_logger().info("Hello ROS2")    # 启动日志

        # ② 订阅口（对比 talker 的 create_publisher）：
        #    参数依次是：消息类型 / 话题名 / 回调函数 / 队列长度
        #    - String、"chatter" 必须和 talker 那边完全对上，否则收不到
        #    - self.callback 是关键：订阅方是"被动"的，消息一到 ROS2 就自动调它
        #      （就像 iOS 里 addObserver 注册一个回调，通知来了系统帮你调）
        self.subscription_ = self.create_subscription(String, "chatter", self.callback, 10)

    def callback(self, msg):                     # ③ 回调：每收到一条 /chatter 的消息就进这里
        # msg 就是收到的消息对象，msg.data 取出里面的字符串内容
        self.get_logger().info("I heard: '%s'" % msg.data)


def main(args=None):
    rclpy.init(args=args)           # 启动 ROS2 运行时
    listener = Listener()           # 造出 listener 节点
    rclpy.spin(listener)            # ④ 转起来：阻塞在此持续运行，趴着等消息，收到就触发 callback，直到 Ctrl+C
    listener.destroy_node()         # 退出时销毁节点（收尾）
    rclpy.shutdown()                # 关闭 ROS2 运行时（收尾）


if __name__ == "__main__":          # 直接 python listener.py 运行时才执行 main()
    main()
