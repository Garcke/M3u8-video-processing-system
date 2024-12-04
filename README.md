# m3u8-video-processing-system
一个视频处理系统，该系统需要从网络中爬取 m3u8 格式的视频文件，并将其下载后合并成一个完整的视频文件。系统需要能够处理下载失败和下载错误，并确保最终的视频文件是完整且无错误的。

## 1. 项目结构

```
crawler/
├── src/
│   ├── __init__.py
│   ├── crawler.py      # M3U8解析模块
│   ├── downloader.py   # 视频片段下载模块
│   ├── merger.py       # 视频合并模块
│   └── utils.py        # 工具函数
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py
│   ├── test_downloader.py
│   ├── test_merger.py
│   └── test_proxy.py
├── logs/
│   └── app.log
├── temp_segments/      # 临时文件夹
├── main.py            # 主程序
└── requirements.txt   # 依赖包
```

## 2. 功能特性

1. **M3U8解析**
   - 支持master playlist解析
   - 自动选择最高质量的视频流
   - 支持相对路径和绝对路径的URL

2. **视频下载**
   - 多线程并行下载
   - 自动重试机制
   - 支持代理设置
   - 进度显示

3. **视频合并**
   - 使用ffmpeg合并视频片段
   - 支持空格路径
   - 详细的错误诊断

4. **其他特性**
   - 命令行参数支持
   - 详细的日志记录
   - 代理切换功能
   - 异常处理机制

## 3. 使用说明

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本用法

```bash
# 不使用代理下载
python main.py --url YOUR_M3U8_URL

# 使用代理下载
python main.py --use-proxy --url YOUR_M3U8_URL
```

## 4. 测试报告

### 4.1 功能测试

1. **M3U8解析测试**

```python
def test_parse_master_playlist():
    crawler = M3U8Crawler()
    segments, durations = crawler.get_ts_segments(
        "https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8"
    )
    assert len(segments) > 0
```

2. **下载测试**

```python
def test_download_segment():
    downloader = M3U8Downloader()
    result = downloader.download_segment(
        "test_url.ts",
        "temp_segments",
        0
    )
    assert result[1] == True
```

3. **合并测试**

```python
def test_merge_ts_files():
    merger = VideoMerger()
    result = merger.merge_ts_files(
        "temp_segments",
        "output.mp4"
    )
    assert result == True
```

### 4.2 异常测试

1. **网络错误处理**

```python
def test_network_error():
    with pytest.raises(RequestException):
        crawler = M3U8Crawler()
        crawler.get_ts_segments("invalid_url")
```

2. **代理切换测试**

```python
def test_proxy_fallback():
    crawler = M3U8Crawler()
    PROXY_CONFIG["enabled"] = True
    segments = crawler.get_ts_segments(url)
    assert len(segments) > 0
```

## 5. 代码优化说明

### 5.1 性能优化

1. **并行下载**

```python
def download_all(self, segments: List[str], save_path: str) -> bool:
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        futures = {
            executor.submit(self.download_segment, url, save_path, i): i
            for i, url in enumerate(segments)
        }
```

2. **内存优化**

```python
def merge_ts_files(self, ts_dir: str, output_file: str) -> bool:
    # 使用ffmpeg直接合并，避免加载到内存
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', filelist_path,
        '-c', 'copy',
        '-y',
        output_file
    ]
```

### 5.2 可靠性优化

1. **自动重试机制**

```python
def download_segment(self, url: str, save_path: str, index: int) -> Tuple[int, bool]:
    for retry in range(self.max_retries):
        try:
            # 下载逻辑
        except RequestException as e:
            if retry == self.max_retries - 1:
                self.logger.error(f"Failed after {self.max_retries} attempts")
```

2. **代理自动切换**

```python
if self.proxies:
    self.logger.info("Retrying without proxy...")
    old_proxies = self.proxies
    self.proxies = None
    try:
        return self.get_ts_segments(m3u8_url)
    finally:
        self.proxies = old_proxies
```

## 6. 已知问题和限制

1. 某些加密的M3U8流可能无法下载
2. 需要预先安装ffmpeg
3. 代理服务器可能限制某些域名访问

## 7. 未来改进计划

1. 添加GUI界面
2. 支持更多视频格式
3. 添加下载进度条
4. 支持断点续传
5. 添加视频加密支持

## 8. 许可证

Apache License  Version 2.0, January 2004

这个项目提供了一个完整的M3U8视频下载解决方案，包括代码实现、测试用例和详细文档。如有任何问题，欢迎提出issue或贡献代码。

