# serverinfo
用于获取服务器信息并保存成表格形式
自动收集并监控服务器的CPU、内存、磁盘的使用情况，形成表格，发送到指定的一个目录。

## 1 基本信息

- 主机名 sys_name
- 内核名称 kernel_name
- 发行版本号 kernel_no
- 内核版本 kernel_version
- 系统架构 sys_framework

```python
import os

info = os.uname()

sys_name=info[1]
kernel_name=info[0]
kernel_no=info[2]
kernel_version=info[3]
sys_framework=info[4]
```

- 现在时间 now_time
- 开机时间 boot_time
- 运行时间 up_time

```python
import datetime

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
```

## 2 用psutil模块等获得服务器信息

psutil = process and system utilities，它不仅可以通过一两行代码实现系统监控，还可以跨平台使用，支持Linux／UNIX／OSX／Windows等，是系统管理员和运维小伙伴不可或缺的必备模块。

### 2.1 显示CPU的使用情况

#### CPU的使用率 cpu_percent

```python
cpu_percent = psutil.cpu_percent(interval=None, percpu=False) 
```

#### CPU用户使用率 cpu_time_percent.user 

#### CPU系统使用率 cpu_time_percent.system 

#### CPU空闲率 cpu_time_percent.idle 

#### CPUiowait cpu_time_percent.iowait

```python
cpu_time_percent = psutil.cpu_times_percent()
```

#### CPU的平均负载（1分钟，5分钟，15分钟）load_avg[0][1][2]

```python
load_avg = os.getloadavg()
```

#### 物理CPU核心数 physical_core_num

```python
physical_core_num = psutil.cpu_count(logical=False)
```

#### 逻辑CPU核心数 logical_core_num

```python
logical_core_num = psutil.cpu_count()
```

#### 正在运行频率 {{ (cpu_freq.current/1000)|round(2) }} GHz

#### 最低运行频率 {{ (cpu_freq.min/1000)|round(2) }} GHz

#### 最高运行频率 {{ (cpu_freq.max/1000)|round(2) }} GHz

```python
    try:
        cpu_freq = psutil.cpu_freq()
    except AttributeError:
        cpu_freq = None
```



### 2.2 显示内存的使用情况

#### 内存大小 context.total|format_size

#### 可用内存 context.available|format_size

#### 内存占用%  context.percent %

#### 已用内存 context.used|format_size

#### 空闲内存 context.free|format_size

#### 缓冲（buffers）  context.buffers|format_size

#### 缓存（cached）context.cached|format_size

#### 共享内存 context.shared|format_size

```python
def memory(part, chart=None):
    if part == 'memory':
        if chart in ['line', 'column']:
            return render_template('memory/memory-%s.html' % chart, part=part, chart=chart)
        context = psutil.virtual_memory()
    elif not chart and part == 'swap':
        context = psutil.swap_memory()
    else:
        return render_template('404.html'), 404

    return render_template('memory/%s.html' % part, context=context, part=part)
```

> ### cache
>
> 缓存（cached）是把读取过的数据保存起来，重新读取时若命中（找到需要的数据）就不要去读硬盘了，若没有命中就读硬盘。其中的数据会根据读取频率进行组织，把最频繁读取的内容放在最容易找到的位置，把不再读的内容不断往后排，直至从中删除。
> Cache并不是缓存文件的，而是缓存块的(块是I/O读写最小的单元)；Cache一般会用在I/O请求上，如果多个进程要访问某个文件，可以把此文件读入Cache中，这样下一个进程获取CPU控制权并访问此文件直接从Cache读取，提高系统性能。
> Cache 作用域在于 Cpu 与内存之间
>
> ### buffer
>
> 缓冲（buffers）是根据磁盘的读写设计的，把分散的写操作集中进行，减少磁盘碎片和硬盘的反复寻道，从而提高系统性能。当存储速度快的设备与存储速度慢的设备进行通信时，存储慢的数据先把数据存放到buffer，达到一定程度存储快的设备再读取buffer的数据，在此期间存储快的设备CPU可以干其他的事情。
> linux有一个守护进程定期清空缓冲内容（即写入磁盘），也可以通过sync命令手动清空缓冲。
> 修改/etc/sysctl.conf中的vm.swappiness右边的数字可以在下次开机时调节swap使用策略。该数字范围是0～100，数字越大越倾向于使用swap。默认为60，可以改一下试试。–两者都是RAM中的数据。



### 2.3 显示磁盘的使用情况

#### 设备 physical_disk_info['device']

#### 挂载点 physical_disk_info['mount_point']

#### 容量 physical_disk_info['space_total']|format_size

#### 已用 physical_disk_info['space_used']|format_size

#### 可用 physical_disk_info['space_free']|format_size

#### 已用% physical_disk_info['used_percent']  %

#### 类型 physical_disk_info['type']

```python
    if part == 'disk':
        context = []
        physical_disk_partitions = psutil.disk_partitions()
        for physical_disk_partition in physical_disk_partitions:
            physical_disk_usage = psutil.disk_usage(
                physical_disk_partition.mountpoint)
            physical_disk = {
                'device': physical_disk_partition.device,
                'mount_point': physical_disk_partition.mountpoint,
                'type': physical_disk_partition.fstype,
                'options': physical_disk_partition.opts,
                'space_total': physical_disk_usage.total,
                'space_used': physical_disk_usage.used,
                'used_percent': physical_disk_usage.percent,
                'space_free': physical_disk_usage.free
            }
            context.append(physical_disk)
```

