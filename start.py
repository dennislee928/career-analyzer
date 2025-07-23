#!/usr/bin/env python3
"""
104職缺搜尋器啟動腳本
提供簡單的選單介面來啟動不同功能
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_banner():
    """顯示歡迎橫幅"""
    print("=" * 60)
    print("🎯 104 職缺搜尋器 - 智能職涯分析系統")
    print("=" * 60)
    print("一個功能完整的104人力銀行職缺爬蟲和分析系統")
    print("提供網頁介面、API服務和自動化排程功能")
    print("=" * 60)

def check_dependencies():
    """檢查依賴套件"""
    print("🔍 檢查依賴套件...")
    
    required_packages = [
        'flask', 'requests', 'pandas', 'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (未安裝)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下套件: {', '.join(missing_packages)}")
        print("請執行以下命令安裝:")
        print("  pip install -r requirements.txt")
        return False
    
    print("✅ 所有依賴套件已安裝")
    return True

def start_web_server():
    """啟動Web伺服器"""
    print("\n🌐 啟動Web伺服器...")
    print("伺服器將在 http://localhost:5001 啟動")
    print("按 Ctrl+C 停止伺服器")
    
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 伺服器已停止")
    except Exception as e:
        print(f"❌ 啟動伺服器時發生錯誤: {e}")

def start_scheduler():
    """啟動自動化排程器"""
    print("\n⏰ 啟動自動化排程器...")
    print("排程器將在背景運行，執行以下任務:")
    print("  - 每天 09:00: 主要爬蟲任務")
    print("  - 每天 15:00: 熱門地區爬蟲")
    print("  - 每週日 02:00: 清理舊資料")
    print("  - 每天 23:00: 生成每日報告")
    print("  - 每小時: 輕量級爬蟲")
    print("按 Ctrl+C 停止排程器")
    
    try:
        subprocess.run([sys.executable, "scheduler.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 排程器已停止")
    except Exception as e:
        print(f"❌ 啟動排程器時發生錯誤: {e}")

def run_command_line_scraper():
    """執行命令列爬蟲"""
    print("\n🔧 命令列爬蟲工具")
    print("請輸入搜尋參數:")
    
    keyword = input("關鍵字 (例如: Python): ").strip()
    if not keyword:
        print("❌ 關鍵字不能為空")
        return
    
    area = input("地區代碼 (預設: 6001001000 台北市): ").strip() or "6001001000"
    pages = input("爬取頁數 (預設: 2): ").strip() or "2"
    
    try:
        pages = int(pages)
    except ValueError:
        pages = 2
    
    print(f"\n開始爬取: 關鍵字='{keyword}', 地區='{area}', 頁數={pages}")
    
    cmd = [
        sys.executable, "scrape_104.py",
        "--keyword", keyword,
        "--area", area,
        "--pages", str(pages)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 爬蟲執行完成")
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")

def run_examples():
    """執行範例程式"""
    print("\n📚 執行使用範例...")
    print("這將展示各種功能的使用方法")
    
    try:
        subprocess.run([sys.executable, "examples.py"], check=True)
        print("✅ 範例執行完成")
    except Exception as e:
        print(f"❌ 範例執行失敗: {e}")

def run_tests():
    """執行測試"""
    print("\n🧪 執行測試...")
    print("這將測試各個功能是否正常運作")
    
    try:
        subprocess.run([sys.executable, "test_scraper.py"], check=True)
        print("✅ 測試執行完成")
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")

def show_system_info():
    """顯示系統資訊"""
    print("\n📊 系統資訊")
    print(f"Python版本: {sys.version}")
    print(f"當前目錄: {os.getcwd()}")
    print(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查檔案存在
    files_to_check = [
        "scrape_104.py", "database.py", "app.py", "scheduler.py",
        "requirements.txt", "README.md"
    ]
    
    print("\n檔案檢查:")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (不存在)")

def show_help():
    """顯示幫助資訊"""
    print("\n📖 幫助資訊")
    print("這個系統提供以下功能:")
    print()
    print("1. 🌐 Web伺服器")
    print("   - 啟動Flask Web API")
    print("   - 提供職缺搜尋介面")
    print("   - 支援即時爬取和資料庫搜尋")
    print()
    print("2. ⏰ 自動化排程器")
    print("   - 定期執行爬蟲任務")
    print("   - 自動清理舊資料")
    print("   - 生成統計報告")
    print()
    print("3. 🔧 命令列工具")
    print("   - 直接執行爬蟲")
    print("   - 支援多種搜尋參數")
    print("   - 可輸出CSV或JSON格式")
    print()
    print("4. 📚 使用範例")
    print("   - 展示各種功能使用方法")
    print("   - 包含實際操作範例")
    print()
    print("5. 🧪 測試功能")
    print("   - 測試爬蟲功能")
    print("   - 測試資料庫操作")
    print("   - 整合測試")
    print()
    print("📁 專案檔案:")
    print("  - scrape_104.py: 核心爬蟲模組")
    print("  - database.py: 資料庫管理模組")
    print("  - app.py: Flask Web API")
    print("  - scheduler.py: 自動化排程腳本")
    print("  - templates/index.html: 前端頁面")
    print("  - requirements.txt: Python依賴")
    print("  - README.md: 詳細說明文件")

def main_menu():
    """主選單"""
    while True:
        print("\n" + "=" * 40)
        print("📋 主選單")
        print("=" * 40)
        print("1. 🌐 啟動Web伺服器")
        print("2. ⏰ 啟動自動化排程器")
        print("3. 🔧 執行命令列爬蟲")
        print("4. 📚 執行使用範例")
        print("5. 🧪 執行測試")
        print("6. 📊 顯示系統資訊")
        print("7. 📖 顯示幫助")
        print("0. 🚪 退出")
        print("=" * 40)
        
        choice = input("請選擇功能 (0-7): ").strip()
        
        if choice == "1":
            start_web_server()
        elif choice == "2":
            start_scheduler()
        elif choice == "3":
            run_command_line_scraper()
        elif choice == "4":
            run_examples()
        elif choice == "5":
            run_tests()
        elif choice == "6":
            show_system_info()
        elif choice == "7":
            show_help()
        elif choice == "0":
            print("\n👋 感謝使用104職缺搜尋器！")
            break
        else:
            print("❌ 無效的選擇，請重新輸入")

def main():
    """主函數"""
    print_banner()
    
    # 檢查依賴
    if not check_dependencies():
        print("\n❌ 依賴檢查失敗，請先安裝所需套件")
        return
    
    # 顯示主選單
    main_menu()

if __name__ == "__main__":
    main() 