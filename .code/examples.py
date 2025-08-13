"""
使用示例和快速启动脚本
"""
from datetime import datetime, timedelta
from config import BilibiliSearchConfig, get_wuda_config, get_recent_config, get_custom_config
from scraper import BilibiliScraper

def example_1_default_wuda():
    """示例1: 默认武大搜索（最近30天）"""
    print("=== 示例1: 默认武大搜索 ===")
    config = get_wuda_config()
    scraper = BilibiliScraper(config)
    result = scraper.run(max_count=100, max_pages=5)
    print(f"结果保存在: {result['work_dir']}")
    return result

def example_2_recent_search():
    """示例2: 搜索最近7天的"武汉大学图书馆"相关视频"""
    print("=== 示例2: 最近7天搜索 ===")
    config = get_recent_config("武汉大学图书馆", days=7)
    scraper = BilibiliScraper(config)
    result = scraper.run(max_count=100, max_pages=5)
    print(f"结果保存在: {result['work_dir']}")
    return result

def example_3_custom_date_range():
    """示例3: 自定义日期范围搜索"""
    print("=== 示例3: 自定义日期范围 ===")
    start_date = "2024-07-01"  # 开始日期
    end_date = "2024-07-31"    # 结束日期
    config = get_custom_config("武大", start_date, end_date)
    scraper = BilibiliScraper(config)
    result = scraper.run(max_count=150, max_pages=8)
    print(f"结果保存在: {result['work_dir']}")
    return result

def example_4_flexible_config():
    """示例4: 灵活配置搜索"""
    print("=== 示例4: 灵活配置 ===")
    config = BilibiliSearchConfig()
    config.set_keyword("华中科技大学") \
          .set_date_range(days_back=15) \
          .set_order("pubdate")  # 按发布时间排序
    
    scraper = BilibiliScraper(config)
    result = scraper.run(max_count=200, max_pages=10)
    print(f"结果保存在: {result['work_dir']}")
    return result

def quick_search(keyword, days_back=7, max_count=100):
    """快速搜索函数"""
    print(f"=== 快速搜索: {keyword} (最近{days_back}天) ===")
    config = get_recent_config(keyword, days=days_back)
    scraper = BilibiliScraper(config)
    result = scraper.run(max_count=max_count, max_pages=max_count//20+1)
    print(f"搜索完成! 结果保存在: {result['work_dir']}")
    return result

def main():
    """主菜单"""
    print("B站视频爬虫 - 选择运行模式:")
    print("1. 默认武大搜索（最近30天）")
    print("2. 武汉大学图书馆搜索（最近7天）") 
    print("3. 自定义日期范围搜索")
    print("4. 灵活配置搜索")
    print("5. 快速搜索")
    print("0. 退出")
    
    choice = input("请选择 (0-5): ").strip()
    
    if choice == "1":
        example_1_default_wuda()
    elif choice == "2":
        example_2_recent_search()
    elif choice == "3":
        example_3_custom_date_range()
    elif choice == "4":
        example_4_flexible_config()
    elif choice == "5":
        keyword = input("请输入搜索关键词: ").strip()
        days = int(input("搜索最近几天的视频 (默认7): ").strip() or "7")
        count = int(input("最大视频数量 (默认100): ").strip() or "100")
        quick_search(keyword, days, count)
    elif choice == "0":
        print("再见!")
    else:
        print("无效选择")

if __name__ == "__main__":
    # 可以直接运行示例，或运行交互菜单
    # main()  # 交互菜单
    
    # 或直接运行某个示例
    example_1_default_wuda()
