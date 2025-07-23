"""
Cloudflare D1 資料庫整合模組
用於連接和管理Cloudflare D1 SQLite資料庫
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class CloudflareD1Database:
    """Cloudflare D1 資料庫管理類別"""
    
    def __init__(self, account_id: str, database_id: str, api_token: str):
        """
        初始化D1資料庫連接
        
        Args:
            account_id: Cloudflare帳戶ID
            database_id: D1資料庫ID
            api_token: Cloudflare API Token
        """
        self.account_id = account_id
        self.database_id = database_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}"
        
        # 設置請求標頭
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # 初始化資料庫表格
        self.init_database()
    
    def init_database(self):
        """初始化資料庫表格"""
        try:
            # 創建jobs表格
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                job_name TEXT NOT NULL,
                cust_name TEXT,
                job_url TEXT,
                job_addr_no_desc TEXT,
                salary_desc TEXT,
                job_detail TEXT,
                appear_date TEXT,
                job_cat TEXT,
                job_type TEXT,
                work_exp TEXT,
                edu TEXT,
                skill TEXT,
                benefit TEXT,
                remote_work TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
            
            self.execute_query(create_table_sql)
            
            # 創建索引
            index_sqls = [
                'CREATE INDEX IF NOT EXISTS idx_job_id ON jobs(job_id)',
                'CREATE INDEX IF NOT EXISTS idx_job_name ON jobs(job_name)',
                'CREATE INDEX IF NOT EXISTS idx_cust_name ON jobs(cust_name)',
                'CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)'
            ]
            
            for index_sql in index_sqls:
                try:
                    self.execute_query(index_sql)
                except Exception as e:
                    logger.warning(f"創建索引時發生警告: {e}")
                    
            logger.info("D1資料庫初始化完成")
            
        except Exception as e:
            logger.error(f"D1資料庫初始化失敗: {e}")
            raise
    
    def execute_query(self, sql: str, params: List = None) -> Dict:
        """
        執行SQL查詢
        
        Args:
            sql: SQL查詢語句
            params: 查詢參數
            
        Returns:
            Dict: 查詢結果
        """
        try:
            payload = {
                'sql': sql
            }
            
            if params:
                payload['params'] = params
            
            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                raise Exception(f"D1查詢失敗: {result.get('errors', '未知錯誤')}")
            
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f"執行D1查詢時發生錯誤: {e}")
            raise
    
    def insert_jobs(self, jobs: List[Dict]) -> int:
        """
        插入職缺資料到D1資料庫
        
        Args:
            jobs: 職缺資料列表
            
        Returns:
            int: 成功插入的記錄數
        """
        if not jobs:
            return 0
        
        inserted_count = 0
        
        for job in jobs:
            try:
                # 使用UPSERT語法（INSERT OR REPLACE）
                sql = '''
                INSERT OR REPLACE INTO jobs (
                    job_id, job_name, cust_name, job_url, job_addr_no_desc,
                    salary_desc, job_detail, appear_date, job_cat, job_type,
                    work_exp, edu, skill, benefit, remote_work, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                params = [
                    job.get('jobId', ''),
                    job.get('jobName', ''),
                    job.get('custName', ''),
                    job.get('jobUrl', ''),
                    job.get('jobAddrNoDesc', ''),
                    job.get('salaryDesc', ''),
                    job.get('jobDetail', ''),
                    job.get('appearDate', ''),
                    job.get('jobCat', ''),
                    job.get('jobType', ''),
                    job.get('workExp', ''),
                    job.get('edu', ''),
                    job.get('skill', ''),
                    job.get('benefit', ''),
                    job.get('remoteWork', ''),
                    datetime.now().isoformat()
                ]
                
                result = self.execute_query(sql, params)
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"插入職缺資料時發生錯誤: {e}")
                continue
        
        logger.info(f"成功插入 {inserted_count} 筆職缺資料到D1")
        return inserted_count
    
    def search_jobs(self, keyword: str = None, company: str = None, 
                   limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        搜尋職缺資料
        
        Args:
            keyword: 職缺名稱關鍵字
            company: 公司名稱關鍵字
            limit: 限制返回記錄數
            offset: 偏移量
            
        Returns:
            List[Dict]: 職缺資料列表
        """
        try:
            # 構建查詢條件
            conditions = []
            params = []
            
            if keyword:
                conditions.append("job_name LIKE ?")
                params.append(f"%{keyword}%")
            
            if company:
                conditions.append("cust_name LIKE ?")
                params.append(f"%{company}%")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            sql = f'''
            SELECT * FROM jobs 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT {limit} OFFSET {offset}
            '''
            
            result = self.execute_query(sql, params)
            
            # 轉換結果格式
            jobs = []
            if 'results' in result:
                for row in result['results']:
                    job = {}
                    if 'columns' in result and 'values' in row:
                        for i, column in enumerate(result['columns']):
                            if i < len(row['values']):
                                job[column] = row['values'][i]
                    jobs.append(job)
            
            return jobs
            
        except Exception as e:
            logger.error(f"搜尋職缺時發生錯誤: {e}")
            return []
    
    def get_job_count(self) -> int:
        """獲取職缺總數"""
        try:
            sql = "SELECT COUNT(*) as count FROM jobs"
            result = self.execute_query(sql)
            
            if 'results' in result and result['results']:
                return result['results'][0].get('values', [0])[0]
            
            return 0
            
        except Exception as e:
            logger.error(f"獲取職缺總數時發生錯誤: {e}")
            return 0
    
    def get_recent_jobs(self, days: int = 7) -> List[Dict]:
        """獲取最近幾天的職缺"""
        try:
            sql = '''
            SELECT * FROM jobs 
            WHERE created_at >= datetime('now', '-{} days')
            ORDER BY created_at DESC
            '''.format(days)
            
            result = self.execute_query(sql)
            
            # 轉換結果格式
            jobs = []
            if 'results' in result:
                for row in result['results']:
                    job = {}
                    if 'columns' in result and 'values' in row:
                        for i, column in enumerate(result['columns']):
                            if i < len(row['values']):
                                job[column] = row['values'][i]
                    jobs.append(job)
            
            return jobs
            
        except Exception as e:
            logger.error(f"獲取最近職缺時發生錯誤: {e}")
            return []
    
    def delete_old_jobs(self, days: int = 30) -> int:
        """刪除舊的職缺資料"""
        try:
            sql = '''
            DELETE FROM jobs 
            WHERE created_at < datetime('now', '-{} days')
            '''.format(days)
            
            result = self.execute_query(sql)
            
            # 獲取刪除的記錄數
            deleted_count = result.get('meta', {}).get('changes', 0)
            
            logger.info(f"成功刪除 {deleted_count} 筆舊職缺資料")
            return deleted_count
            
        except Exception as e:
            logger.error(f"刪除舊職缺時發生錯誤: {e}")
            return 0
    
    def get_database_info(self) -> Dict:
        """獲取資料庫資訊"""
        try:
            sql = "SELECT name FROM sqlite_master WHERE type='table'"
            result = self.execute_query(sql)
            
            tables = []
            if 'results' in result:
                for row in result['results']:
                    if 'values' in row and row['values']:
                        tables.append(row['values'][0])
            
            return {
                'database_id': self.database_id,
                'tables': tables,
                'total_jobs': self.get_job_count(),
                'recent_jobs': len(self.get_recent_jobs(days=1))
            }
            
        except Exception as e:
            logger.error(f"獲取資料庫資訊時發生錯誤: {e}")
            return {}

# 環境變數配置
def get_d1_config():
    """從環境變數獲取D1配置"""
    return {
        'account_id': os.getenv('CLOUDFLARE_ACCOUNT_ID'),
        'database_id': os.getenv('CLOUDFLARE_D1_DATABASE_ID', '845a885d-2722-4b74-9f50-e404d02216f3'),
        'api_token': os.getenv('CLOUDFLARE_API_TOKEN')
    }

def create_d1_database():
    """創建D1資料庫實例"""
    config = get_d1_config()
    
    if not all([config['account_id'], config['database_id'], config['api_token']]):
        raise ValueError("缺少必要的D1配置環境變數")
    
    return CloudflareD1Database(
        account_id=config['account_id'],
        database_id=config['database_id'],
        api_token=config['api_token']
    ) 