import unittest
import tempfile
import os
import logging
import sys

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.downloader import M3U8Downloader
from src.crawler import M3U8Crawler

# 设置日志级别，减少测试时的警告信息
logging.getLogger('src.downloader').setLevel(logging.ERROR)

class TestM3U8Downloader(unittest.TestCase):
    def setUp(self):
        self.downloader = M3U8Downloader(max_workers=5, max_retries=2)
        self.crawler = M3U8Crawler()
        self.temp_dir = tempfile.mkdtemp()
        self.test_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        
    def test_download_segment(self):
        """测试下载有效的视频片段"""
        segments = self.crawler.get_ts_segments(self.test_url)
        
        if not segments:
            self.skipTest("No segments found in test stream")
            
        # 测试下载第一个片段
        result = self.downloader.download_segment(segments[0], self.temp_dir, 0)
        self.assertEqual(result[1], True)  # 应该成功下载
        
        # 验证文件是否存在
        expected_file = os.path.join(self.temp_dir, "00000.ts")
        self.assertTrue(os.path.exists(expected_file))
            
    def test_invalid_url(self):
        """测试处理无效URL的情况"""
        with self.assertLogs('src.downloader', level='ERROR') as cm:
            invalid_url = "https://test-streams.mux.dev/nonexistent.ts"
            result = self.downloader.download_segment(invalid_url, self.temp_dir, 0)
            self.assertEqual(result, (0, False))
            
            # 验证是否记录了正确的错误日志
            self.assertTrue(any('Segment 0 not found' in msg for msg in cm.output))
        
    def tearDown(self):
        """清理测试环境"""
        try:
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up test directory: {e}")

if __name__ == '__main__':
    unittest.main() 