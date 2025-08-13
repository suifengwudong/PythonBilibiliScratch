# B站视频爬虫项目

这是一个可复用的B站视频搜索爬虫项目，支持灵活的关键词和日期配置，以及黑名单过滤功能。

## 项目结构

```
scratch_bilibili/
├── .code/                  # 源代码目录
│   ├── config.py           # 搜索配置模块
│   ├── csv_handler.py      # CSV数据处理模块  
│   ├── scraper.py          # 爬虫核心模块
│   ├── examples.py         # 使用示例
│   ├── blacklist_manager.py # 黑名单管理工具
│   ├── black_list.json     # 黑名单配置文件
│   └── gui_app_qt.py       # PyQt5美观图形界面（推荐）
├── scratch/                # 爬取结果存储目录（自动生成）
├── requirements.txt        # 依赖包列表
└── README.md              # 说明文档
```

## 主要特性

1. **灵活的关键词配置** - 可随时更换搜索关键词
2. **灵活的日期配置** - 支持自定义日期范围，默认最新日期为今天
3. **黑名单过滤系统** - 自动过滤不需要的视频内容
4. **数据处理流水线** - 自动去重、格式化、清洗数据
5. **结果分类存储** - 按时间戳和关键词自动创建存储目录
6. **可复用架构** - 模块化设计，易于扩展和复用


## 图形界面（推荐）

### PyQt5美观GUI

本项目推荐使用PyQt5开发的美观图形界面，支持：

- 一键运行爬虫，自动加载最新结果
- 表格展示所有获取视频，支持按任意字段排序
- 多选视频一键加入黑名单
- 黑名单查看与清空
- 支持手动加载历史CSV结果

启动方法：

```bash
cd .code
python gui_app_qt.py
```

> 注：原tkinter版本已废弃，无需再使用。

### 黑名单格式支持

黑名单文件 `.code/black_list.json` 支持三种格式：

1. **bvid列表** - 直接过滤指定的bvid
2. **aid列表** - 直接过滤指定的aid  
3. **视频对象列表** - 根据标题+作者+日期精确匹配过滤

```json
{
  "blacklist": [
    "BV1xx411c7mD",
    12345,
    {
      "title": "不相关的视频标题",
      "author": "作者名",
      "pubdate": "2024-07-25"
    }
  ]
}
```

## 快速开始

### 1. 基础用法

```python
import sys
sys.path.append('.code')

from config import BilibiliSearchConfig
from scraper import BilibiliScraper

# 创建配置
config = BilibiliSearchConfig()
config.set_keyword("武大").set_date_range(days_back=7)

# 运行爬虫
scraper = BilibiliScraper(config)
result = scraper.run(max_count=100)
```

### 2. 预定义配置

```python
import sys
sys.path.append('.code')

from config import get_wuda_config, get_recent_config, get_custom_config

# 武大配置
config1 = get_wuda_config()

# 最近N天配置  
config2 = get_recent_config("武汉大学图书馆", days=7)

# 自定义日期范围
config3 = get_custom_config("华科", "2024-07-01", "2024-07-31")
```


### 3. 运行示例（命令行/脚本）

```bash
cd .code
python examples.py
```

## 配置选项

### 关键词配置
- `set_keyword(keyword)` - 设置搜索关键词

### 日期配置  
- `set_date_range(start_date, end_date, days_back)` - 设置日期范围
- 默认：最近30天到今天
- 支持字符串('YYYY-MM-DD')或datetime对象

### 排序配置
- `set_order(order)` - 设置排序方式
  - `click` - 综合排序(默认)
  - `pubdate` - 最新发布
  - `dm` - 最多弹幕  
  - `stow` - 最多收藏

## 输出文件

每次运行会在 `scratch/` 目录下创建以下文件:

- `video_infos.json` - 原始JSON数据
- `video_infos.csv` - CSV格式数据
- `video_infos_processed.csv` - 处理后的数据（已应用黑名单过滤）
- `config.txt` - 运行配置记录

黑名单过滤会在生成 `video_infos_processed.csv` 时自动应用。


## 依赖要求

见 `requirements.txt`，如需图形界面请确保已安装 PyQt5：

```bash
pip install PyQt5
```

## 注意事项

1. 需要配置Edge浏览器驱动路径
2. 爬取时请遵守网站robots.txt和使用条款
3. 建议设置合理的延时避免被封禁
4. 黑名单配置文件位于 `.code/black_list.json`
5. 运行代码时需要从项目根目录或正确设置Python路径

## 使用流程

1. 配置黑名单（可选）
2. 运行爬虫获取数据
3. 查看 `scratch/` 目录下的结果文件
4. `video_infos_processed.csv` 为最终处理后的数据
