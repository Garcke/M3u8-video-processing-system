import unittest
import requests
from src.utils import get_proxy_dict

class TestProxy(unittest.TestCase):
    def test_proxy_connection(self):
        """测试代理连接是否正常"""
        proxies = get_proxy_dict()
        try:
            response = requests.get(
                "https://dev.kdlapi.com/testproxy",
                proxies=proxies,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            print(f"Proxy test response: {response.text}")
        except Exception as e:
            self.fail(f"Proxy test failed: {str(e)}")

if __name__ == '__main__':
    unittest.main() 