"""
黑名单管理工具
用于管理不希望出现在处理后CSV中的视频
"""
import json
import os
from datetime import datetime

class BlacklistManager:
    def __init__(self, blacklist_path=None):
        if blacklist_path is None:
            self.blacklist_path = os.path.join(os.path.dirname(__file__), 'black_list.json')
        else:
            self.blacklist_path = blacklist_path
        
        self.data = self.load_blacklist()
    
    def load_blacklist(self):
        """加载黑名单文件"""
        if os.path.exists(self.blacklist_path):
            with open(self.blacklist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建默认黑名单文件
            default_data = {
                "_description": "黑名单配置文件 - 用于过滤不希望出现在处理后CSV中的视频",
                "_usage": "支持三种格式：bvid列表、aid列表、或完整视频对象列表",
                "_examples": {
                    "bvid_list": ["BV1xx411c7mD", "BV1yy411c7mE"],
                    "aid_list": [12345, 67890], 
                    "video_objects": [
                        {
                            "title": "不相关的视频标题",
                            "author": "作者名",
                            "pubdate": "2024-07-25"
                        }
                    ]
                },
                "blacklist": []
            }
            self.save_blacklist(default_data)
            return default_data
    
    def save_blacklist(self, data=None):
        """保存黑名单文件"""
        if data is None:
            data = self.data
        with open(self.blacklist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_bvid(self, bvid):
        """添加bvid到黑名单"""
        if 'blacklist' not in self.data:
            self.data['blacklist'] = []
        if bvid not in self.data['blacklist']:
            self.data['blacklist'].append(bvid)
            self.save_blacklist()
            print(f"已添加bvid到黑名单: {bvid}")
    
    def add_video_object(self, title, author, pubdate):
        """添加视频对象到黑名单"""
        if 'blacklist' not in self.data:
            self.data['blacklist'] = []
        
        video_obj = {
            "title": title,
            "author": author,  
            "pubdate": pubdate
        }
        
        # 检查是否已存在
        for item in self.data['blacklist']:
            if isinstance(item, dict) and item.get('title') == title and item.get('author') == author:
                print(f"视频已在黑名单中: {title}")
                return
        
        self.data['blacklist'].append(video_obj)
        self.save_blacklist()
        print(f"已添加视频到黑名单: {title}")
    
    def add_from_csv(self, csv_file, date_before=None):
        """从CSV文件批量添加到黑名单（指定日期之前的视频）"""
        import pandas as pd
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        if date_before:
            df['pubdate'] = pd.to_datetime(df['pubdate'], errors='coerce')
            df_filtered = df[df['pubdate'] <= pd.to_datetime(date_before)]
        else:
            df_filtered = df
        
        added_count = 0
        for _, row in df_filtered.iterrows():
            self.add_video_object(row['title'], row['author'], row['pubdate'])
            added_count += 1
        
        print(f"从CSV文件添加了{added_count}个视频到黑名单")
    
    def remove_item(self, identifier):
        """移除黑名单项"""
        if 'blacklist' not in self.data:
            return False
        
        original_length = len(self.data['blacklist'])
        
        # 如果是字符串，直接移除
        if isinstance(identifier, str):
            if identifier in self.data['blacklist']:
                self.data['blacklist'].remove(identifier)
        else:
            # 如果是字典，按标题匹配移除
            self.data['blacklist'] = [
                item for item in self.data['blacklist'] 
                if not (isinstance(item, dict) and item.get('title') == identifier.get('title'))
            ]
        
        if len(self.data['blacklist']) < original_length:
            self.save_blacklist()
            print(f"已从黑名单移除: {identifier}")
            return True
        else:
            print(f"未找到要移除的项: {identifier}")
            return False
    
    def clear_blacklist(self):
        """清空黑名单"""
        self.data['blacklist'] = []
        self.save_blacklist()
        print("黑名单已清空")
    
    def show_blacklist(self):
        """显示当前黑名单"""
        blacklist = self.data.get('blacklist', [])
        if not blacklist:
            print("黑名单为空")
            return
        
        print(f"当前黑名单共{len(blacklist)}项:")
        for i, item in enumerate(blacklist, 1):
            if isinstance(item, str):
                print(f"{i}. {item}")
            elif isinstance(item, dict):
                print(f"{i}. {item.get('title', 'N/A')} - {item.get('author', 'N/A')} ({item.get('pubdate', 'N/A')})")

def main():
    """黑名单管理命令行工具"""
    manager = BlacklistManager()
    
    while True:
        print("\n=== 黑名单管理 ===")
        print("1. 查看黑名单")
        print("2. 添加bvid")
        print("3. 添加视频对象")
        print("4. 从CSV批量添加")
        print("5. 移除项目")
        print("6. 清空黑名单")
        print("0. 退出")
        
        choice = input("请选择操作 (0-6): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            manager.show_blacklist()
        elif choice == "2":
            bvid = input("请输入bvid: ").strip()
            manager.add_bvid(bvid)
        elif choice == "3":
            title = input("请输入视频标题: ").strip()
            author = input("请输入作者: ").strip()
            pubdate = input("请输入发布日期 (YYYY-MM-DD): ").strip()
            manager.add_video_object(title, author, pubdate)
        elif choice == "4":
            csv_file = input("请输入CSV文件路径: ").strip()
            date_before = input("只添加此日期之前的视频 (YYYY-MM-DD，留空表示全部): ").strip() or None
            manager.add_from_csv(csv_file, date_before)
        elif choice == "5":
            manager.show_blacklist()
            index = input("请输入要移除的项目编号: ").strip()
            try:
                idx = int(index) - 1
                item = manager.data['blacklist'][idx]
                manager.remove_item(item)
            except (ValueError, IndexError):
                print("无效的编号")
        elif choice == "6":
            confirm = input("确定要清空黑名单吗? (y/N): ").strip().lower()
            if confirm == 'y':
                manager.clear_blacklist()

if __name__ == "__main__":
    main()
