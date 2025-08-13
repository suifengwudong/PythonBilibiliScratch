"""
配置文件 - 可自定义搜索参数
"""
from datetime import datetime, timedelta
from urllib.parse import quote

class BilibiliSearchConfig:
    def __init__(self):
        # 默认配置
        self.keyword = "武大"  # 搜索关键词
        self.order = "click"  # 排序方式：click(综合排序), pubdate(最新发布), dm(最多弹幕), stow(最多收藏)
        self.search_source = "5"  # 搜索来源
        self.from_source = "webtop_search"
        self.spm_id_from = "333.788"
        
        # 日期范围（默认最近30天到今天）
        self.end_date = datetime.now()  # 结束日期（默认今天）
        self.start_date = self.end_date - timedelta(days=30)  # 开始日期（默认30天前）
        
    def set_keyword(self, keyword):
        """设置搜索关键词"""
        self.keyword = keyword
        return self
    
    def set_date_range(self, start_date=None, end_date=None, days_back=30):
        """
        设置日期范围
        :param start_date: 开始日期 (datetime对象或字符串'YYYY-MM-DD')
        :param end_date: 结束日期 (datetime对象或字符串'YYYY-MM-DD'，默认今天)
        :param days_back: 如果只指定end_date，往前推多少天作为start_date
        """
        if end_date is None:
            self.end_date = datetime.now()
        elif isinstance(end_date, str):
            self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            self.end_date = end_date
            
        if start_date is None:
            self.start_date = self.end_date - timedelta(days=days_back)
        elif isinstance(start_date, str):
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            self.start_date = start_date
        return self
    
    def set_order(self, order):
        """
        设置排序方式
        :param order: click(综合), pubdate(最新), dm(弹幕), stow(收藏)
        """
        self.order = order
        return self
    
    def get_search_url(self):
        """生成搜索URL"""
        # 转换为时间戳（秒）
        start_timestamp = int(self.start_date.timestamp())
        end_timestamp = int(self.end_date.timestamp())
        
        # URL编码关键词
        encoded_keyword = quote(self.keyword)
        
        url = (f"https://search.bilibili.com/video"
               f"?keyword={encoded_keyword}"
               f"&from_source={self.from_source}"
               f"&spm_id_from={self.spm_id_from}"
               f"&search_source={self.search_source}"
               f"&order={self.order}")
        
        # 添加日期范围（如果有的话）
        if self.start_date and self.end_date:
            url += f"&pubtime_begin_s={start_timestamp}&pubtime_end_s={end_timestamp}"
            
        return url
    
    def __str__(self):
        return (f"搜索配置:\n"
                f"  关键词: {self.keyword}\n"
                f"  排序: {self.order}\n"
                f"  日期范围: {self.start_date.strftime('%Y-%m-%d')} 到 {self.end_date.strftime('%Y-%m-%d')}")

# 预定义配置
def get_wuda_config():
    """武大相关配置"""
    return BilibiliSearchConfig().set_keyword("武大")

def get_recent_config(keyword, days=7):
    """最近几天的配置"""
    return BilibiliSearchConfig().set_keyword(keyword).set_date_range(days_back=days)

def get_custom_config(keyword, start_date, end_date):
    """自定义配置"""
    return BilibiliSearchConfig().set_keyword(keyword).set_date_range(start_date, end_date)
