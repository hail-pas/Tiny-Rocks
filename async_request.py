# socket客户端 只需要封装请求，然后直接发送数据
# socket服务端的实现需要再封装HttpReponse,将接收到的数据传递到该类中处理
#       拆分数据 \r\n 请求头和请求体


import socket, select


class HttpResponse(object):
    def __init__(self, recv_data):
        self.recv_data = recv_data
        self.header_dict = {}
        self.body = None

    def initialize(self):
        headers, body = self.recv_data.split(b"\r\n\r\n", 1)
        header_list = headers.spplit(b"\r\n")
        for header in header_list:
            header = str(header, encoding="utf-8")
            temp = header.split(":", 1)
            if len(temp) == 2:
                self.header_dict[temp[0]] = temp[1]


class HttpRequest(object):
    def __init__(self, sk, host, callback):
        self.socket = sk
        self.host = host
        self.callback = callback

    def fileno(self):
        return self.socket.fileno()


class AsyncRequest(object):
    def __init__(self):
        # 计数器功能
        self.rconn = []
        self.wconn = []

    def add_request(self, host, callback):
        try:
            sk = socket.socket()
            sk.setblocking(False)  # 同步非阻塞式
            sk.connect((host, 80))
        except BlockingIOError as block_e:
            pass
        finally:
            cus_sk = HttpRequest(sk, host, callback)
            self.rconn.append(cus_sk)
            self.wconn.append(cus_sk)

    def run(self):
        while True:
            read, write, err = select.select(self.rconn, self.wconn, [], 2)
            for w in write:
                print(w.host, "连接成功！！")
                http_send_data = "GET / HTTP/1.0\r\nHost:%s\r\n\r\n" % w.host
                w.socket.send(bytes(http_send_data, encoding="utf-8"))
                self.wconn.remove(w)
            for r in read:
                print(r.host, "开始接收！！！")
                recv_data = bytes()
                while True:  # 确保数据接收完成
                    try:
                        recv_data += r.socket.recv(8096)
                    except Exception:
                        break

                print(r.host, recv_data)
                r.callback(recv_data)
                #### 服务端
                # response = HttpResponse(recv_data)
                # r.callback(response)
                # r.socket.close()
                ##########

                self.rconn.remove(r)
            if len(self.rconn) == 0:
                print("结束")
                break


def callback_fun1(*args):
    print(args[0])


def callback_fun2(*args):
    print(args[0])


item_list = [
    {"host": "www.baidu.com", "callback": callback_fun1},
    {"host": "www.163.com", "callback": callback_fun2},
    {"host": "www.cnblogs.com", "callback": callback_fun1}
]

a_req = AsyncRequest()
for item in item_list:
    a_req.add_request(item["host"], item["callback"])
a_req.run()
####### 同步 IO
# sk = socket.socket()
# sk.setblocking(False)  # 同步非阻塞式
# sk.connect(("www.baidu.com", 80))
# print("连接成功！！")
# sk.send(b"GET / HTTP/1.0\nHost:www.baidu.com\n\n")
# data = sk.recv(1024)
# print(data)
