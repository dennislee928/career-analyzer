#!/usr/bin/env python3
"""
自動化排程腳本
用於定期執行104職缺爬蟲任務
"""

import schedule
import time
import logging
import json
from datetime import datetime
from scrape_104 import Job104Scraper
from database import JobDatabase

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobScheduler:
    def __init__(self):
        self.scraper = Job104Scraper()
        self.db = JobDatabase(db_type="sqlite", db_path="jobs.db")
        
        # 預設搜尋關鍵字列表
        self.default_keywords = [
            "Python", "JavaScript", "Java", "C++", "Go", "Rust",
            "前端工程師", "後端工程師", "全端工程師", "資料工程師",
            "機器學習", "人工智慧", "DevOps", "SRE", "產品經理"
        ]
        
        # 地區代碼
        self.areas = [
            "6001001000",  # 台北市
            "6001002000",  # 新北市
            "6001003000",  # 桃園市
            "6001004000",  # 台中市
            "6001005000",  # 台南市
            "6001006000"   # 高雄市
        ]
    
    def scrape_jobs(self, keyword: str, area: str = "6001001000", pages: int = 2):
        """執行爬蟲任務"""
        try:
            logger.info(f"開始爬取職缺: keyword={keyword}, area={area}, pages={pages}")
            
            jobs = self.scraper.scrape_104(
                keyword=keyword,
                area=area,
                pages=pages
            )
            
            if jobs:
                inserted_count = self.db.insert_jobs(jobs)
                logger.info(f"成功爬取 {len(jobs)} 筆職缺，存入 {inserted_count} 筆")
                
                # 記錄統計資訊
                self.log_statistics(keyword, len(jobs), inserted_count)
            else:
                logger.warning(f"關鍵字 '{keyword}' 沒有找到職缺")
                
        except Exception as e:
            logger.error(f"爬取職缺時發生錯誤: {e}")
    
    def scrape_all_keywords(self):
        """爬取所有預設關鍵字"""
        logger.info("開始執行定期爬蟲任務")
        
        for keyword in self.default_keywords:
            # 為每個關鍵字爬取主要地區（台北市）
            self.scrape_jobs(keyword, "6001001000", 2)
            time.sleep(5)  # 避免請求過於頻繁
        
        logger.info("定期爬蟲任務完成")
    
    def scrape_hot_areas(self):
        """爬取熱門地區的職缺"""
        logger.info("開始爬取熱門地區職缺")
        
        hot_keywords = ["Python", "JavaScript", "前端工程師", "後端工程師"]
        
        for area in self.areas:
            for keyword in hot_keywords:
                self.scrape_jobs(keyword, area, 1)
                time.sleep(3)
        
        logger.info("熱門地區爬蟲任務完成")
    
    def cleanup_old_jobs(self):
        """清理舊的職缺資料"""
        try:
            logger.info("開始清理舊職缺資料")
            deleted_count = self.db.delete_old_jobs(days=30)
            logger.info(f"成功清理 {deleted_count} 筆舊職缺資料")
        except Exception as e:
            logger.error(f"清理舊職缺時發生錯誤: {e}")
    
    def log_statistics(self, keyword: str, scraped_count: int, inserted_count: int):
        """記錄統計資訊"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "keyword": keyword,
            "scraped_count": scraped_count,
            "inserted_count": inserted_count
        }
        
        try:
            with open("scraping_stats.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(stats, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"記錄統計資訊時發生錯誤: {e}")
    
    def get_daily_report(self):
        """生成每日報告"""
        try:
            total_jobs = self.db.get_job_count()
            recent_jobs = self.db.get_recent_jobs(days=1)
            
            report = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_jobs": total_jobs,
                "new_jobs_today": len(recent_jobs),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"每日報告: {report}")
            
            # 儲存報告
            with open("daily_reports.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(report, ensure_ascii=False) + "\n")
                
        except Exception as e:
            logger.error(f"生成每日報告時發生錯誤: {e}")
    
    def setup_schedule(self):
        """設置排程任務"""
        # 每天早上9點執行主要爬蟲任務
        schedule.every().day.at("09:00").do(self.scrape_all_keywords)
        
        # 每天下午3點執行熱門地區爬蟲
        schedule.every().day.at("15:00").do(self.scrape_hot_areas)
        
        # 每週日凌晨2點清理舊資料
        schedule.every().sunday.at("02:00").do(self.cleanup_old_jobs)
        
        # 每天晚上11點生成每日報告
        schedule.every().day.at("23:00").do(self.get_daily_report)
        
        # 每小時執行一次輕量級爬蟲（只爬取熱門關鍵字）
        schedule.every().hour.do(lambda: self.scrape_jobs("Python", "6001001000", 1))
        
        logger.info("排程任務已設置完成")
        logger.info("排程時間:")
        logger.info("  - 每天 09:00: 主要爬蟲任務")
        logger.info("  - 每天 15:00: 熱門地區爬蟲")
        logger.info("  - 每週日 02:00: 清理舊資料")
        logger.info("  - 每天 23:00: 生成每日報告")
        logger.info("  - 每小時: 輕量級爬蟲")
    
    def run(self):
        """運行排程器"""
        logger.info("啟動104職缺爬蟲排程器...")
        
        # 設置排程
        self.setup_schedule()
        
        # 立即執行一次主要爬蟲任務
        logger.info("執行初始爬蟲任務...")
        self.scrape_all_keywords()
        
        # 運行排程
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
        except KeyboardInterrupt:
            logger.info("排程器已停止")
        except Exception as e:
            logger.error(f"排程器運行時發生錯誤: {e}")

def main():
    """主函數"""
    scheduler = JobScheduler()
    scheduler.run()

if __name__ == "__main__":
    main() 