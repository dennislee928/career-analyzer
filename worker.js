/**
 * Cloudflare Worker for 104 Job Scraper
 * 處理API請求和自動化排程任務
 */

// 104 API配置
const API_CONFIG = {
  baseUrl: "https://www.104.com.tw/jobs/search/list",
  headers: {
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    Accept: "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    Referer: "https://www.104.com.tw/jobs/search/",
    Origin: "https://www.104.com.tw",
  },
};

// 預設搜尋關鍵字
const DEFAULT_KEYWORDS = [
  "Python",
  "JavaScript",
  "Java",
  "Go",
  "Rust",
  "前端工程師",
  "後端工程師",
  "全端工程師",
  "資料工程師",
  "機器學習",
  "人工智慧",
  "DevOps",
  "SRE",
  "產品經理",
];

// 地區代碼
const AREAS = {
  6001001000: "台北市",
  6001002000: "新北市",
  6001003000: "桃園市",
  6001004000: "台中市",
  6001005000: "台南市",
  6001006000: "高雄市",
};

/**
 * 處理HTTP請求
 */
async function handleRequest(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;

  // 設置CORS標頭
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
  };

  // 處理OPTIONS請求
  if (request.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    let response;

    switch (path) {
      case "/api/search":
        response = await handleSearch(request, env);
        break;
      case "/api/jobs/recent":
        response = await handleRecentJobs(request, env);
        break;
      case "/api/jobs/stats":
        response = await handleStats(request, env);
        break;
      case "/api/scrape":
        response = await handleScrape(request, env);
        break;
      case "/api/jobs/cleanup":
        response = await handleCleanup(request, env);
        break;
      default:
        response = { status: "error", message: "API端點不存在" };
    }

    return new Response(JSON.stringify(response), {
      headers: corsHeaders,
    });
  } catch (error) {
    console.error("處理請求時發生錯誤:", error);
    return new Response(
      JSON.stringify({
        status: "error",
        message: error.message,
      }),
      {
        status: 500,
        headers: corsHeaders,
      }
    );
  }
}

/**
 * 處理搜尋請求
 */
async function handleSearch(request, env) {
  const url = new URL(request.url);
  const keyword = url.searchParams.get("keyword") || "";
  const area = url.searchParams.get("area") || "6001001000";
  const pages = parseInt(url.searchParams.get("pages")) || 1;
  const useDatabase = url.searchParams.get("use_database") !== "false";

  if (useDatabase && keyword) {
    // 從資料庫搜尋
    const jobs = await searchJobsFromDB(keyword, env);
    return {
      status: "success",
      source: "database",
      count: jobs.length,
      data: jobs,
      timestamp: new Date().toISOString(),
    };
  } else {
    // 即時爬取
    const jobs = await scrapeJobs(keyword, area, pages);
    if (jobs.length > 0) {
      await insertJobsToDB(jobs, env);
    }
    return {
      status: "success",
      source: "scraper",
      count: jobs.length,
      data: jobs,
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * 處理最近職缺請求
 */
async function handleRecentJobs(request, env) {
  const url = new URL(request.url);
  const days = parseInt(url.searchParams.get("days")) || 7;

  const jobs = await getRecentJobsFromDB(days, env);

  return {
    status: "success",
    count: jobs.length,
    data: jobs,
  };
}

/**
 * 處理統計資訊請求
 */
async function handleStats(request, env) {
  const totalJobs = await getJobCountFromDB(env);
  const recentJobs = await getRecentJobsFromDB(7, env);

  return {
    status: "success",
    stats: {
      total_jobs: totalJobs,
      recent_jobs: recentJobs.length,
      last_updated: new Date().toISOString(),
    },
  };
}

/**
 * 處理爬蟲請求
 */
async function handleScrape(request, env) {
  const data = await request.json();
  const keyword = data?.keyword || "Python";
  const area = data?.area || "6001001000";
  const pages = data?.pages || 1;

  const jobs = await scrapeJobs(keyword, area, pages);
  let insertedCount = 0;

  if (jobs.length > 0) {
    insertedCount = await insertJobsToDB(jobs, env);
  }

  return {
    status: "success",
    scraped_count: jobs.length,
    inserted_count: insertedCount,
    message: `成功爬取 ${jobs.length} 筆職缺，存入 ${insertedCount} 筆`,
  };
}

/**
 * 處理清理請求
 */
async function handleCleanup(request, env) {
  const data = await request.json();
  const days = data?.days || 30;

  const deletedCount = await deleteOldJobsFromDB(days, env);

  return {
    status: "success",
    deleted_count: deletedCount,
    message: `成功刪除 ${deletedCount} 筆舊職缺資料`,
  };
}

/**
 * 從104爬取職缺資料
 */
async function scrapeJobs(keyword, area, pages) {
  const jobs = [];

  for (let page = 1; page <= pages; page++) {
    try {
      const params = new URLSearchParams({
        ro: "0",
        kwop: "7",
        keyword: keyword,
        expansionType: "area,spec,com,job,wf,wktm",
        order: "15",
        page: page.toString(),
        mode: "s",
        jobsource: "2018indexpoc",
        langFlag: "0",
        langStatus: "0",
        recommendJob: "1",
        hotJob: "1",
        area: area,
      });

      const response = await fetch(`${API_CONFIG.baseUrl}?${params}`, {
        headers: API_CONFIG.headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.data && data.data.list) {
        for (const job of data.data.list) {
          jobs.push({
            jobId: job.jobId || "",
            jobName: job.jobName || "",
            custName: job.custName || "",
            jobUrl: job.jobUrl || "",
            jobAddrNoDesc: job.jobAddrNoDesc || "",
            salaryDesc: job.salaryDesc || "",
            jobDetail: job.jobDetail || "",
            appearDate: job.appearDate || "",
            jobCat: job.jobCat || "",
            jobType: job.jobType || "",
            workExp: job.workExp || "",
            edu: job.edu || "",
            skill: job.skill || "",
            benefit: job.benefit || "",
            remoteWork: job.remoteWork || "",
            createdAt: new Date().toISOString(),
          });
        }
      }

      // 避免請求過於頻繁
      if (page < pages) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    } catch (error) {
      console.error(`爬取第 ${page} 頁時發生錯誤:`, error);
    }
  }

  return jobs;
}

/**
 * 從D1資料庫搜尋職缺
 */
async function searchJobsFromDB(keyword, env) {
  try {
    const stmt = env.DB.prepare(`
      SELECT * FROM jobs 
      WHERE job_name LIKE ? 
      ORDER BY created_at DESC 
      LIMIT 50
    `);
    const result = await stmt.bind(`%${keyword}%`).all();
    return result.results || [];
  } catch (error) {
    console.error("從資料庫搜尋職缺時發生錯誤:", error);
    return [];
  }
}

/**
 * 插入職缺到D1資料庫
 */
async function insertJobsToDB(jobs, env) {
  if (!jobs.length) return 0;

  let insertedCount = 0;

  for (const job of jobs) {
    try {
      const stmt = env.DB.prepare(`
        INSERT OR REPLACE INTO jobs (
          job_id, job_name, cust_name, job_url, job_addr_no_desc,
          salary_desc, job_detail, appear_date, job_cat, job_type,
          work_exp, edu, skill, benefit, remote_work, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      await stmt
        .bind(
          job.jobId,
          job.jobName,
          job.custName,
          job.jobUrl,
          job.jobAddrNoDesc,
          job.salaryDesc,
          job.jobDetail,
          job.appearDate,
          job.jobCat,
          job.jobType,
          job.workExp,
          job.edu,
          job.skill,
          job.benefit,
          job.remoteWork,
          job.createdAt,
          new Date().toISOString()
        )
        .run();

      insertedCount++;
    } catch (error) {
      console.error("插入職缺時發生錯誤:", error);
    }
  }

  return insertedCount;
}

/**
 * 從D1資料庫獲取最近職缺
 */
async function getRecentJobsFromDB(days, env) {
  try {
    const stmt = env.DB.prepare(`
      SELECT * FROM jobs 
      WHERE created_at >= datetime('now', '-${days} days')
      ORDER BY created_at DESC
    `);
    const result = await stmt.all();
    return result.results || [];
  } catch (error) {
    console.error("獲取最近職缺時發生錯誤:", error);
    return [];
  }
}

/**
 * 從D1資料庫獲取職缺總數
 */
async function getJobCountFromDB(env) {
  try {
    const stmt = env.DB.prepare("SELECT COUNT(*) as count FROM jobs");
    const result = await stmt.first();
    return result?.count || 0;
  } catch (error) {
    console.error("獲取職缺總數時發生錯誤:", error);
    return 0;
  }
}

/**
 * 從D1資料庫刪除舊職缺
 */
async function deleteOldJobsFromDB(days, env) {
  try {
    const stmt = env.DB.prepare(`
      DELETE FROM jobs 
      WHERE created_at < datetime('now', '-${days} days')
    `);
    const result = await stmt.run();
    return result.meta?.changes || 0;
  } catch (error) {
    console.error("刪除舊職缺時發生錯誤:", error);
    return 0;
  }
}

/**
 * 處理排程任務
 */
async function handleScheduledTask(env) {
  console.log("執行排程任務:", new Date().toISOString());

  try {
    // 爬取預設關鍵字
    for (const keyword of DEFAULT_KEYWORDS.slice(0, 5)) {
      // 限制數量避免超時
      const jobs = await scrapeJobs(keyword, "6001001000", 1);
      if (jobs.length > 0) {
        await insertJobsToDB(jobs, env);
      }
      // 延遲避免請求過於頻繁
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }

    console.log("排程任務完成");
  } catch (error) {
    console.error("排程任務執行失敗:", error);
  }
}

// 導出處理函數
export default {
  async fetch(request, env, ctx) {
    return handleRequest(request, env);
  },

  async scheduled(event, env, ctx) {
    return handleScheduledTask(env);
  },
};
