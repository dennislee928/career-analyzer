from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scrape_104 import Job104Scraper
from database import JobDatabase
import os
import logging
from datetime import datetime

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化爬蟲和資料庫
scraper = Job104Scraper()
db = JobDatabase(db_type="sqlite", db_path="jobs.db")

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search_jobs():
    """搜尋職缺API"""
    try:
        # 從請求參數中獲取搜尋條件
        keyword = request.args.get('keyword', default='', type=str)
        area = request.args.get('area', default='6001001000', type=str)
        pages = request.args.get('pages', default=1, type=int)
        jobcat = request.args.get('jobcat', default=None, type=str)
        salary_min = request.args.get('salary_min', default=None, type=int)
        salary_max = request.args.get('salary_max', default=None, type=int)
        experience = request.args.get('experience', default=None, type=str)
        remote_work = request.args.get('remote_work', default=False, type=bool)
        
        # 檢查是否要從資料庫搜尋還是重新爬取
        use_database = request.args.get('use_database', default='true', type=str).lower() == 'true'
        
        if use_database and keyword:
            # 從資料庫搜尋
            jobs = db.search_jobs(keyword=keyword, limit=50)
            source = "database"
        else:
            # 重新爬取資料
            logger.info(f"開始爬取職缺: keyword={keyword}, area={area}, pages={pages}")
            
            jobs = scraper.scrape_104(
                keyword=keyword,
                area=area,
                pages=pages,
                jobcat=jobcat,
                salary_min=salary_min,
                salary_max=salary_max,
                experience=experience,
                remote_work=remote_work
            )
            
            # 將爬取的資料存入資料庫
            if jobs:
                db.insert_jobs(jobs)
            
            source = "scraper"
        
        return jsonify({
            "status": "success",
            "source": source,
            "count": len(jobs),
            "data": jobs,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"搜尋職缺時發生錯誤: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/jobs/recent', methods=['GET'])
def get_recent_jobs():
    """獲取最近的職缺"""
    try:
        days = request.args.get('days', default=7, type=int)
        jobs = db.get_recent_jobs(days=days)
        
        return jsonify({
            "status": "success",
            "count": len(jobs),
            "data": jobs
        })
        
    except Exception as e:
        logger.error(f"獲取最近職缺時發生錯誤: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/jobs/stats', methods=['GET'])
def get_job_stats():
    """獲取職缺統計資訊"""
    try:
        total_count = db.get_job_count()
        recent_jobs = db.get_recent_jobs(days=7)
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_jobs": total_count,
                "recent_jobs": len(recent_jobs),
                "last_updated": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"獲取統計資訊時發生錯誤: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/jobs/cleanup', methods=['POST'])
def cleanup_old_jobs():
    """清理舊的職缺資料"""
    try:
        days = request.json.get('days', 30) if request.is_json else 30
        deleted_count = db.delete_old_jobs(days=days)
        
        return jsonify({
            "status": "success",
            "deleted_count": deleted_count,
            "message": f"成功刪除 {deleted_count} 筆舊職缺資料"
        })
        
    except Exception as e:
        logger.error(f"清理舊職缺時發生錯誤: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_jobs():
    """手動觸發爬蟲"""
    try:
        data = request.get_json() or {}
        
        keyword = data.get('keyword', 'Python')
        area = data.get('area', '6001001000')
        pages = data.get('pages', 1)
        jobcat = data.get('jobcat')
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        experience = data.get('experience')
        remote_work = data.get('remote_work', False)
        
        logger.info(f"手動觸發爬蟲: keyword={keyword}, pages={pages}")
        
        jobs = scraper.scrape_104(
            keyword=keyword,
            area=area,
            pages=pages,
            jobcat=jobcat,
            salary_min=salary_min,
            salary_max=salary_max,
            experience=experience,
            remote_work=remote_work
        )
        
        # 存入資料庫
        if jobs:
            inserted_count = db.insert_jobs(jobs)
        else:
            inserted_count = 0
        
        return jsonify({
            "status": "success",
            "scraped_count": len(jobs),
            "inserted_count": inserted_count,
            "message": f"成功爬取 {len(jobs)} 筆職缺，存入 {inserted_count} 筆"
        })
        
    except Exception as e:
        logger.error(f"手動爬蟲時發生錯誤: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "API端點不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "伺服器內部錯誤"
    }), 500

if __name__ == '__main__':
    # 確保templates目錄存在
    os.makedirs('templates', exist_ok=True)
    
    print("啟動104職缺搜尋API伺服器...")
    print("API端點:")
    print("  GET  /api/search - 搜尋職缺")
    print("  GET  /api/jobs/recent - 獲取最近職缺")
    print("  GET  /api/jobs/stats - 獲取統計資訊")
    print("  POST /api/jobs/cleanup - 清理舊職缺")
    print("  POST /api/scrape - 手動觸發爬蟲")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 