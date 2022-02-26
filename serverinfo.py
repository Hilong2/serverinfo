# designed by Hilong 2022/2/21
# 自动收集并监控服务器的CPU、内存、磁盘的使用情况，| 形成表格，发送到指定的一个目录。

import os
import datetime
import psutil
import csv
import time

class Serverinfo:

    # 获取服务器基本信息
    def info(self):
        # osinfo = os.uname()
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        boot_time_format = boot_time.strftime("%Y-%m-%d %H:%M:%S")
        now_time = datetime.datetime.now()
        now_time_format = now_time.strftime("%Y-%m-%d %H:%M:%S")
        up_time = "{} 天 {} 小时 {} 分钟 {} 秒".format(
            (now_time - boot_time).days,
            str(now_time - boot_time).split('.')[0].split(':')[0],
            str(now_time - boot_time).split('.')[0].split(':')[1],
            str(now_time - boot_time).split('.')[0].split(':')[2]
        )
        # 保存成字典形式
        info = {
            # 'sys_name': osinfo[1],
            # 'kernel_name': osinfo[0],
            # 'kernel_no': osinfo[2],
            # 'kernel_version': osinfo[3],
            # 'sys_framework': osinfo[4],
            # 'boot_time': boot_time_format,
            # 'now_time': now_time_format,
            # 'up_time': up_time,
            '当前时间': now_time_format
        }
        return info

    # 获取cpu的使用情况
    def cpu_info(self):
        cpu_percent = psutil.cpu_percent(interval=None, percpu=False)
        cpu_time_percent = psutil.cpu_times_percent()
        # load_avg = os.getloadavg()  # 平均负载
        physical_core_num = psutil.cpu_count(logical=False)
        logical_core_num = psutil.cpu_count()
        try:
            cpu_freq = psutil.cpu_freq()
        except AttributeError:
            cpu_freq = None
        cpu_info = {
            'CPU使用率%': cpu_percent,
            # '平均负载（1min）': load_avg[0],
            # 'cpu_percent': cpu_percent,
            # 'cpu_time_user': cpu_time_percent.user,
            # 'cpu_time_sys': cpu_time_percent.system,
            # 'cpu_time_idle': cpu_time_percent.idle,
            # 'cpu_time_iowait': cpu_time_percent.iowait,
            # 'load_avg1': load_avg[0],
            # 'load_avg5': load_avg[1],
            # 'load_avg15':load_avg[2],
            # 'physical_core_num': physical_core_num,
            # 'logical_core_num': logical_core_num,
            # 'cpu_freq_current': cpu_freq.current,
            # 'cpu_freq_min': cpu_freq.min,
            # 'cpu_freq_max': cpu_freq.max
        }
        return cpu_info

    # 获取内存的使用情况
    def memory_info(self):
        context = psutil.virtual_memory()
        memory = {
            '内存使用率%': context.percent,
            # 'memory_total': context.total,
            # 'memory_available': context.available,
            # 'memory_percent': context.percent,
            # 'memory_used': context.used,
            # 'memory_free': context.free,
            # 'memory_buffers': context.buffers,
            # 'memory_cached': context.cached,
            # 'memory_shared': context.shared
        }
        return memory

    # 获取磁盘的使用情况
    def disk_info(self):
        disks = []
        physical_disk_partitions = psutil.disk_partitions()

        for physical_disk_partition in physical_disk_partitions:
            physical_disk_usage = psutil.disk_usage(physical_disk_partition.mountpoint)
            physical_disk = {
                '磁盘%s使用率%%'% physical_disk_partition.device: physical_disk_usage.percent,
                # 'device': physical_disk_partition.device,
                # 'mount_point': physical_disk_partition.mountpoint,
                # 'type': physical_disk_partition.fstype,
                # 'options': physical_disk_partition.opts,
                # 'space_total': physical_disk_usage.total,
                # 'space_used': physical_disk_usage.used,
                # 'used_percent': physical_disk_usage.percent,
                # 'space_free': physical_disk_usage.free
            }
            disks.append(physical_disk)
        return disks


B_TO_G = 1073741824.0
B_TO_M = 1048576.0
B_TO_K = 1024.0
# 进制转换
def format_size(value):
    tmp = value / B_TO_G
    if tmp < 1.0:
        tmp = value / B_TO_M
        if tmp < 1.0:
            tmp = value / B_TO_K
            return "%s K" % round(tmp, 2)
        return "%s M" % round(tmp, 2)
    return "%s G" % round(tmp, 2)


# 合并字典
def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


# 获取全部信息并将字典组合
def getall():
    server = Serverinfo()
    info = server.info()
    cpu_info = server.cpu_info()
    memory = server.memory_info()
    disks = server.disk_info()

    disk = {}
    for dis in disks:
        disk = merge(disk, dis)

    abinfo = merge(info, cpu_info)
    cdinfo = merge(memory, disk)
    allinfo = merge(abinfo, cdinfo)

    print("已获取服务器信息")
    print(allinfo)
    # print(type(info))
    # print(list(info.keys()))

    return allinfo


def csv_writer(path, info):

    colname = []
    for headers in info.keys():  # 把字典的键取出来,注意不要使用sorted不然会导致键的顺序改变
        colname.append(headers)
    # print(colname)
    header = colname  # 提取列名列表

    # 第一次打开文件时，第一行写入表头
    if not os.path.exists(path):
        with open(path, "a", newline='', encoding='utf-8-sig') as csvfile:  # newline='' 去除空白行
            writer = csv.DictWriter(csvfile, fieldnames=header)  # 写字典的方法
            writer.writeheader()  # 写表头的方法
    # 写入内容 a表示以“追加”的形式写入，如果是“w”的话，表示在写入之前会清空原文件中的数据
    with open(path, "a", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writerow(info)  # 写入数据
        print("数据写入成功")



if __name__ == '__main__':
    while True:
        info = getall()
        path = 'serverInfo.csv'
        csv_writer(path, info)
        time.sleep(60)


'''
# 实例化SSHClient
ssh_client = paramiko.SSHClient()
# 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接 ，此方法必须放在connect方法的前面
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接SSH服务端，以用户名和密码进行认证 ，调用connect方法连接服务器
ssh_client.connect(hostname='ip', port=22, username='root', password='password')
# 打开一个Channel并执行命令  结果放到stdout中，如果有错误将放到stderr中
stdin, stdout, stderr = ssh_client.exec_command('df -hT ')
# stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
# df -hT :df 命令是 “Disk Free” 的首字母组合，它报告文件系统磁盘空间的使用情况。
# 打印执行结果
print(stdout.read().decode('utf-8'))
# 关闭SSHClient连接
ssh_client.close()
'''



