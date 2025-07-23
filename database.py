import sqlite3
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

class JobDatabase:
    def __init__(self, db_type: str = "sqlite", db_path: str = "jobs.db", 
                 pg_config: Optional[Dict] = None):
        """
        初始化資料庫連接
        
        Args:
            db_type: 資料庫類型 ("sqlite" 或 "postgresql")
            db_path: SQLite資料庫檔案路徑
            pg_config: PostgreSQL連接配置
        """
        self.db_type = db_type
        self.db_path = db_path
        self.pg_config = pg_config or {
            'host': 'localhost',
            'database': 'jobs_db',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        }
        
        self.init_database()
    
    def get_connection(self):
        """獲取資料庫連接"""
        if self.db_type == "sqlite":
            return sqlite3.connect(self.db_path)
        elif self.db_type == "postgresql":
            return psycopg2.connect(**self.pg_config)
        else:
            raise ValueError(f"不支援的資料庫類型: {self.db_type}")
    
    def init_database(self):
        """初始化資料庫表格"""
        if self.db_type == "sqlite":
            self._init_sqlite()
        elif self.db_type == "postgresql":
            self._init_postgresql()
    
    def _init_sqlite(self):
        """初始化SQLite資料庫"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
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
        ''')
        
        # 創建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_id ON jobs(job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_name ON jobs(job_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cust_name ON jobs(cust_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)')
        
        conn.commit()
        conn.close()
    
    def _init_postgresql(self):
        """初始化PostgreSQL資料庫"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                job_id VARCHAR(255) UNIQUE,
                job_name VARCHAR(500) NOT NULL,
                cust_name VARCHAR(255),
                job_url TEXT,
                job_addr_no_desc VARCHAR(255),
                salary_desc VARCHAR(255),
                job_detail TEXT,
                appear_date VARCHAR(50),
                job_cat VARCHAR(255),
                job_type VARCHAR(255),
                work_exp VARCHAR(255),
                edu VARCHAR(255),
                skill TEXT,
                benefit TEXT,
                remote_work VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 創建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_id ON jobs(job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_name ON jobs(job_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cust_name ON jobs(cust_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)')
        
        conn.commit()
        conn.close()
    
    def insert_jobs(self, jobs: List[Dict]) -> int:
        """
        插入職缺資料到資料庫
        
        Args:
            jobs: 職缺資料列表
            
        Returns:
            int: 成功插入的記錄數
        """
        if not jobs:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        
        for job in jobs:
            try:
                if self.db_type == "sqlite":
                    cursor.execute('''
                        INSERT OR REPLACE INTO jobs (
                            job_id, job_name, cust_name, job_url, job_addr_no_desc,
                            salary_desc, job_detail, appear_date, job_cat, job_type,
                            work_exp, edu, skill, benefit, remote_work, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
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
                        datetime.now()
                    ))
                else:  # PostgreSQL
                    cursor.execute('''
                        INSERT INTO jobs (
                            job_id, job_name, cust_name, job_url, job_addr_no_desc,
                            salary_desc, job_detail, appear_date, job_cat, job_type,
                            work_exp, edu, skill, benefit, remote_work, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (job_id) DO UPDATE SET
                            job_name = EXCLUDED.job_name,
                            cust_name = EXCLUDED.cust_name,
                            job_url = EXCLUDED.job_url,
                            job_addr_no_desc = EXCLUDED.job_addr_no_desc,
                            salary_desc = EXCLUDED.salary_desc,
                            job_detail = EXCLUDED.job_detail,
                            appear_date = EXCLUDED.appear_date,
                            job_cat = EXCLUDED.job_cat,
                            job_type = EXCLUDED.job_type,
                            work_exp = EXCLUDED.work_exp,
                            edu = EXCLUDED.edu,
                            skill = EXCLUDED.skill,
                            benefit = EXCLUDED.benefit,
                            remote_work = EXCLUDED.remote_work,
                            updated_at = EXCLUDED.updated_at
                    ''', (
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
                        datetime.now()
                    ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"插入職缺資料時發生錯誤: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"成功插入 {inserted_count} 筆職缺資料")
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
        conn = self.get_connection()
        
        if self.db_type == "sqlite":
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 構建查詢條件
        conditions = []
        params = []
        
        if keyword:
            conditions.append("job_name LIKE ?" if self.db_type == "sqlite" else "job_name ILIKE %s")
            params.append(f"%{keyword}%")
        
        if company:
            conditions.append("cust_name LIKE ?" if self.db_type == "sqlite" else "cust_name ILIKE %s")
            params.append(f"%{company}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f'''
            SELECT * FROM jobs 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT {limit} OFFSET {offset}
        '''
        
        cursor.execute(query, params)
        
        if self.db_type == "sqlite":
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_job_count(self) -> int:
        """獲取職缺總數"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_recent_jobs(self, days: int = 7) -> List[Dict]:
        """獲取最近幾天的職缺"""
        conn = self.get_connection()
        
        if self.db_type == "sqlite":
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM jobs 
                WHERE created_at >= datetime('now', '-{} days')
                ORDER BY created_at DESC
            '''.format(days))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM jobs 
                WHERE created_at >= CURRENT_DATE - INTERVAL '{} days'
                ORDER BY created_at DESC
            '''.format(days))
            
            results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def delete_old_jobs(self, days: int = 30) -> int:
        """刪除舊的職缺資料"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.db_type == "sqlite":
            cursor.execute('''
                DELETE FROM jobs 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
        else:
            cursor.execute('''
                DELETE FROM jobs 
                WHERE created_at < CURRENT_DATE - INTERVAL '{} days'
            '''.format(days))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"刪除了 {deleted_count} 筆舊職缺資料")
        return deleted_count 