"""
B站爬虫主工作流类
"""
import os
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import time
import bs4
from config import BilibiliSearchConfig
from csv_handler import process_csv_data, json_to_csv, save_csv

class BilibiliScraper:
    def __init__(self, config: BilibiliSearchConfig = None, work_dir=None, driver_path=None):
        """
        初始化爬虫
        :param config: 搜索配置对象
        :param work_dir: 工作目录
        :param driver_path: WebDriver路径
        """
        self.config = config or BilibiliSearchConfig()
        
        # 创建工作目录
        if work_dir is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            keyword_safe = self.config.keyword.replace(' ', '_').replace('/', '_')
            # scratch目录在项目根目录下（与.code平级）
            project_root = os.path.dirname(os.path.dirname(__file__))
            work_dir = os.path.join(project_root, 'scratch', f'{keyword_safe}_{timestamp}')
        
        self.work_dir = os.path.abspath(work_dir)
        os.makedirs(self.work_dir, exist_ok=True)
        
        # WebDriver配置
        self.driver_path = driver_path or 'E:/PYTHON/Scripts/msedgedriver.exe'
        self.driver = None
        self.video_infos = []

    def start_driver(self):
        """启动WebDriver"""
        service = Service(self.driver_path)
        self.driver = webdriver.Edge(service=service)

    def stop_driver(self):
        """停止WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_page(self, url):
        """爬取单页数据"""
        self.driver.get(url)
        time.sleep(3)  # 等待页面渲染
        
        html = self.driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        videos = soup.find_all('div', class_="bili-video-card")
        
        page_videos = []
        for video in videos:
            try:
                stat = video.find('div', class_="bili-video-card__stats")
                info = video.find('div', class_="bili-video-card__info")
                
                if not stat or not info:
                    continue
                
                video_info = {}
                video_info["author"] = info.find('span', class_='bili-video-card__info--author').get_text(strip=True)
                video_info["pubdate"] = info.find('span', class_='bili-video-card__info--date').get_text(strip=True)[2:]
                video_info["title"] = info.find('h3', class_="bili-video-card__info--tit").get_text(strip=True)
                
                items = stat.find_all('span', class_='bili-video-card__stats--item')
                if len(items) >= 2:
                    video_info["views"] = items[0].get_text(strip=True)
                    video_info["danmu"] = items[1].get_text(strip=True)
                
                duration_elem = stat.find('span', class_='bili-video-card__stats__duration')
                if duration_elem:
                    video_info["duration"] = duration_elem.get_text(strip=True)
                
                page_videos.append(video_info)
                
            except Exception as e:
                print(f"解析视频信息出错: {e}")
                continue
        
        return page_videos

    def scrape_videos(self, max_count=1000, max_pages=30):
        """
        爬取视频信息
        :param max_count: 最大视频数量
        :param max_pages: 最大页数
        """
        print(f"开始爬取: {self.config}")
        print(f"目标URL: {self.config.get_search_url()}")
        
        self.start_driver()
        base_url = self.config.get_search_url()
        
        try:
            for page in range(1, max_pages + 1):
                if len(self.video_infos) >= max_count:
                    break
                
                # 构建分页URL
                if page == 1:
                    url = base_url
                else:
                    # B站的分页参数
                    offset = (page - 1) * 20  # 每页大约20个视频
                    url = base_url + f"&page={page}"
                
                print(f"正在爬取第{page}页...")
                page_videos = self.scrape_page(url)
                
                if not page_videos:  # 如果没有更多视频，停止
                    print("没有更多视频，停止爬取")
                    break
                
                self.video_infos.extend(page_videos)
                print(f"第{page}页获取{len(page_videos)}个视频，总计{len(self.video_infos)}个")
                
                if len(self.video_infos) >= max_count:
                    break
                    
                time.sleep(2)  # 避免请求过快
                
        finally:
            self.stop_driver()
        
        print(f"爬取完成，共获取{len(self.video_infos)}个视频")

    def deduplicate(self):
        """去重"""
        seen = set()
        unique_videos = []
        
        for video in self.video_infos:
            key = (video.get('title', ''), video.get('author', ''))
            if key not in seen:
                seen.add(key)
                unique_videos.append(video)
        
        removed_count = len(self.video_infos) - len(unique_videos)
        self.video_infos = unique_videos
        print(f"去重完成，移除{removed_count}个重复视频，剩余{len(self.video_infos)}个")

    def save_data(self):
        """保存数据"""
        # 保存JSON
        json_path = os.path.join(self.work_dir, 'video_infos.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.video_infos, f, ensure_ascii=False, indent=2)
        print(f"JSON已保存到: {json_path}")
        
        # 转换为CSV
        csv_path = os.path.join(self.work_dir, 'video_infos.csv')
        json_to_csv(json_path, csv_path)
        print(f"CSV已保存到: {csv_path}")
        
        # 处理CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        processed_df = process_csv_data(df)
        
        processed_path = os.path.join(self.work_dir, 'video_infos_processed.csv')
        save_csv(processed_df, processed_path)
        print(f"处理后的CSV已保存到: {processed_path}")
        
        # 保存配置信息
        config_path = os.path.join(self.work_dir, 'config.txt')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(str(self.config))
            f.write(f"\n\n爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            f.write(f"\n视频总数: {len(self.video_infos)}")
        
        return {
            'json_path': json_path,
            'csv_path': csv_path,
            'processed_path': processed_path,
            'work_dir': self.work_dir
        }

    def run(self, max_count=1000, max_pages=30):
        """运行完整流程"""
        self.scrape_videos(max_count, max_pages)
        self.deduplicate()
        return self.save_data()

def main():
    """主函数示例"""
    # 示例1: 默认武大配置
    config = BilibiliSearchConfig().set_keyword("武大")
    scraper = BilibiliScraper(config)
    result = scraper.run(max_count=200, max_pages=10)
    print(f"数据已保存到: {result['work_dir']}")

if __name__ == "__main__":
    main()
