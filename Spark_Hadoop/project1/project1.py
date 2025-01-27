import subprocess
import sys
import threading

# 用于读取子进程输出的函数
def read_output(process):
    while True:
        output = process.stdout.readline()  # 从子进程的标准输出读取一行
        if output == '' and process.poll() is not None:
            break  # 如果子进程结束且没有更多输出，退出循环
        if output:
            sys.stdout.write(output)  # 直接输出到屏幕
            sys.stdout.flush()  # 刷新输出

# 用于向子进程输入的函数
def write_input(process):
    while True:
        user_input = input()  # 获取用户输入
        if user_input.lower() == 'exit':
            process.terminate()  # 输入 'exit' 时终止子进程
            break
        process.stdin.write(user_input + '\n')  # 直接写入字符串
        process.stdin.flush()  # 刷新输入缓冲区

def main():
    # 启动一个 bash 或 zsh 进程
    process = subprocess.Popen(
        ['/bin/bash'],  # 你也可以换成 '/bin/zsh' 或其他 shell
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # 将输入输出作为字符串处理
    )

    # 启动两个线程：一个用于读取子进程的输出，另一个用于获取用户输入
    output_thread = threading.Thread(target=read_output, args=(process,))
    input_thread = threading.Thread(target=write_input, args=(process,))

    output_thread.start()
    input_thread.start()

    # 等待线程完成
    input_thread.join()
    output_thread.join()

    process.wait()  # 等待子进程结束

if __name__ == '__main__':
    main()
