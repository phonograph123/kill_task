# kill_task

## 项目简介

`kill_task` 是一个基于 Python 的 Windows 进程黑名单拦截工具。
它可定时扫描系统进程，自动终止指定黑名单中的进程，支持进程名和完整路径匹配。
适用于屏蔽广告弹窗、恶意软件、办公环境下自动清理干扰进程等场景。

## 下载
[kill_task.exe](https://github.com/phonograph123/kill_task/releases/download/python/kill_task.zip)

## 功能特性

- 支持进程名和路径黑名单
- 自动定时扫描并终止黑名单进程
- 日志记录拦截和终止操作
- 支持自定义黑名单和检测间隔（config.json）
- 系统托盘图标，后台运行，右键菜单可退出
- 支持 PyInstaller 打包为单文件可执行程序

## 安装与运行

### 依赖环境

- Python 3.7 及以上
- 依赖库：psutil、pystray、Pillow

安装依赖：

```shell
pip install psutil pystray pillow
```

### 运行脚本

```shell
python kill_task.py
```

首次运行会自动生成 `config.json` 配置文件。

### 打包为可执行文件（可选）

需安装 [PyInstaller](https://www.pyinstaller.org/)：

```shell
pip install pyinstaller
pyinstaller -F -w --add-data "kill_icon.ico;." kill_task.py
```

打包后可直接运行 `dist/kill_task.exe`，系统托盘显示图标。

## 配置说明

- `config.json` 文件包含黑名单进程和检测间隔设置
- 黑名单支持进程名（如 `"msgcenter.exe"`）和完整路径（如 `"C:\\badprogram.exe"`）
- 检测间隔单位为秒

示例：

```json
{
  "blacklist": [
    "msgcenter.exe",
    "C:\\badprogram.exe"
  ],
  "check_interval": 10
}
```

## 使用方法

1. 编辑 `config.json`，添加需要拦截的进程名，设置检测间隔 check_interval
2. 运行脚本或打包后的程序
3. 程序会在后台自动拦截并终止黑名单进程
4. 系统托盘图标右键可退出程序
5. 拦截日志保存在 `process_blocker.log`

## 注意事项

- 需以管理员权限运行，才能终止部分高权限进程
- 黑名单进程名请使用小写，路径需为绝对路径
- 仅支持 Windows 系统

## 开源协议

MIT License
