# @Time : 2022/6/3 19:28 
# @Author : kongsh
# @File : server.py
# websocket server端代码
# encoding=utf-8

import socket
import hashlib
import base64


def get_headers(data):
    """
    将请求头格式化成字典
    :param data:
    :return:
    """
    header_dict = {}
    data = str(data, encoding='utf-8')

    header, body = data.split('\r\n\r\n', 1)
    header_list = header.split('\r\n')
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[i].split(' ')) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[i].split(' ')
        else:
            k, v = header_list[i].split(':', 1)
            header_dict[k] = v.strip()
    return header_dict


def get_data(info):
    """
    按照websocket解密规则针对不同的数字进行不同的解密处理
    :param info:
    :return:
    """
    payload_len = info[1] & 127
    if payload_len == 126:
        extend_payload_len = info[2:4]
        mask = info[4:8]
        decoded = info[8:]
    elif payload_len == 127:
        extend_payload_len = info[2:10]
        mask = info[10:14]
        decoded = info[14:]
    else:
        extend_payload_len = None
        mask = info[2:6]
        decoded = info[6:]

    bytes_list = bytearray()
    for i in range(len(decoded)):
        chunk = decoded[i] ^ mask[i % 4]
        bytes_list.append(chunk)
    print(bytes_list)
    body = bytes_list.decode('utf-8', 'ignore')


    return body


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 防止mac/linux在重启时报端口被占用的错误
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", 8080))
sock.listen()

conn, addr = sock.accept()
# 获取客户端发送的消息
data = conn.recv(1024)

# 将一大堆请求头转换成字典数据  类似于wsgiref模块
header_dict = get_headers(data)
# 获取浏览器发送过来的随机字符串
client_random_str = header_dict['Sec-WebSocket-Key']
# 全球共用的随机字符串
magic_str = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
value = client_random_str + magic_str
cipher = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())

# 拼接好响应头
tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
      "Upgrade:websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "Sec-WebSocket-Accept: %s\r\n" \
      "WebSocket-Location: ws://127.0.0.1:8080\r\n\r\n"
response_str = tpl % cipher.decode('utf-8')
conn.send(bytes(response_str, encoding="utf-8"))

while 1:
    data = conn.recv(1024)
    value = get_data(data)
    print(value)
