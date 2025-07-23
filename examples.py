#!/usr/bin/env python3
"""
104職缺搜尋器使用範例
展示如何使用各個模組的功能
"""

from scrape_104 import Job104Scraper
from database import JobDatabase
import json
import time

def example_basic_scraping():
    """基本爬蟲範例"""
    print("=== 基本爬蟲範例 ===")
    
    scraper = Job104Scraper()
    
    # 搜尋Python相關職缺
    jobs = scraper.scrape_104(
        keyword="Python",
        area="6001001000",  # 台北市
        pages=2
    )
    
    print(f"找到 {len(jobs)} 筆Python職缺")
    
    # 顯示前3筆職缺
    for i, job in enumerate(jobs[:3]):
        print(f"\n職缺 {i+1}:")
        print(f"  職位: {job['jobName']}")
        print(f"  公司: {job['custName']}")
        print(f"  地區: {job['jobAddrNoDesc']}")
        print(f"  薪資: {job['salaryDesc']}")

def example_advanced_scraping():
    """進階爬蟲範例"""
    print("\n=== 進階爬蟲範例 ===")
    
    scraper = Job104Scraper()
    
    # 搜尋前端工程師，要求1年以上經驗，可遠端工作
    jobs = scraper.scrape_104(
        keyword="前端工程師",
        area="6001001000",
        pages=1,
        experience="1y",
        remote_work=True
    )
    
    print(f"找到 {len(jobs)} 筆符合條件的前端工程師職缺")
    
    # 顯示遠端工作職缺
    remote_jobs = [job for job in jobs if job.get('remoteWork')]
    print(f"其中 {len(remote_jobs)} 筆可遠端工作")

def example_database_operations():
    """資料庫操作範例"""
    print("\n=== 資料庫操作範例 ===")
    
    # 初始化資料庫
    db = JobDatabase(db_type="sqlite", db_path="example.db")
    
    # 爬取一些職缺資料
    scraper = Job104Scraper()
    jobs = scraper.scrape_104(keyword="JavaScript", pages=1)
    
    if jobs:
        # 存入資料庫
        inserted_count = db.insert_jobs(jobs)
        print(f"成功存入 {inserted_count} 筆JavaScript職缺")
        
        # 搜尋資料庫中的職缺
        search_results = db.search_jobs(keyword="JavaScript", limit=5)
        print(f"從資料庫中找到 {len(search_results)} 筆JavaScript職缺")
        
        # 顯示統計資訊
        total_count = db.get_job_count()
        print(f"資料庫總共有 {total_count} 筆職缺")
        
        # 獲取最近職缺
        recent_jobs = db.get_recent_jobs(days=1)
        print(f"最近1天新增 {len(recent_jobs)} 筆職缺")

def example_multiple_keywords():
    """多關鍵字搜尋範例"""
    print("\n=== 多關鍵字搜尋範例 ===")
    
    scraper = Job104Scraper()
    keywords = ["Python", "JavaScript", "Java", "Go"]
    
    all_jobs = []
    
    for keyword in keywords:
        print(f"搜尋關鍵字: {keyword}")
        jobs = scraper.scrape_104(keyword=keyword, pages=1)
        all_jobs.extend(jobs)
        print(f"  找到 {len(jobs)} 筆職缺")
        time.sleep(2)  # 避免請求過於頻繁
    
    print(f"\n總共找到 {len(all_jobs)} 筆職缺")
    
    # 按公司統計
    companies = {}
    for job in all_jobs:
        company = job.get('custName', '未知公司')
        companies[company] = companies.get(company, 0) + 1
    
    print("\n熱門公司 (職缺數量):")
    sorted_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)
    for company, count in sorted_companies[:5]:
        print(f"  {company}: {count} 筆")

def example_salary_analysis():
    """薪資分析範例"""
    print("\n=== 薪資分析範例 ===")
    
    scraper = Job104Scraper()
    
    # 搜尋不同薪資範圍的職缺
    salary_ranges = [
        (30000, 50000, "3-5萬"),
        (50000, 80000, "5-8萬"),
        (80000, 120000, "8-12萬")
    ]
    
    for min_salary, max_salary, label in salary_ranges:
        jobs = scraper.scrape_104(
            keyword="工程師",
            area="6001001000",
            pages=1,
            salary_min=min_salary,
            salary_max=max_salary
        )
        
        print(f"{label}薪資範圍: 找到 {len(jobs)} 筆職缺")
        
        # 顯示薪資資訊
        for job in jobs[:2]:  # 只顯示前2筆
            print(f"  - {job['jobName']}: {job.get('salaryDesc', '薪資未公開')}")
        
        time.sleep(2)

def example_area_comparison():
    """地區比較範例"""
    print("\n=== 地區比較範例 ===")
    
    scraper = Job104Scraper()
    areas = {
        "6001001000": "台北市",
        "6001002000": "新北市",
        "6001004000": "台中市",
        "6001006000": "高雄市"
    }
    
    area_stats = {}
    
    for area_code, area_name in areas.items():
        print(f"搜尋 {area_name} 的Python職缺...")
        jobs = scraper.scrape_104(
            keyword="Python",
            area=area_code,
            pages=1
        )
        
        area_stats[area_name] = len(jobs)
        print(f"  {area_name}: {len(jobs)} 筆職缺")
        time.sleep(2)
    
    print("\n地區職缺數量比較:")
    for area, count in sorted(area_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {area}: {count} 筆")

def example_data_export():
    """資料匯出範例"""
    print("\n=== 資料匯出範例 ===")
    
    scraper = Job104Scraper()
    
    # 爬取資料
    jobs = scraper.scrape_104(keyword="資料工程師", pages=2)
    
    if jobs:
        # 儲存為CSV
        csv_file = scraper.save_to_csv(jobs, "data_engineer_jobs.csv")
        print(f"CSV檔案已儲存: {csv_file}")
        
        # 儲存為JSON
        json_file = scraper.save_to_json(jobs, "data_engineer_jobs.json")
        print(f"JSON檔案已儲存: {json_file}")
        
        # 顯示資料結構
        print(f"\n職缺資料包含以下欄位:")
        if jobs:
            for key in jobs[0].keys():
                print(f"  - {key}")

def main():
    """執行所有範例"""
    print("104職缺搜尋器使用範例")
    print("=" * 50)
    
    try:
        example_basic_scraping()
        example_advanced_scraping()
        example_database_operations()
        example_multiple_keywords()
        example_salary_analysis()
        example_area_comparison()
        example_data_export()
        
        print("\n=== 所有範例執行完成 ===")
        print("您可以查看生成的檔案:")
        print("  - example.db (SQLite資料庫)")
        print("  - data_engineer_jobs.csv")
        print("  - data_engineer_jobs.json")
        
    except Exception as e:
        print(f"執行範例時發生錯誤: {e}")

if __name__ == "__main__":
    main() 