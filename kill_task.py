import psutil
import time
import logging
from datetime import datetime
import threading
import pystray
from PIL import Image, ImageDraw
import subprocess

# 配置日志（记录拦截记录）
logging.basicConfig(
    filename='process_blocker.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



class ProcessBlocker:
    def __init__(self, blacklist, check_interval=5):
        """
        初始化进程拦截器
        :param blacklist: 进程黑名单（可包含进程名或路径）
        :param check_interval: 检测间隔（秒）
        """
        self.blacklist = [name.lower() for name in blacklist]  # 统一转为小写，忽略大小写
        self.check_interval = check_interval
        print(f"进程黑名单工具启动，监控间隔：{check_interval}秒")
        print(f"黑名单进程：{self.blacklist}")

    def is_blocked(self, process):
        """判断进程是否在黑名单中"""
        try:
            process_name = process.name().lower()
            if process_name in self.blacklist:
                return True, process_name
            process_path = process.exe().lower()
            for blocked in self.blacklist:
                if blocked in process_path:
                    return True, process_path
            return False, None
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False, None

    def kill_process(self, process):
        """终止进程"""
        try:
            process.kill()
            time.sleep(1)
            if process.is_running():
                # 尝试用 taskkill 强制终止
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(process.pid)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(1)
                    return not process.is_running()
                except Exception as e:
                    return False
            return True
        except psutil.NoSuchProcess:
            return True
        except psutil.AccessDenied:
            # 权限不足时也尝试 taskkill
            try:
                subprocess.run(['taskkill', '/F', '/PID', str(process.pid)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)
                return not process.is_running()
            except Exception as e:
                return False

    def start_monitoring(self):
        try:
            while True:
                for proc in psutil.process_iter(['name', 'exe']):
                    is_blocked, target = self.is_blocked(proc)
                    if is_blocked:
                        success = self.kill_process(proc)
                        msg = f"检测到黑名单进程：{target}，PID：{proc.pid}，{'已成功终止' if success else '终止失败（可能无权限）'}"
                        print(msg)
                        logging.info(msg)
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n工具已手动停止")

# 系统托盘相关
def create_image():
    # 加载自定义图标
    import os, sys
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, 'kill_icon.ico')
    else:
        icon_path = os.path.join(os.path.dirname(__file__), 'kill_icon.ico')
    return Image.open(icon_path)

def on_quit(icon, item):
    icon.stop()
    import os
    os._exit(0)

def run_tray():
    icon = pystray.Icon("ProcessBlocker")
    icon.icon = create_image()
    icon.title = "进程黑名单工具"
    icon.menu = pystray.Menu(
        pystray.MenuItem("退出", on_quit)
    )
    icon.run()

if __name__ == "__main__":
    import json
    import os

    CONFIG_PATH = 'config.json'
    DEFAULT_CONFIG = {
        "blacklist": [
            "msgcenter.exe",
            "QQPYUserCenter.exe",
            "GetWordSearch.exe",
            "360AICenter.exe",
            "NewsReader.exe",
            "GameChrome.exe",
            "BookingAssistant.exe",
            "360DayPop.exe",
            "360AI办公-AI文档处理.exe",
            "360secore.exe",
            "AndrowsInstaller.exe",
            "QuickInfo.exe",
            "QuickInfo64.exe",
            "multitip.exe",
            "miniserver.exe",
            "ntdhcp.exe",
            "msinfo.exe",
            "LoginServer.exe",
            "msgchkcenter.exe",
            "Preview.exe",
            "readertray.exe",
            "SodaDownloader.exe",
            "C:\\badprogram.exe"
        ],
        "check_interval": 10
    }

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"配置文件 {CONFIG_PATH} 不存在，已创建默认配置")

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if 'blacklist' not in config or 'check_interval' not in config:
            print(f"配置文件 {CONFIG_PATH} 缺少必要键，使用默认配置")
            blacklist = DEFAULT_CONFIG['blacklist']
            check_interval = DEFAULT_CONFIG['check_interval']
        else:
            blacklist = config['blacklist']
            check_interval = config['check_interval']
            print(f"已从 {CONFIG_PATH} 加载配置：黑名单{len(blacklist)}项，检测间隔{check_interval}秒")
    except json.JSONDecodeError:
        print(f"配置文件 {CONFIG_PATH} 格式错误，使用默认配置")
        blacklist = DEFAULT_CONFIG['blacklist']
        check_interval = DEFAULT_CONFIG['check_interval']
    except Exception as e:
        print(f"加载配置文件失败：{str(e)}，使用默认配置")
        blacklist = DEFAULT_CONFIG['blacklist']
        check_interval = DEFAULT_CONFIG['check_interval']

    blocker = ProcessBlocker(blacklist, check_interval=check_interval)
    t = threading.Thread(target=blocker.start_monitoring, daemon=True)
    t.start()
    run_tray()