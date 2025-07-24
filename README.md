# 104 職缺搜尋器 - 智能職涯分析系統

一個功能完整的 104 人力銀行職缺爬蟲和分析系統，提供網頁介面、API 服務和自動化排程功能。

## 🌟 主要功能

### 1. 智能爬蟲系統

- **多參數搜尋**: 支援關鍵字、地區、薪資範圍、工作經歷、遠端工作等搜尋條件
- **命令列介面**: 支援命令列參數執行，方便自動化
- **反爬蟲保護**: 內建延遲和隨機化機制，避免被封鎖
- **多格式輸出**: 支援 CSV 和 JSON 格式輸出

### 2. 資料庫管理

- **SQLite 支援**: 輕量級檔案資料庫，適合小型專案
- **PostgreSQL 支援**: 企業級資料庫，適合大型應用
- **自動去重**: 基於職缺 ID 自動避免重複資料
- **資料清理**: 自動清理過期職缺資料

### 3. Web API 服務

- **RESTful API**: 完整的 API 端點設計
- **即時搜尋**: 支援即時爬取和資料庫搜尋
- **統計資訊**: 提供職缺統計和分析資料
- **跨域支援**: 支援前端跨域請求

### 4. 現代化前端

- **響應式設計**: 支援桌面和行動裝置
- **即時搜尋**: 無需重新整理頁面的即時搜尋體驗
- **美觀介面**: 現代化的 UI 設計，提供良好的使用者體驗
- **統計儀表板**: 即時顯示職缺統計資訊

### 5. 自動化排程

- **本地排程**: 使用 Python schedule 套件
- **雲端排程**: GitHub Actions 自動化工作流程
- **智能清理**: 自動清理舊資料和生成報告
- **監控日誌**: 完整的執行日誌記錄

## 🚀 快速開始

### 方法一：本地開發

1. **安裝依賴**

```bash
pip install -r requirements.txt
```

2. **啟動 Web 服務**

```bash
python app.py
```

3. **訪問應用**
   在瀏覽器中打開 `http://localhost:5001`

### 方法二：Docker 部署

1. **使用 Docker Compose**

```bash
docker-compose up -d
```

2. **訪問應用**
   在瀏覽器中打開 `http://localhost:5001`

### 方法三：Cloudflare Workers

1. **安裝 Wrangler CLI**

```bash
npm install -g wrangler
```

2. **設置環境變數**

```bash
wrangler secret put CLOUDFLARE_ACCOUNT_ID
wrangler secret put CLOUDFLARE_API_TOKEN
```

3. **部署 Worker**

```bash
wrangler deploy
```

### 命令列使用

```bash
# 基本搜尋
python scrape_104.py --keyword "Python" --pages 3

# 進階搜尋
python scrape_104.py --keyword "前端工程師" --area "6001001000" --pages 5 --experience "1y" --remote-work

# 指定輸出格式
python scrape_104.py --keyword "資料工程師" --format json --output "data_engineer_jobs.json"
```

### 啟動自動化排程

```bash
python scheduler.py
```

## 📁 專案結構

```
career-analyzer/
├── scrape_104.py          # 核心爬蟲模組
├── database.py            # 資料庫管理模組
├── cloudflare_d1.py       # Cloudflare D1資料庫整合
├── app.py                 # Flask Web API
├── scheduler.py           # 自動化排程腳本
├── start.py               # 啟動腳本（選單介面）
├── examples.py            # 使用範例
├── test_scraper.py        # 測試腳本
├── requirements.txt       # Python依賴
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
├── wrangler.toml          # Cloudflare Workers配置
├── worker.js              # Cloudflare Worker腳本
├── env.example            # 環境變數範例
├── DEPLOYMENT.md          # 部署指南
├── templates/
│   └── index.html        # 前端頁面
├── .github/workflows/
│   ├── scheduler.yml     # GitHub Actions排程
│   └── deploy-pages.yml  # GitHub Pages部署
└── README.md             # 專案說明
```

## 🔧 API 端點

### 搜尋職缺

```
GET /api/search?keyword=Python&area=6001001000&pages=2
```

### 獲取最近職缺

```
GET /api/jobs/recent?days=7
```

### 獲取統計資訊

```
GET /api/jobs/stats
```

### 手動觸發爬蟲

```
POST /api/scrape
Content-Type: application/json

{
  "keyword": "Python",
  "area": "6001001000",
  "pages": 2
}
```

### 清理舊資料

```
POST /api/jobs/cleanup
Content-Type: application/json

{
  "days": 30
}
```

## 🗄️ 資料庫配置

### SQLite (預設)

```python
from database import JobDatabase

db = JobDatabase(db_type="sqlite", db_path="jobs.db")
```

### PostgreSQL

```python
from database import JobDatabase

pg_config = {
    'host': 'localhost',
    'database': 'jobs_db',
    'user': 'postgres',
    'password': 'your_password',
    'port': 5432
}

db = JobDatabase(db_type="postgresql", pg_config=pg_config)
```

### Cloudflare D1 (推薦)

```python
from cloudflare_d1 import create_d1_database

# 設置環境變數
os.environ['CLOUDFLARE_ACCOUNT_ID'] = 'your_account_id'
os.environ['CLOUDFLARE_D1_DATABASE_ID'] = '845a885d-2722-4b74-9f50-e404d02216f3'
os.environ['CLOUDFLARE_API_TOKEN'] = 'your_api_token'

db = create_d1_database()
```

## ⚙️ 配置選項

### 搜尋參數

- `keyword`: 搜尋關鍵字
- `area`: 地區代碼 (6001001000=台北市)
- `pages`: 爬取頁數
- `jobcat`: 職務類別代碼
- `salary_min/salary_max`: 薪資範圍
- `experience`: 工作經歷 (1y, 3y, 5y)
- `remote_work`: 是否可遠端工作

### 地區代碼

- `6001001000`: 台北市
- `6001002000`: 新北市
- `6001003000`: 桃園市
- `6001004000`: 台中市
- `6001005000`: 台南市
- `6001006000`: 高雄市

## 🔄 自動化排程

### 本地排程

系統會自動執行以下任務：

- **每天 09:00**: 主要爬蟲任務
- **每天 15:00**: 熱門地區爬蟲
- **每週日 02:00**: 清理舊資料
- **每天 23:00**: 生成每日報告
- **每小時**: 輕量級爬蟲

### GitHub Actions

- 每天早上 9 點自動執行爬蟲
- 自動提交更新到 GitHub
- 生成爬蟲報告

## 📊 資料分析

系統提供多種資料分析功能：

- 職缺總數統計
- 最近新增職缺數量
- 按地區、職務類別分析
- 薪資範圍分析
- 遠端工作趨勢

## 🛡️ 注意事項

1. **遵守網站條款**: 請遵守 104 人力銀行的使用條款
2. **合理使用**: 避免過於頻繁的請求
3. **資料用途**: 僅供學習和研究使用
4. **法律責任**: 使用者需自行承擔使用風險

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 📄 授權

本專案採用 MIT 授權條款。

## 📞 支援

如有問題或建議，請在 GitHub 上提交 Issue。

---

**免責聲明**: 本專案僅供學習和研究使用，請遵守相關網站的使用條款和法律法規。
