import logging
import os

# 代理配置
PROXY_CONFIG = {
    "enabled": False,  # 是否启用代理
    "tunnel": "y847.kdltps.com:15818",
    "username": "t13313871649778",
    "password": "0yqdp89m"
}

def get_proxy_dict():
    """获取代理配置字典"""
    if not PROXY_CONFIG["enabled"]:
        return None
        
    tunnel = PROXY_CONFIG["tunnel"]
    username = PROXY_CONFIG["username"]
    password = PROXY_CONFIG["password"]
    
    return {
        "http": f"http://{username}:{password}@{tunnel}/",
        "https": f"http://{username}:{password}@{tunnel}/"
    }

def setup_logging(log_dir: str = 'logs'):
    """
    配置日志系统
    """
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler()
        ]
    ) 