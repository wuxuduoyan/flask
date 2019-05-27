import re
import socket
import multiprocessing
from dynamic.my_web import application


class MyServer(object):
    """服务器"""

    def handler_client(self, client_socket):
        """5.处理客户端请求"""
        print('接收到客户端的的数据')
        request_data = client_socket.recv(1024).decode('utf-8')
        print(request_data)
        if not request_data:
            # 如果数据是空的 关闭client_socket
            client_socket.close()
            return

        request_lines = request_data.splitlines()
        # 打印每一行的数据
        for i, line in enumerate(request_lines):
            print(i, line)

        # GET /index.html HTTP / 1.1
        # 正则匹配 返回
        ret = re.match(r'([^/]*)([^ ]*)', request_lines[0])
        if ret:
            # print('正则匹配')
            # print(ret.group(0))
            # print(ret.group(1))
            # print(ret.group(2))
            file_name = ret.group(2)
            print(file_name)

            # 如果不写index.html 读取的依然是index.html
            if file_name == '/':
                file_name = '/index.html'

        if not file_name.endswith('html'):
            # 处理静态文件

            try:
                # "./html/index.html"
                # 读取文件内容 由于最后还要发送 直接用rb读取二进制
                with open(self.static_document_root + file_name, 'rb') as f:
                    # 读取文件全部的内容
                    content = f.read()
            except:
                response_body = '您的访问路径有错误,请修改后重新访问'
                # 文件读取异常  404
                response_header = 'HTTP/1.1 404 Not Found\r\n'

                # 添加编码 避免 浏览器 乱码
                response_header += "Content-Type:text/html; charset=utf-8\r\n"
                response_header += 'Content-Length:%s\r\n' % len(response_body.encode('utf-8'))

                response_header += '\r\n'  # 这里换行 为了 分开头信息和body信息

                # 给客户端返回数据
                # 头信息是字符串 需要转码 body不需要 所以分开发送
                client_socket.send((response_header + response_body).encode('utf-8'))
            else:
                response_body = content

                response_header = 'HTTP/1.1 200 OK\r\n'
                response_header += 'Content-Length:%s\r\n' % len(response_body)
                response_header += '\r\n'  # 这里换行 为了 分开头信息和body信息

                # 给客户端返回数据
                # 头信息是字符串 需要转码 body不需要 所以分开发送
                client_socket.send(response_header.encode('utf-8'))
                client_socket.send(response_body)
        else:
            # 处理动态的
            # 创建一个 空字典
            environ = dict()

            # 把请求的文件名 通过字典传给web框架  注意 key的名字要约定好
            environ['PATH_INFO'] = file_name

            # application是web应用框架的函数 返回的数据就是body数据
            response_body = self.application(environ, self.set_response_headers)

            # 用self.headers里的内容替换赋值
            response_header = 'HTTP/1.1 %s\r\n' % self.headers[0]
            for head in self.headers[1]:
                response_header += '%s:%s\r\n' % (head[0], head[1])

            response_header += '\r\n'  # 这里换行 为了 分开头信息和body信息

            # 给客户端返回数据
            # 头信息是字符串 需要转码 body不需要 所以分开发送
            client_socket.send(response_header.encode('utf-8'))
            client_socket.send(response_body.encode('utf-8'))

    def set_response_headers(self, status, headers):
        """用来获取头信息的函数"""
        # 把获取的头信息 保存为如下的格式 这里属性名叫self.headers
        # ['200 OK',[('Content-Type', 'text/html'), ('Connection', 'Keep-Alive')]]

        self.headers = [status, headers]

    def __init__(self, static_document_root, application):
        """程序入口"""
        self.static_document_root = static_document_root
        # web框架 获取数据的函数
        self.application = application

        # 1.创建tcp的套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置端口复用
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2 绑定端口
        self.server_socket.bind(("", 10000))

        # 3.设置被动监听
        self.server_socket.listen(128)

    def run_forever(self):
        """服务器运行"""
        while True:
            # 4.接收客户端请求
            # 返回客户端套接字对象和客户端的地址
            client_socket, client_addr = self.server_socket.accept()
            print('接收到客户端的连接')

            # 5.处理客户端请求  用进程 异步处理

            # 获取进程对象
            client_process = multiprocessing.Process(target=self.handler_client, args=(client_socket,))
            # 开启进程
            client_process.start()

            #  子进程会复制主进程所有的资源  包括client_socket 导致最后关闭是 只关闭了子进程的client_socket
            # 主进程的client_socket提前关闭
            client_socket.close()


def main():
    # 服务器静态文件的路径
    STATIC_DOCUMENT_ROOT = './static'

    # 服务器获取动态数据的框架路径
    DYNAMIC_DOCUMENT_ROOT = './dynamic'

    # python3 server.py my_web:application

    """入口  用来测试服务器"""
    myserver = MyServer(STATIC_DOCUMENT_ROOT, application)
    # 运行服务器
    myserver.run_forever()


if __name__ == '__main__':
    main()
