import requests
import pandas as pd
import time
import random
import argparse
import json
from typing import Dict, List, Optional
from urllib.parse import urlencode

class Job104Scraper:
    def __init__(self):
        self.base_url = "https://www.104.com.tw/jobs/search/list"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.104.com.tw/jobs/search/',
            'Origin': 'https://www.104.com.tw'
        }
        
    def scrape_104(self, 
                   keyword: str = "Python", 
                   area: str = "6001001000", 
                   pages: int = 5,
                   jobcat: Optional[str] = None,
                   salary_min: Optional[int] = None,
                   salary_max: Optional[int] = None,
                   experience: Optional[str] = None,
                   remote_work: Optional[bool] = None) -> List[Dict]:
        """
        爬取104人力銀行的職缺資料
        
        Args:
            keyword: 搜尋關鍵字
            area: 地區代碼 (6001001000=台北市)
            pages: 爬取頁數
            jobcat: 職務類別代碼
            salary_min: 最低薪資
            salary_max: 最高薪資
            experience: 工作經歷 (1y, 3y, 5y等)
            remote_work: 是否可遠端工作
            
        Returns:
            List[Dict]: 職缺資料列表
        """
        all_jobs = []
        
        for page in range(1, pages + 1):
            print(f"正在爬取第 {page} 頁...")
            
            # 構建搜尋參數
            params = {
                'ro': '0',  # 全職
                'kwop': '7',  # 關鍵字搜尋
                'keyword': keyword,
                'expansionType': 'area,spec,com,job,wf,wktm',
                'order': '15',  # 最新職缺
                'page': page,
                'mode': 's',
                'jobsource': '2018indexpoc',
                'langFlag': '0',
                'langStatus': '0',
                'recommendJob': '1',
                'hotJob': '1'
            }
            
            # 添加地區參數
            if area:
                params['area'] = area
                
            # 添加職務類別
            if jobcat:
                params['jobcat'] = jobcat
                
            # 添加薪資範圍
            if salary_min:
                params['s_c'] = salary_min
            if salary_max:
                params['s_d'] = salary_max
                
            # 添加工作經歷
            if experience:
                params['exp'] = experience
                
            # 添加遠端工作
            if remote_work:
                params['remoteWork'] = '1'
            
            try:
                response = requests.get(self.base_url, params=params, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' in data and 'list' in data['data']:
                    jobs = data['data']['list']
                    
                    for job in jobs:
                        job_info = {
                            'jobName': job.get('jobName', ''),
                            'custName': job.get('custName', ''),
                            'jobUrl': job.get('jobUrl', ''),
                            'jobAddrNoDesc': job.get('jobAddrNoDesc', ''),
                            'salaryDesc': job.get('salaryDesc', ''),
                            'jobDetail': job.get('jobDetail', ''),
                            'appearDate': job.get('appearDate', ''),
                            'jobCat': job.get('jobCat', ''),
                            'jobType': job.get('jobType', ''),
                            'workExp': job.get('workExp', ''),
                            'edu': job.get('edu', ''),
                            'skill': job.get('skill', ''),
                            'benefit': job.get('benefit', ''),
                            'remoteWork': job.get('remoteWork', ''),
                            'jobId': job.get('jobId', '')
                        }
                        all_jobs.append(job_info)
                    
                    print(f"第 {page} 頁成功爬取 {len(jobs)} 筆職缺")
                else:
                    print(f"第 {page} 頁沒有找到職缺資料")
                    
            except requests.exceptions.RequestException as e:
                print(f"爬取第 {page} 頁時發生錯誤: {e}")
                continue
            except json.JSONDecodeError as e:
                print(f"解析第 {page} 頁JSON資料時發生錯誤: {e}")
                continue
            
            # 隨機延遲，避免被反爬蟲
            time.sleep(random.uniform(1, 3))
        
        print(f"總共爬取到 {len(all_jobs)} 筆職缺")
        return all_jobs
    
    def save_to_csv(self, jobs: List[Dict], filename: str = None) -> str:
        """將職缺資料儲存為CSV檔案"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"104_jobs_{timestamp}.csv"
        
        df = pd.DataFrame(jobs)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"資料已儲存至 {filename}")
        return filename
    
    def save_to_json(self, jobs: List[Dict], filename: str = None) -> str:
        """將職缺資料儲存為JSON檔案"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"104_jobs_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        
        print(f"資料已儲存至 {filename}")
        return filename

def main():
    """命令列介面"""
    parser = argparse.ArgumentParser(description="104職缺爬蟲工具")
    parser.add_argument('--keyword', type=str, required=True, help='搜尋關鍵字')
    parser.add_argument('--area', type=str, default='6001001000', help='地區代碼 (6001001000=台北市)')
    parser.add_argument('--pages', type=int, default=5, help='爬取頁數')
    parser.add_argument('--jobcat', type=str, help='職務類別代碼')
    parser.add_argument('--salary-min', type=int, help='最低薪資')
    parser.add_argument('--salary-max', type=int, help='最高薪資')
    parser.add_argument('--experience', type=str, help='工作經歷 (1y, 3y, 5y等)')
    parser.add_argument('--remote-work', action='store_true', help='可遠端工作')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='輸出格式')
    parser.add_argument('--output', type=str, help='輸出檔案名稱')
    
    args = parser.parse_args()
    
    # 創建爬蟲實例
    scraper = Job104Scraper()
    
    # 執行爬蟲
    jobs = scraper.scrape_104(
        keyword=args.keyword,
        area=args.area,
        pages=args.pages,
        jobcat=args.jobcat,
        salary_min=args.salary_min,
        salary_max=args.salary_max,
        experience=args.experience,
        remote_work=args.remote_work
    )
    
    if jobs:
        # 儲存資料
        if args.format == 'csv':
            scraper.save_to_csv(jobs, args.output)
        else:
            scraper.save_to_json(jobs, args.output)
    else:
        print("沒有找到任何職缺")

if __name__ == "__main__":
    main() 