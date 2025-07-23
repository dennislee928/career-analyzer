#!/usr/bin/env python3
"""
104職缺爬蟲測試腳本
用於測試各個功能是否正常運作
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
import os
from scrape_104 import Job104Scraper
from database import JobDatabase

class TestJob104Scraper(unittest.TestCase):
    """測試Job104Scraper類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.scraper = Job104Scraper()
        
    def test_scraper_initialization(self):
        """測試爬蟲初始化"""
        self.assertIsNotNone(self.scraper.base_url)
        self.assertIsNotNone(self.scraper.headers)
        self.assertIn('User-Agent', self.scraper.headers)
    
    @patch('requests.get')
    def test_scrape_104_success(self, mock_get):
        """測試成功爬取職缺"""
        # 模擬API回應
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'list': [
                    {
                        'jobName': 'Python工程師',
                        'custName': '測試公司',
                        'jobUrl': '/job/123',
                        'jobAddrNoDesc': '台北市',
                        'salaryDesc': '月薪50000-80000',
                        'jobDetail': '工作內容...',
                        'appearDate': '2024-01-01',
                        'jobCat': '軟體工程師',
                        'jobType': '全職',
                        'workExp': '1年以上',
                        'edu': '大學',
                        'skill': 'Python, Django',
                        'benefit': '年終獎金',
                        'remoteWork': '1',
                        'jobId': '123'
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 執行爬蟲
        jobs = self.scraper.scrape_104(keyword="Python", pages=1)
        
        # 驗證結果
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['jobName'], 'Python工程師')
        self.assertEqual(jobs[0]['custName'], '測試公司')
    
    @patch('requests.get')
    def test_scrape_104_no_results(self, mock_get):
        """測試沒有搜尋結果的情況"""
        # 模擬空回應
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'list': []}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        jobs = self.scraper.scrape_104(keyword="不存在的職位", pages=1)
        self.assertEqual(len(jobs), 0)
    
    def test_save_to_csv(self):
        """測試CSV儲存功能"""
        test_jobs = [
            {
                'jobName': '測試職位1',
                'custName': '測試公司1',
                'salaryDesc': '50000-80000'
            },
            {
                'jobName': '測試職位2',
                'custName': '測試公司2',
                'salaryDesc': '60000-90000'
            }
        ]
        
        # 使用臨時檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            filename = self.scraper.save_to_csv(test_jobs, temp_file)
            self.assertTrue(os.path.exists(filename))
            
            # 驗證檔案內容
            with open(filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                self.assertIn('測試職位1', content)
                self.assertIn('測試公司1', content)
        finally:
            # 清理臨時檔案
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_save_to_json(self):
        """測試JSON儲存功能"""
        test_jobs = [
            {
                'jobName': '測試職位1',
                'custName': '測試公司1',
                'salaryDesc': '50000-80000'
            }
        ]
        
        # 使用臨時檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            filename = self.scraper.save_to_json(test_jobs, temp_file)
            self.assertTrue(os.path.exists(filename))
            
            # 驗證JSON內容
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['jobName'], '測試職位1')
        finally:
            # 清理臨時檔案
            if os.path.exists(temp_file):
                os.unlink(temp_file)

class TestJobDatabase(unittest.TestCase):
    """測試JobDatabase類別"""
    
    def setUp(self):
        """設置測試環境"""
        # 使用臨時資料庫檔案
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db = JobDatabase(db_type="sqlite", db_path=self.temp_db.name)
    
    def tearDown(self):
        """清理測試環境"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """測試資料庫初始化"""
        self.assertEqual(self.db.db_type, "sqlite")
        self.assertEqual(self.db.db_path, self.temp_db.name)
    
    def test_insert_and_search_jobs(self):
        """測試插入和搜尋職缺"""
        test_jobs = [
            {
                'jobId': '123',
                'jobName': 'Python工程師',
                'custName': '測試公司',
                'jobUrl': '/job/123',
                'jobAddrNoDesc': '台北市',
                'salaryDesc': '50000-80000',
                'jobDetail': '工作內容',
                'appearDate': '2024-01-01',
                'jobCat': '軟體工程師',
                'jobType': '全職',
                'workExp': '1年以上',
                'edu': '大學',
                'skill': 'Python',
                'benefit': '年終獎金',
                'remoteWork': '1'
            }
        ]
        
        # 插入職缺
        inserted_count = self.db.insert_jobs(test_jobs)
        self.assertEqual(inserted_count, 1)
        
        # 搜尋職缺
        search_results = self.db.search_jobs(keyword="Python")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['jobName'], 'Python工程師')
    
    def test_duplicate_insertion(self):
        """測試重複插入處理"""
        test_job = {
            'jobId': '123',
            'jobName': 'Python工程師',
            'custName': '測試公司',
            'jobUrl': '/job/123',
            'jobAddrNoDesc': '台北市',
            'salaryDesc': '50000-80000',
            'jobDetail': '工作內容',
            'appearDate': '2024-01-01',
            'jobCat': '軟體工程師',
            'jobType': '全職',
            'workExp': '1年以上',
            'edu': '大學',
            'skill': 'Python',
            'benefit': '年終獎金',
            'remoteWork': '1'
        }
        
        # 第一次插入
        inserted_count1 = self.db.insert_jobs([test_job])
        self.assertEqual(inserted_count1, 1)
        
        # 修改職位名稱後再次插入（相同jobId）
        test_job['jobName'] = 'Python開發工程師'
        inserted_count2 = self.db.insert_jobs([test_job])
        self.assertEqual(inserted_count2, 1)  # 應該更新而不是新增
        
        # 驗證總數
        total_count = self.db.get_job_count()
        self.assertEqual(total_count, 1)  # 應該只有一筆記錄
    
    def test_search_by_company(self):
        """測試按公司搜尋"""
        test_jobs = [
            {
                'jobId': '123',
                'jobName': 'Python工程師',
                'custName': 'Google',
                'jobUrl': '/job/123',
                'jobAddrNoDesc': '台北市',
                'salaryDesc': '50000-80000',
                'jobDetail': '工作內容',
                'appearDate': '2024-01-01',
                'jobCat': '軟體工程師',
                'jobType': '全職',
                'workExp': '1年以上',
                'edu': '大學',
                'skill': 'Python',
                'benefit': '年終獎金',
                'remoteWork': '1'
            },
            {
                'jobId': '124',
                'jobName': '前端工程師',
                'custName': 'Facebook',
                'jobUrl': '/job/124',
                'jobAddrNoDesc': '台北市',
                'salaryDesc': '60000-90000',
                'jobDetail': '工作內容',
                'appearDate': '2024-01-01',
                'jobCat': '軟體工程師',
                'jobType': '全職',
                'workExp': '1年以上',
                'edu': '大學',
                'skill': 'JavaScript',
                'benefit': '年終獎金',
                'remoteWork': '0'
            }
        ]
        
        # 插入職缺
        self.db.insert_jobs(test_jobs)
        
        # 按公司搜尋
        google_jobs = self.db.search_jobs(company="Google")
        self.assertEqual(len(google_jobs), 1)
        self.assertEqual(google_jobs[0]['custName'], 'Google')
        
        facebook_jobs = self.db.search_jobs(company="Facebook")
        self.assertEqual(len(facebook_jobs), 1)
        self.assertEqual(facebook_jobs[0]['custName'], 'Facebook')

def run_integration_test():
    """執行整合測試"""
    print("執行整合測試...")
    
    try:
        # 創建爬蟲實例
        scraper = Job104Scraper()
        
        # 執行實際爬蟲（只爬取1頁，避免過度請求）
        print("測試實際爬蟲功能...")
        jobs = scraper.scrape_104(keyword="Python", pages=1)
        
        if jobs:
            print(f"✅ 爬蟲測試成功，找到 {len(jobs)} 筆職缺")
            
            # 測試資料庫功能
            print("測試資料庫功能...")
            db = JobDatabase(db_type="sqlite", db_path="test.db")
            
            # 插入職缺
            inserted_count = db.insert_jobs(jobs)
            print(f"✅ 資料庫插入測試成功，插入 {inserted_count} 筆職缺")
            
            # 搜尋職缺
            search_results = db.search_jobs(keyword="Python", limit=5)
            print(f"✅ 資料庫搜尋測試成功，找到 {len(search_results)} 筆職缺")
            
            # 清理測試資料庫
            if os.path.exists("test.db"):
                os.unlink("test.db")
                
        else:
            print("⚠️ 爬蟲沒有找到職缺，可能是網路問題或網站結構變更")
            
    except Exception as e:
        print(f"❌ 整合測試失敗: {e}")

if __name__ == '__main__':
    # 執行單元測試
    print("執行單元測試...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*50 + "\n")
    
    # 執行整合測試
    run_integration_test() 