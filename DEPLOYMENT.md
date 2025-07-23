# 部署指南

本文件說明如何部署 104 職缺搜尋器到不同的平台。

## 🐳 Docker 部署

### 本地 Docker 部署

1. **構建 Docker 映像**

```bash
docker build -t 104-job-scraper .
```

2. **使用 Docker Compose 啟動**

```bash
docker-compose up -d
```

3. **查看日誌**

```bash
docker-compose logs -f
```

4. **停止服務**

```bash
docker-compose down
```

### 生產環境 Docker 部署

1. **設置環境變數**

```bash
cp env.example .env
# 編輯.env檔案，設置生產環境配置
```

2. **使用 Docker Compose 部署**

```bash
docker-compose -f docker-compose.yml up -d
```

3. **設置反向代理（Nginx 範例）**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🌐 GitHub Pages 部署

### 自動部署

1. **啟用 GitHub Pages**

   - 前往 Repository Settings > Pages
   - Source 選擇"GitHub Actions"

2. **推送代碼觸發部署**

```bash
git add .
git commit -m "Update for GitHub Pages deployment"
git push origin main
```

3. **查看部署狀態**
   - 前往 Actions 標籤頁查看部署進度
   - 部署完成後，網站將在 `https://your-username.github.io/your-repo-name` 可用

### 手動部署

1. **構建靜態檔案**

```bash
mkdir -p docs
cp templates/index.html docs/
# 修改API URL為生產環境地址
sed -i 's|http://127.0.0.1:5001|https://your-api-domain.com|g' docs/index.html
```

2. **推送到 gh-pages 分支**

```bash
git add docs/
git commit -m "Add static files for GitHub Pages"
git push origin main
```

## ☁️ Cloudflare D1 部署

### 1. 設置 Cloudflare D1 資料庫

1. **安裝 Wrangler CLI**

```bash
npm install -g wrangler
```

2. **登入 Cloudflare**

```bash
wrangler login
```

3. **創建 D1 資料庫**

```bash
wrangler d1 create 104-jobs
```

4. **更新 wrangler.toml**

```toml
[[d1_databases]]
binding = "DB"
database_name = "104-jobs"
database_id = "845a885d-2722-4b74-9f50-e404d02216f3"
```

### 2. 部署 Cloudflare Worker

1. **設置環境變數**

```bash
wrangler secret put CLOUDFLARE_ACCOUNT_ID
wrangler secret put CLOUDFLARE_API_TOKEN
```

2. **部署 Worker**

```bash
wrangler deploy
```

3. **查看部署狀態**

```bash
wrangler tail
```

### 3. 設置自定義域名

1. **在 Cloudflare Dashboard 中添加域名**
2. **設置 DNS 記錄指向 Worker**
3. **配置 SSL 證書**

## 🔧 環境變數配置

### 本地開發

```bash
cp env.example .env
# 編輯.env檔案
```

### Docker 環境

```bash
# 在docker-compose.yml中設置
environment:
  - DB_TYPE=d1
  - CLOUDFLARE_ACCOUNT_ID=your_account_id
  - CLOUDFLARE_D1_DATABASE_ID=845a885d-2722-4b74-9f50-e404d02216f3
  - CLOUDFLARE_API_TOKEN=your_api_token
```

### GitHub Actions

在 Repository Settings > Secrets 中添加：

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_D1_DATABASE_ID`

## 📊 監控和日誌

### 本地監控

```bash
# 查看應用日誌
tail -f app.log

# 查看Docker日誌
docker-compose logs -f

# 查看Worker日誌
wrangler tail
```

### 生產環境監控

- **Cloudflare Analytics**: 查看 Worker 執行統計
- **GitHub Actions**: 查看部署和排程任務狀態
- **自定義監控**: 設置健康檢查端點

## 🔒 安全配置

### 1. API Token 權限

確保 Cloudflare API Token 具有以下權限：

- `D1:Edit`
- `Workers:Edit`
- `Zone:Read`

### 2. 環境變數安全

- 不要在代碼中硬編碼敏感資訊
- 使用環境變數或密鑰管理服務
- 定期輪換 API Token

### 3. 網路安全

- 設置適當的 CORS 策略
- 使用 HTTPS
- 考慮添加 API 速率限制

## 🚀 性能優化

### 1. 資料庫優化

- 定期清理舊資料
- 創建適當的索引
- 使用連接池

### 2. 快取策略

- 實作 Redis 快取
- 使用 CDN 快取靜態資源
- 設置適當的快取標頭

### 3. 監控指標

- 響應時間
- 錯誤率
- 資料庫查詢性能
- 記憶體使用量

## 🔄 更新和維護

### 1. 代碼更新

```bash
# 拉取最新代碼
git pull origin main

# 重新部署
docker-compose down
docker-compose up -d --build
```

### 2. 資料庫遷移

```bash
# 備份資料
wrangler d1 execute 104-jobs --command "SELECT * FROM jobs" --output backup.json

# 執行遷移
wrangler d1 execute 104-jobs --file migration.sql
```

### 3. 監控和警報

- 設置錯誤警報
- 監控系統資源
- 定期檢查日誌

## 📞 故障排除

### 常見問題

1. **Docker 容器無法啟動**

   - 檢查端口是否被佔用
   - 確認環境變數設置正確
   - 查看 Docker 日誌

2. **D1 資料庫連接失敗**

   - 確認 API Token 權限
   - 檢查資料庫 ID 是否正確
   - 驗證網路連接

3. **GitHub Pages 部署失敗**

   - 檢查 Actions 日誌
   - 確認檔案路徑正確
   - 驗證權限設置

4. **Worker 執行錯誤**
   - 查看 Worker 日誌
   - 檢查 D1 資料庫狀態
   - 驗證 API 端點

### 獲取幫助

- 查看專案 README.md
- 檢查 GitHub Issues
- 查看 Cloudflare 文檔
- 聯繫開發團隊
