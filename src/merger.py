import os
import logging
import subprocess
from typing import List

class VideoMerger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def merge_ts_files(self, ts_dir: str, output_file: str) -> bool:
        """
        使用ffmpeg合并ts片段
        """
        try:
            # 获取绝对路径并统一使用正斜杠
            ts_dir = os.path.abspath(ts_dir).replace('\\', '/')
            output_file = os.path.abspath(output_file).replace('\\', '/')
            filelist_path = os.path.join(ts_dir, "filelist.txt").replace('\\', '/')
            
            # 检查ts文件
            ts_files = sorted([f for f in os.listdir(ts_dir) if f.endswith('.ts')])
            if not ts_files:
                self.logger.error(f"No .ts files found in {ts_dir}")
                return False
                
            print(f"Found {len(ts_files)} .ts files to merge")
            
            # 创建filelist.txt
            with open(filelist_path, 'w', encoding='utf-8') as f:
                for ts_file in ts_files:
                    # 使用完整路径
                    full_path = os.path.join(ts_dir, ts_file).replace('\\', '/')
                    f.write(f"file '{full_path}'\n")
            
            print(f"Created file list at: {filelist_path}")
            
            # 使用ffmpeg合并视频
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', filelist_path,
                '-c', 'copy',
                '-y',
                output_file
            ]
            
            self.logger.info(f"Executing command: {' '.join(cmd)}")
            
            # 执行命令
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                shell=True  # 在Windows上需要shell=True
            )
            
            if process.returncode == 0:
                self.logger.info(f"Successfully merged video to {output_file}")
                print(f"Video merged successfully to: {os.path.abspath(output_file)}")
                return True
            else:
                self.logger.error(f"FFmpeg stderr output:\n{process.stderr}")
                
                # 添加更多调试信息
                print("\nDebug information:")
                print(f"Working directory: {os.getcwd()}")
                print(f"First few lines of filelist.txt:")
                with open(filelist_path, 'r', encoding='utf-8') as f:
                    print(f.read()[:200])
                print("\nChecking first few ts files:")
                for ts_file in ts_files[:3]:
                    full_path = os.path.join(ts_dir, ts_file)
                    exists = os.path.exists(full_path)
                    size = os.path.getsize(full_path) if exists else 'N/A'
                    print(f"{full_path}: exists={exists}, size={size}")
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error during video merging: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False