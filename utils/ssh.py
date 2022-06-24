# @Time : 2022/6/4 19:19 
# @Author : kongsh
# @File : ssh.py
# paramiko模块的封装类


import paramiko


class SSHProxy(object):
    def __init__(self, hostname, port, username, password):
        """构造函数"""
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.transport = None

    def open(self):
        """
        给对象赋值一个上传下载文件对象连接
        :return:
        """
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.transport.connect(username=self.username, password=self.password)

    def command(self, cmd):
        """
        基于transport执行命令的连接,远程执行命令
        :param cmd:
        :return:
        """
        ssh = paramiko.SSHClient()
        # 允许链接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = self.transport

        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        err = stderr.read()
        return result, err

    def upload(self, local_path, remote_path):
        """上传文件"""
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        sftp.put(local_path, remote_path)
        sftp.close()

    def close(self):
        self.transport.close()

    def __enter__(self):
        """
        对象执行with上下文会自动触发,返回的时什么，with语法内的as后面拿到的就是什么
        :return:
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with执行结束自动触发
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        # print('触发了exit')
        self.close()


if __name__ == '__main__':
    with SSHProxy('192.168.1.9', 22, 'root', 'kongsh8778') as ssh:
        print(ssh.command('pwd'))