#!/usr/bin/env python3
"""
Cloudflare D1 資料庫管理腳本
用於初始化、備份、維護和查詢D1資料庫
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from cloudflare_d1 import create_d1_database, CloudflareD1Database

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """初始化D1資料庫"""
    try:
        db = create_d1_database()
        logger.info("D1資料庫連接成功")
        
        # 讀取初始化SQL腳本
        with open('init_d1_database.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 執行SQL腳本
        statements = sql_script.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    db.execute_query(statement)
                    logger.info(f"執行SQL: {statement[:50]}...")
                except Exception as e:
                    logger.warning(f"執行SQL時發生警告: {e}")
        
        logger.info("D1資料庫初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"D1資料庫初始化失敗: {e}")
        return False

def backup_database(output_file=None):
    """備份D1資料庫"""
    try:
        db = create_d1_database()
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'd1_backup_{timestamp}.json'
        
        # 獲取所有表格
        tables_result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = []
        if 'results' in tables_result:
            for row in tables_result['results']:
                if 'values' in row and row['values']:
                    tables.append(row['values'][0])
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'tables': {}
        }
        
        # 備份每個表格的資料
        for table in tables:
            try:
                result = db.execute_query(f"SELECT * FROM {table}")
                backup_data['tables'][table] = result.get('results', [])
                logger.info(f"備份表格 {table}: {len(result.get('results', []))} 筆記錄")
            except Exception as e:
                logger.warning(f"備份表格 {table} 時發生錯誤: {e}")
        
        # 寫入備份檔案
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"備份完成: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"備份失敗: {e}")
        return False

def restore_database(backup_file):
    """從備份檔案還原D1資料庫"""
    try:
        db = create_d1_database()
        
        # 讀取備份檔案
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        logger.info(f"開始還原備份: {backup_file}")
        
        # 還原每個表格的資料
        for table_name, records in backup_data['tables'].items():
            if table_name == 'jobs':
                # 使用批量插入
                for record in records:
                    try:
                        if 'values' in record and 'columns' in backup_data['tables'][table_name]:
                            columns = backup_data['tables'][table_name]['columns']
                            values = record['values']
                            
                            # 構建INSERT語句
                            placeholders = ', '.join(['?' for _ in values])
                            column_names = ', '.join(columns)
                            sql = f"INSERT OR REPLACE INTO {table_name} ({column_names}) VALUES ({placeholders})"
                            
                            db.execute_query(sql, values)
                    except Exception as e:
                        logger.warning(f"還原記錄時發生錯誤: {e}")
        
        logger.info("還原完成")
        return True
        
    except Exception as e:
        logger.error(f"還原失敗: {e}")
        return False

def show_stats():
    """顯示資料庫統計資訊"""
    try:
        db = create_d1_database()
        
        # 獲取基本統計
        total_jobs = db.get_job_count()
        recent_jobs = db.get_recent_jobs(days=7)
        
        # 獲取資料庫資訊
        db_info = db.get_database_info()
        
        print("\n=== D1 資料庫統計資訊 ===")
        print(f"資料庫ID: {db_info.get('database_id', 'N/A')}")
        print(f"表格數量: {len(db_info.get('tables', []))}")
        print(f"職缺總數: {total_jobs}")
        print(f"最近7天職缺: {len(recent_jobs)}")
        print(f"最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 顯示表格列表
        print(f"\n表格列表: {', '.join(db_info.get('tables', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"獲取統計資訊失敗: {e}")
        return False

def cleanup_old_data(days=30):
    """清理舊資料"""
    try:
        db = create_d1_database()
        
        # 清理舊職缺
        deleted_jobs = db.delete_old_jobs(days)
        
        # 清理舊統計資料
        sql = f"DELETE FROM scraping_stats WHERE created_at < datetime('now', '-{days} days')"
        result = db.execute_query(sql)
        deleted_stats = result.get('meta', {}).get('changes', 0)
        
        print(f"\n=== 清理完成 ===")
        print(f"刪除舊職缺: {deleted_jobs} 筆")
        print(f"刪除舊統計: {deleted_stats} 筆")
        print(f"清理天數: {days} 天")
        
        return True
        
    except Exception as e:
        logger.error(f"清理失敗: {e}")
        return False

def search_jobs(keyword, limit=10):
    """搜尋職缺"""
    try:
        db = create_d1_database()
        jobs = db.search_jobs(keyword=keyword, limit=limit)
        
        print(f"\n=== 搜尋結果: '{keyword}' ===")
        print(f"找到 {len(jobs)} 筆職缺")
        
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.get('job_name', 'N/A')}")
            print(f"   公司: {job.get('cust_name', 'N/A')}")
            print(f"   地點: {job.get('job_addr_no_desc', 'N/A')}")
            print(f"   薪資: {job.get('salary_desc', 'N/A')}")
            print(f"   更新: {job.get('created_at', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"搜尋失敗: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Cloudflare D1 資料庫管理工具')
    parser.add_argument('action', choices=[
        'init', 'backup', 'restore', 'stats', 'cleanup', 'search'
    ], help='執行動作')
    
    parser.add_argument('--output', '-o', help='備份檔案路徑')
    parser.add_argument('--input', '-i', help='還原檔案路徑')
    parser.add_argument('--days', '-d', type=int, default=30, help='清理天數')
    parser.add_argument('--keyword', '-k', help='搜尋關鍵字')
    parser.add_argument('--limit', '-l', type=int, default=10, help='搜尋結果限制')
    
    args = parser.parse_args()
    
    # 檢查環境變數
    required_envs = ['CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_D1_DATABASE_ID', 'CLOUDFLARE_API_TOKEN']
    missing_envs = [env for env in required_envs if not os.getenv(env)]
    
    if missing_envs:
        print(f"錯誤: 缺少必要的環境變數: {', '.join(missing_envs)}")
        print("請設置以下環境變數:")
        for env in missing_envs:
            print(f"  export {env}=your_value")
        sys.exit(1)
    
    # 執行動作
    success = False
    
    if args.action == 'init':
        success = init_database()
    elif args.action == 'backup':
        success = backup_database(args.output)
    elif args.action == 'restore':
        if not args.input:
            print("錯誤: 還原需要指定輸入檔案 (--input)")
            sys.exit(1)
        success = restore_database(args.input)
    elif args.action == 'stats':
        success = show_stats()
    elif args.action == 'cleanup':
        success = cleanup_old_data(args.days)
    elif args.action == 'search':
        if not args.keyword:
            print("錯誤: 搜尋需要指定關鍵字 (--keyword)")
            sys.exit(1)
        success = search_jobs(args.keyword, args.limit)
    
    if success:
        print("\n操作完成!")
        sys.exit(0)
    else:
        print("\n操作失敗!")
        sys.exit(1)

if __name__ == '__main__':
    main() 