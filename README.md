# HPC_LogFile_Analysis

### #step 1

- Collect the bhist logs（Use python or shell script）

### #step 2

- Parse the bhist log for each user

- Modify each user's logfile to a proper excel format


### #step 3 

- Visulize excel data tables, analyze user's submission habits and properties
  - job_accuracy
  - job_runtime
  - job_total_CPU_time
  - job_submit_moment
  - job_pend_time
  - job_memory_used
  - job_full_states_by_day
  - job_long_pending_by_day
  - job_submission_counts_by_day
  - job_latest_features

### #step 4 

- Extract queue's features, analyze the queue's recent status
  - User 
  - Status
  - DateRange
  - Days_Recorded
  - Jobs_Recorded
  - Accuracy
  - MEAN_Memory
  - MEAN_CPU_Time
  - MEAN_Real_Time
  - MEAN_Pend
  - MEAN_Submission_Count_Recorded
  - MEAN_Submission_Count
  - latest_job_submission_counts
  - latest_long_pending_jobs

### #step 5

- Correlation analysis

### #step 6

- Further exploration, to be continued...
  - user feature's cluster analysis
  - bjobs logfile analysis
  - Real-time sorting of long-pending jobs 
  - Perhaps use **ELK** tools
#### #Summary

- **难点**在于**业务梳理,以及指标制定**，工具使用还属其次
- 完成日志数据分析全流程：数据提取—数据清洗—特征定义—数据可视化—指导决策
- 代码规范、优化什么的没考虑

#### # Results presentation

![user_log.png](https://i.loli.net/2021/05/29/cT3mBA8vMf5YRuX.jpg)

<!-- ![user_excel.png](https://i.loli.net/2021/05/29/RYbOTXVvrKGl7k2.jpg)

![JustQueue-2019-user_547maa_job_accuracy.png](https://i.loli.net/2021/05/29/l5jdLnQmXs71Zgc.png)

![JustQueue-2019-user_547maa_job_runtime.png](https://i.loli.net/2021/05/29/FdA92bZJYVhUeXN.png)

![JustQueue-2019-user_547maa_job_total_CPUtime.png](https://i.loli.net/2021/05/29/uL8sBzf5xQcy64j.png)

![JustQueue-2019-user_547maa_job_Submit_moment.png](https://i.loli.net/2021/05/29/MuO7i9qeGjKFTDr.png)

![JustQueue-2019-user_547maa_job_pend_time.png](https://i.loli.net/2021/05/29/DTaorbfZ92OvWp8.png)

![JustQueue-2019-user_547maa_job_memory_used.png](https://i.loli.net/2021/05/29/mGEahFsKARjZD5M.png)

![submission_status.png](https://i.loli.net/2021/05/29/9BCyezHwqv6LS5x.jpg)

![JustQueue-2019-user_547maa_job_long_pending_by_day.png](https://i.loli.net/2021/05/29/teumYXfV9yPKNOj.png)

![JustQueue-2019-user_547maa_job_long_pending_of_last_45_days.png](https://i.loli.net/2021/05/29/yXbuR6I31oOQ9Uc.png)

![JustQueue-2019-user_547maa_job_submission_counts_by_day.png](https://i.loli.net/2021/05/29/EsIiOZoHyY2xBez.png)

![JustQueue-2019-user_547maa_job_submission_counts_of_last_45_days.png](https://i.loli.net/2021/05/29/nhdiqbQrkFlLYtG.png)

![JustQueue-2019_last_30_days_job_count.png](https://i.loli.net/2021/05/29/65NBdzAjCE1b9Sl.png)

![part_of_queue_long_pending.png](https://i.loli.net/2021/05/29/zlAtIoYQkTqM2cN.jpg)

![JustQueue-2019_last_30_days_user_feature_collection.png](https://i.loli.net/2021/05/29/8x57ralnDBVeCQO.png) -->


