-- Cloudflare D1 資料庫初始化腳本
-- 用於創建jobs表格和相關索引

-- 創建jobs表格
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
);

-- 創建索引以提升查詢性能
CREATE INDEX IF NOT EXISTS idx_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_job_name ON jobs(job_name);
CREATE INDEX IF NOT EXISTS idx_cust_name ON jobs(cust_name);
CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_updated_at ON jobs(updated_at);
CREATE INDEX IF NOT EXISTS idx_job_cat ON jobs(job_cat);
CREATE INDEX IF NOT EXISTS idx_job_type ON jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_work_exp ON jobs(work_exp);

-- 創建複合索引
CREATE INDEX IF NOT EXISTS idx_job_name_cust ON jobs(job_name, cust_name);
CREATE INDEX IF NOT EXISTS idx_created_at_job_cat ON jobs(created_at, job_cat);

-- 創建統計表格
CREATE TABLE IF NOT EXISTS scraping_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    area TEXT,
    pages INTEGER,
    jobs_found INTEGER,
    jobs_inserted INTEGER,
    execution_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引
CREATE INDEX IF NOT EXISTS idx_stats_keyword ON scraping_stats(keyword);
CREATE INDEX IF NOT EXISTS idx_stats_created_at ON scraping_stats(created_at);

-- 插入一些測試資料（可選）
INSERT OR IGNORE INTO jobs (
    job_id, job_name, cust_name, job_url, job_addr_no_desc,
    salary_desc, job_detail, appear_date, job_cat, job_type,
    work_exp, edu, skill, benefit, remote_work
) VALUES (
    'test_001',
    'Python 後端工程師',
    '測試公司',
    'https://www.104.com.tw/job/test_001',
    '台北市信義區',
    '月薪 60,000-80,000 元',
    '負責後端API開發和資料庫設計',
    '2024-01-01',
    '資訊軟體系統類',
    '全職',
    '3年以上',
    '大學',
    'Python, Django, PostgreSQL',
    '年終獎金、健保、勞保',
    '可'
);

-- 創建視圖用於常用查詢
CREATE VIEW IF NOT EXISTS recent_jobs_view AS
SELECT 
    job_id,
    job_name,
    cust_name,
    job_url,
    job_addr_no_desc,
    salary_desc,
    created_at
FROM jobs 
WHERE created_at >= datetime('now', '-7 days')
ORDER BY created_at DESC;

-- 創建視圖用於統計
CREATE VIEW IF NOT EXISTS job_stats_view AS
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN created_at >= datetime('now', '-1 day') THEN 1 END) as today_jobs,
    COUNT(CASE WHEN created_at >= datetime('now', '-7 days') THEN 1 END) as week_jobs,
    COUNT(CASE WHEN created_at >= datetime('now', '-30 days') THEN 1 END) as month_jobs
FROM jobs; 