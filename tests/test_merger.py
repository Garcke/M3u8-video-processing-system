import unittest
import os
import tempfile
import shutil
import subprocess

import sys
# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.merger import VideoMerger

def is_ffmpeg_installed():
    """检查ffmpeg是否已安装"""
    try:
        # 在Windows系统中，需要指定shell=True
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      shell=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

@unittest.skipUnless(is_ffmpeg_installed(), "FFmpeg is not installed")
class TestVideoMerger(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.merger = VideoMerger()
        # 使用项目根目录下的temp_segments文件夹
        self.temp_segments_dir = os.path.join(parent_dir, "temp_segments")
        # 创建输出目录
        self.output_dir = tempfile.mkdtemp()
        print(f"\nUsing existing temp_segments directory: {self.temp_segments_dir}")
        print(f"Output directory created: {self.output_dir}")
                
    def test_merge_existing_ts_files(self):
        """测试合并已存在的ts文件"""
        # 确保temp_segments目录存在且包含ts文件
        self.assertTrue(os.path.exists(self.temp_segments_dir), "temp_segments directory not found")
        ts_files = [f for f in os.listdir(self.temp_segments_dir) if f.endswith('.ts')]
        self.assertTrue(len(ts_files) > 0, "No .ts files found in temp_segments directory")
        
        print(f"Found {len(ts_files)} .ts files in temp_segments directory")
        # Add debug information
        print(f"First few TS files: {ts_files[:5]}")
        for ts_file in ts_files[:5]:
            full_path = os.path.join(self.temp_segments_dir, ts_file)
            print(f"File exists: {os.path.exists(full_path)}, Size: {os.path.getsize(full_path) if os.path.exists(full_path) else 'N/A'}")
        
        # 尝试合并视频
        output_file = os.path.join(self.output_dir, "merged_output.mp4")
        result = self.merger.merge_ts_files(self.temp_segments_dir, output_file)
        
        # 检查结果
        self.assertTrue(result, "Video merging failed")
        self.assertTrue(os.path.exists(output_file), "Output file was not created")
        
        # 检查输出文件大小
        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 0, "Output file is empty")
        print(f"Successfully created merged video: {output_file} (size: {file_size} bytes)")
        
    def test_merge_with_spaces(self):
        """测试带空格路径的合并"""
        # 创建带空格的输出文件路径
        output_file = os.path.join(self.output_dir, "merged video.mp4")
        result = self.merger.merge_ts_files(self.temp_segments_dir, output_file)
        
        self.assertTrue(result, "Video merging failed with spaces in path")
        self.assertTrue(os.path.exists(output_file), "Output file was not created")
        
    def tearDown(self):
        """测试后的清理工作"""
        # 只清理输出目录，保留temp_segments
        try:
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
                print(f"Cleaned up output directory")
        except Exception as e:
            print(f"Warning: Failed to clean up output directory: {e}")

if __name__ == '__main__':
    if not is_ffmpeg_installed():
        print("Warning: FFmpeg is not installed. Tests will be skipped.")
        print("Please install FFmpeg and add it to your system PATH.")
    unittest.main() 