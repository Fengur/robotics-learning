# m1_hello_py —— 手写的第一对 ROS2 节点

> **里程碑 M1 · L3**：从"用别人写好的 demo 节点"跨到"自己造节点"。
> 这个 demo 里的 `talker.py`（发布者）和 `listener.py`（订阅者）**整条通信链路都是手写的**，不再借用任何现成 demo。

---

## 一、怎么跑

需要两个终端窗口（因为是两个独立进程）。每个窗口都先 `rosgo` 激活环境。

```bash
# 窗口 A —— 发布者
rosgo
cd ~/Desktop/XASDK/personal/learning/robotics/demos/m1_hello_py
python talker.py
# 每秒刷:  [talker]: Publishing: 'Hello ROS2 N'

# 窗口 B —— 订阅者
rosgo
cd ~/Desktop/XASDK/personal/learning/robotics/demos/m1_hello_py
python listener.py
# 每秒刷:  [listener]: I heard: 'Hello ROS2 N'   （序号和 A 对得上）
```

验证它们真在 ROS2 网络里活着：

```bash
ros2 node list            # 能看到 /talker 和 /listener
ros2 topic echo /chatter  # 不用 listener，直接偷听 talker 发的内容
```

停止：各窗口 `Ctrl+C`。

---

## 二、一个节点最少要交代 4 件事

不管发还是收，手写一个 ROS2 节点都绕不开这 4 件事。看代码时按这个骨架读：

| # | 件事 | talker（发布者） | listener（订阅者） |
|---|------|-----------------|-------------------|
| ① | **报到** | `super().__init__("talker")` | `super().__init__("listener")` |
| ② | **开口子** | 发布口 `create_publisher` | 订阅口 `create_subscription` |
| ③ | **干活** | 定时器**主动**每秒发 | 回调**被动**收到才触发 |
| ④ | **转起来** | `rclpy.spin()` 定时被唤醒 | `rclpy.spin()` 趴着等消息 |

**收发两端唯一必须一致的**：消息类型（都用 `String`）+ 话题名（都用 `chatter`）。对不上就通信不了。

---

## 三、talker（发布者）讲解

核心就三行（完整带注释源码见 [`talker.py`](https://github.com/Fengur/robotics-learning/blob/master/demos/m1_hello_py/talker.py)）：

```python
# ② 发布口：往 chatter 话题发 String，队列长度 10。这行只是"接好水管"，还没发东西
self.publisher_ = self.create_publisher(String, "chatter", 10)

# ④ 心跳：每 1.0 秒调一次 publish_message（定时器 = 节点主动干活的节拍）
self.timer_ = self.create_timer(1.0, self.publish_message)

# ③ 干活：造消息 → 发出去（.publish 是灵魂，少了它就是空转）→ 序号+1
def publish_message(self):
    msg = String()
    msg.data = "Hello ROS2 %d" % self.count
    self.publisher_.publish(msg)     # ★ 真正把消息发到 /chatter
    self.count += 1
```

**关键理解**：`create_publisher` 只是声明"我有个出水口"，真正发消息靠 `.publish(msg)`。少了这一行，节点会安静地每秒啥也不发。

---

## 四、listener（订阅者）讲解

和 talker 的区别全在②③（完整带注释源码见 [`listener.py`](https://github.com/Fengur/robotics-learning/blob/master/demos/m1_hello_py/listener.py)）：

```python
# ② 订阅口（对比 talker 的发布口）：类型/话题名要和 talker 对上，多一个"回调函数"
self.subscription_ = self.create_subscription(String, "chatter", self.callback, 10)

# ③ 回调：订阅方是被动的，消息一到 ROS2 自动调这个方法
def callback(self, msg):
    self.get_logger().info("I heard: '%s'" % msg.data)  # msg.data 取出内容
```

**关键理解**：talker 靠定时器**主动**发；listener 没有定时器，靠**回调被动**收——消息来了 ROS2 才唤醒你的 `callback`。同一个 `rclpy.spin()`，在 talker 是"定时被唤醒去发"，在 listener 是"趴着等消息来"。

---

## 五、和 iOS 经验的类比（帮理解）

这套"节点 + 话题 + 发布/订阅"，本质就是 iOS 的 **NotificationCenter**：

| ROS2 | iOS NotificationCenter |
|------|------------------------|
| 节点（进程）| 一个对象 |
| `create_publisher` + `.publish()` | `NotificationCenter.post(name:)` |
| `create_subscription(..., callback)` | `addObserver(..., selector:)` |
| 话题名 `chatter` | 通知名 `Notification.Name` |
| `rclpy.spin()` 保持存活 | 对象要被持有，别被释放 |

**最大的不同**：iOS 的 NotificationCenter 是**同一个进程内**对象在收发；ROS2 的 talker/listener 是**两个完全独立的进程**，甚至能跑在不同机器/不同板子上照样通信。这正是机器人能把"感知/规划/控制"拆到不同硬件还协同工作的根基（见 [`../../02-机器人系统构造.md`](../../02-机器人系统构造.md) 的分层架构）。

---

## 六、我学到了什么

- 会**造节点**了（不只是用）：报到 → 开口子 → 干活 → spin 的骨架
- 理解了发布方**主动**、订阅方**被动**的差别，以及两端类型/话题名必须对齐
- 踩过的坑：`self.publisher_.publish` 的**点**别漏（补全爱黏一起）、`%d` 占位符要先"挖坑"再填值

**下一步（M1 继续）**：话题之外的另两种通信——服务（service，一问一答）、动作（action，长任务带反馈）。
