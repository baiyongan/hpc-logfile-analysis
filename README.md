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


