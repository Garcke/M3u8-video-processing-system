import re
import logging
import requests
from urllib.parse import urljoin, urlparse
from typing import Optional, List, Tuple
from .utils import get_proxy_dict

class M3U8Crawler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.timeout = 30
        self.proxies = get_proxy_dict()
        
    def get_ts_segments(self, m3u8_url: str) -> Tuple[List[str], List[float]]:
        """
        解析m3u8文件获取所有ts片段链接和时长
        """
        try:
            response = self.session.get(
                m3u8_url, 
                timeout=self.timeout,
                proxies=self.proxies
            )
            response.raise_for_status()
            
            # 添加调试信息
            self.logger.debug(f"M3U8 content:\n{response.text}")
            
            base_url = self._get_base_url(m3u8_url)
            content = response.text.strip()
            
            # 检查是否是master playlist
            if '#EXT-X-STREAM-INF' in content:
                self.logger.info("Found master playlist, selecting best quality stream")
                best_url = self._get_best_playlist_url(content, base_url)
                if best_url:
                    self.logger.info(f"Selected stream: {best_url}")
                    # 如果使用代理失败，尝试不使用代理
                    try:
                        return self.get_ts_segments(best_url)
                    except requests.exceptions.RequestException as e:
                        self.logger.warning(f"Failed with proxy, trying without proxy: {str(e)}")
                        old_proxies = self.proxies
                        self.proxies = None
                        try:
                            return self.get_ts_segments(best_url)
                        finally:
                            self.proxies = old_proxies
                else:
                    self.logger.error("No valid stream found in master playlist")
                    return [], []
            
            segments = []
            durations = []
            lines = content.split('\n')
            current_duration = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                if line.startswith('#EXTINF:'):
                    try:
                        current_duration = float(line.split(':')[1].split(',')[0])
                    except (IndexError, ValueError) as e:
                        self.logger.warning(f"Failed to parse duration from line: {line}")
                        current_duration = 0
                elif line.endswith('.ts') or '.ts?' in line:
                    if not line.startswith('http'):
                        line = urljoin(base_url, line)
                    segments.append(line)
                    durations.append(current_duration if current_duration is not None else 0)
                    
            if not segments:
                self.logger.warning(f"No ts segments found in {m3u8_url}")
                self.logger.debug(f"M3U8 content:\n{content}")
                
            return segments, durations
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to parse m3u8 file {m3u8_url}: {str(e)}")
            # 如果使用代理失败，尝试不使用代理
            if self.proxies:
                self.logger.info("Retrying without proxy...")
                old_proxies = self.proxies
                self.proxies = None
                try:
                    return self.get_ts_segments(m3u8_url)
                finally:
                    self.proxies = old_proxies
            return [], []
            
    def _get_base_url(self, url: str) -> str:
        """获取基础URL，用于处理相对路径"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"
        
    def _get_best_playlist_url(self, content: str, base_url: str) -> Optional[str]:
        """从master playlist中获取最高质量的流"""
        max_bandwidth = -1
        best_url = None
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '#EXT-X-STREAM-INF' in line:
                # 解析带宽信息
                bandwidth_match = re.search(r'BANDWIDTH=(\d+)', line)
                if bandwidth_match and i + 1 < len(lines):
                    bandwidth = int(bandwidth_match.group(1))
                    if bandwidth > max_bandwidth:
                        max_bandwidth = bandwidth
                        playlist_url = lines[i + 1].strip()
                        if not playlist_url.startswith('http'):
                            playlist_url = urljoin(base_url, playlist_url)
                        best_url = playlist_url
                        
        return best_url