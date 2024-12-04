import os
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
from requests.exceptions import RequestException
from .utils import get_proxy_dict

class M3U8Downloader:
    def __init__(self, max_workers: int = 10, max_retries: int = 3):
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        self.proxies = get_proxy_dict()
        
    def download_segment(self, url: str, save_path: str, index: int) -> Tuple[int, bool]:
        """
        下载单个ts片段
        
        Args:
            url: ts片段URL
            save_path: 保存路径
            index: 片段索引
            
        Returns:
            (index, 是否成功)
        """
        for retry in range(self.max_retries):
            try:
                # 使用代理下载
                response = requests.get(
                    url, 
                    timeout=10,
                    proxies=self.proxies
                )
                
                # 只有在状态码为404时才记录警告，其他错误继续重试
                if response.status_code == 404:
                    self.logger.error(f"Segment {index} not found at {url}")
                    return index, False
                    
                response.raise_for_status()
                
                filename = os.path.join(save_path, f"{index:05d}.ts")
                with open(filename, 'wb') as f:
                    f.write(response.content)
                    
                self.logger.debug(f"Successfully downloaded segment {index}")
                return index, True
                
            except RequestException as e:
                if retry == self.max_retries - 1:
                    self.logger.error(f"Failed to download segment {index} after {self.max_retries} attempts: {str(e)}")
                else:
                    self.logger.debug(f"Retry {retry + 1} for segment {index} due to: {str(e)}")
                
        return index, False
        
    def download_all(self, segments: List[str], save_path: str) -> bool:
        """
        并行下载所有ts片段
        
        Args:
            segments: ts片段URL列表
            save_path: 保存路径
            
        Returns:
            是否全部下载成功
        """
        os.makedirs(save_path, exist_ok=True)
        failed_segments = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.download_segment, url, save_path, i): i
                for i, url in enumerate(segments)
            }
            
            for future in as_completed(future_to_index):
                index, success = future.result()
                if not success:
                    failed_segments.append(index)
                    
        return len(failed_segments) == 0 