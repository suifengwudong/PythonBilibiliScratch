"""
PyQt5版B站爬虫与黑名单管理界面
"""
import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt
from config import BilibiliSearchConfig
from scraper import BilibiliScraper
from blacklist_manager import BlacklistManager

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B站爬虫与黑名单管理 (PyQt5)")
        self.resize(1100, 700)
        self.blacklist_mgr = BlacklistManager()
        self.video_df = pd.DataFrame()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # 搜索区
        search_group = QHBoxLayout()
        search_group.addWidget(QLabel("关键词:"))
        self.keyword_edit = QLineEdit("武大")
        self.keyword_edit.setFixedWidth(120)
        search_group.addWidget(self.keyword_edit)
        search_group.addWidget(QLabel("起始日期:"))
        self.start_edit = QLineEdit()
        self.start_edit.setFixedWidth(100)
        search_group.addWidget(self.start_edit)
        search_group.addWidget(QLabel("结束日期:"))
        self.end_edit = QLineEdit()
        self.end_edit.setFixedWidth(100)
        search_group.addWidget(self.end_edit)
        search_group.addWidget(QLabel("搜索深度(max_count):"))
        self.max_count_edit = QLineEdit("1000")
        self.max_count_edit.setFixedWidth(80)
        search_group.addWidget(self.max_count_edit)
        self.run_btn = QPushButton("运行爬虫")
        self.run_btn.setFixedWidth(100)
        self.run_btn.clicked.connect(self.run_scraper)
        search_group.addWidget(self.run_btn)
        main_layout.addLayout(search_group)

        # 黑名单管理区
        bl_group = QHBoxLayout()
        self.show_bl_btn = QPushButton("查看黑名单")
        self.show_bl_btn.setFixedWidth(120)
        self.show_bl_btn.clicked.connect(self.show_blacklist)
        bl_group.addWidget(self.show_bl_btn)
        self.clear_bl_btn = QPushButton("清空黑名单")
        self.clear_bl_btn.setFixedWidth(120)
        self.clear_bl_btn.clicked.connect(self.clear_blacklist)
        bl_group.addWidget(self.clear_bl_btn)
        bl_group.addStretch()
        main_layout.addLayout(bl_group)

        # 排序区
        sort_group = QHBoxLayout()
        sort_group.addWidget(QLabel("排序字段:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["author", "pubdate", "title", "views", "danmu", "duration"])
        self.sort_btn = QPushButton("排序")
        self.sort_btn.setFixedWidth(80)
        self.sort_btn.clicked.connect(self.sort_table)
        sort_group.addWidget(self.sort_combo)
        sort_group.addWidget(self.sort_btn)
        sort_group.addStretch()
        main_layout.addLayout(sort_group)

        # 视频表格区
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["author", "pubdate", "title", "views", "danmu", "duration"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(self.table.SelectRows)
        main_layout.addWidget(self.table)

        # 操作按钮区
        op_group = QHBoxLayout()
        self.add_bl_btn = QPushButton("选中加入黑名单")
        self.add_bl_btn.setFixedWidth(150)
        self.add_bl_btn.clicked.connect(self.add_selected_to_blacklist)
        op_group.addWidget(self.add_bl_btn)
        self.load_csv_btn = QPushButton("加载视频CSV")
        self.load_csv_btn.setFixedWidth(150)
        self.load_csv_btn.clicked.connect(self.load_csv)
        op_group.addWidget(self.load_csv_btn)
        op_group.addStretch()
        main_layout.addLayout(op_group)

        self.setLayout(main_layout)

    def show_blacklist(self):
        bl = self.blacklist_mgr.data.get("blacklist", [])
        msg = "\n".join([str(item) for item in bl]) or "黑名单为空"
        QMessageBox.information(self, "当前黑名单", msg)

    def clear_blacklist(self):
        if QMessageBox.question(self, "确认", "确定要清空黑名单吗？") == QMessageBox.Yes:
            self.blacklist_mgr.data["blacklist"] = []
            self.blacklist_mgr.save_blacklist()
            QMessageBox.information(self, "提示", "黑名单已清空")

    def run_scraper(self):
        keyword = self.keyword_edit.text().strip()
        start = self.start_edit.text().strip()
        end = self.end_edit.text().strip()
        max_count_str = self.max_count_edit.text().strip()
        try:
            max_count = int(max_count_str)
        except Exception:
            max_count = 1000
        config = BilibiliSearchConfig().set_keyword(keyword)
        if start or end:
            config.set_date_range(start_date=start or None, end_date=end or None)
        try:
            scraper = BilibiliScraper(config)
            result = scraper.run(max_count=max_count)
            QMessageBox.information(self, "完成", f"爬取完成，结果目录: {result['work_dir']}")
            # 自动加载最新csv
            csv_path = os.path.join(result['work_dir'], 'video_infos_processed.csv')
            if os.path.exists(csv_path):
                self.load_csv(csv_path)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"爬虫运行出错: {e}")

    def load_csv(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "选择CSV文件", "", "CSV Files (*.csv)")
        if path:
            self.video_df = pd.read_csv(path)
            self.refresh_table()

    def refresh_table(self):
        df = self.video_df
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            for j, col in enumerate(["author", "pubdate", "title", "views", "danmu", "duration"]):
                item = QTableWidgetItem(str(row[col]))
                if col == "title":
                    item.setToolTip(str(row[col]))
                self.table.setItem(i, j, item)
        self.table.resizeRowsToContents()

    def sort_table(self):
        col = self.sort_combo.currentText()
        if not self.video_df.empty:
            # 排序后同步self.video_df，保证选中行与数据一致
            ascending = False if col in ["views", "danmu", "duration"] else True
            self.video_df = self.video_df.sort_values(by=col, ascending=ascending).reset_index(drop=True)
            self.refresh_table()

    def add_selected_to_blacklist(self):
        rows = set(idx.row() for idx in self.table.selectedIndexes())
        if not rows:
            QMessageBox.information(self, "提示", "请先选中要加入黑名单的视频行")
            return
        bl = self.blacklist_mgr.data["blacklist"]
        added = 0
        for r in rows:
            rowdata = self.video_df.iloc[r]
            # 优先bvid字段，否则用title+author+pubdate对象
            bvid = rowdata.get("bvid") if "bvid" in rowdata else None
            if bvid and bvid not in bl:
                bl.append(bvid)
                added += 1
            elif not bvid:
                video_obj = {
                    "title": str(rowdata.get("title", "")),
                    "author": str(rowdata.get("author", "")),
                    "pubdate": str(rowdata.get("pubdate", ""))
                }
                if video_obj not in bl:
                    bl.append(video_obj)
                    added += 1
        self.blacklist_mgr.save_blacklist()
        QMessageBox.information(self, "完成", f"已添加{added}项到黑名单")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
