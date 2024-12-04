import os
import argparse
from src.crawler import M3U8Crawler
from src.downloader import M3U8Downloader
from src.merger import VideoMerger
from src.utils import setup_logging, PROXY_CONFIG

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='M3U8视频下载器')
    parser.add_argument('--use-proxy', action='store_true', help='是否使用代理')
    parser.add_argument('--url', type=str, help='M3U8链接', 
                        default="https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8")
    args = parser.parse_args()
    
    # 设置是否使用代理
    PROXY_CONFIG["enabled"] = args.use_proxy
    
    # 设置日志
    setup_logging()
    
    # 初始化各个模块
    crawler = M3U8Crawler()
    downloader = M3U8Downloader(max_workers=10)
    merger = VideoMerger()
    
    print("开始下载视频...")
    print(f"M3U8 URL: {args.url}")
    if args.use_proxy:
        print("使用代理下载...")
    else:
        print("不使用代理下载...")
    
    try:
        # 获取ts片段列表
        segments, durations = crawler.get_ts_segments(args.url)
        
        if not segments:
            print("未找到视频片段！请检查URL是否正确")
            return
            
        print(f"找到 {len(segments)} 个视频片段")
        print("第一个片段URL示例:", segments[0])
        
        # 创建临时目录存放ts片段
        temp_dir = "temp_segments"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 下载所有片段
        print("正在下载视频片段...")
        if downloader.download_all(segments, temp_dir):
            print("所有片段下载完成")
            
            # 合并视频
            print("正在合并视频片段...")
            output_file = "output.mp4"
            if merger.merge_ts_files(temp_dir, output_file):
                print(f"视频合并完成！输出文件：{output_file}")
                print(f"文件保存在: {os.path.abspath(output_file)}")
            else:
                print("视频合并失败！")
        else:
            print("部分片段下载失败！")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print("请检查网络连接是否正常")

if __name__ == "__main__":
    main() 