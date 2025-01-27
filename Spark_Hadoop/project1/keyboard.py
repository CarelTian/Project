import time
from pynput import keyboard
from threading import Thread, Event

# 创建键盘控制器和事件
keyboard_controller = keyboard.Controller()
pause_event = Event()  # 用于暂停和恢复

# 初始状态为运行
pause_event.set()

# 按下空格键的循环逻辑
def press_space():
    while True:
        if pause_event.is_set():  # 检查是否处于运行状态
            keyboard_controller.press(' ')
            keyboard_controller.release(' ')
        time.sleep(   1)

# 键盘监听器的逻辑
def on_press(key):
    try:
        if key.char == 's':  # 检查用户是否输入了 's'
            if pause_event.is_set():
                pause_event.clear()  # 暂停
                print("已暂停")
            else:
                pause_event.set()  # 恢复
                print("已恢复")
    except AttributeError:
        pass  # 忽略特殊按键

# 主程序入口
if __name__ == "__main__":
    # 启动空格键循环的线程
    space_thread = Thread(target=press_space, daemon=True)
    space_thread.start()

    # 启动键盘监听器
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
