# -*- coding: utf-8 -*-
# -*- coding: us-ascii -*-

"""
功能：解析用户的Excel文件，并根据需求，生成相应的用户统计图等
日期：2019/12/10
作者：Bai-Yong-an
备注：需要更改的参数有 FolderName, DateRange, AnalysisDate, 手动注释来开闭相应的方法
"""

import sys
import os
import re
import inspect
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as ticker
from datetime import datetime
from pylab import *
import openpyxl
from openpyxl import Workbook
import time
import shutil
import glob
mpl.rcParams['font.sans-serif'] = ['SimHei']
from queue_status_analysis import append_df_to_excel # 该方法将多个df数据写入到同excel的同一个 sheet 下面


class User_Analysis:
    """
    分析一个用户的历史作业信息，绘制图表，求解并导出必要特征值
    """
    def __init__(self):
        """
        数据初始化，数据导入与预处理
        """
        self.dataset = pd.read_excel(Summary)
        self.ds = self.dataset
        #可能有的数据没有解析到，为了后续处理，先给用None替换
        self.ds = self.ds.fillna('None')
        # 去除 JobID 为 None 的作业
        self.ds1 = self.ds[~self.ds['JobID'].isin(['None'])]
        #按照常理来讲，Completed 和 Done 这两列数值不能同时为None, 不能同时有时间戳，应该删除掉错误行
        #下面两列是精华——前期一定要舍得去除脏数据
        self.ds1 = self.ds1.drop(self.ds1[(self.ds1['Completed'] == 'None') & (self.ds1['Done'] == 'None')].index)
        self.ds1 = self.ds1.drop(self.ds1[(self.ds1['Completed'].str.len() > 4) & (self.ds1['Done'].str.len() > 4)].index)

        self.ds1['User'] = self.ds1['User'].astype(str)
        self.ds1['CPU_Time'] = self.ds1['CPU_Time'].astype(str)
        self.User = ''.join(np.unique(self.ds1['User']))

    def analyse_job_accuracy(self):
        """
        统计分析用户每月的作业准确率,分total，correct，error
        """
        # Total
        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total['Submit'] = pd.to_datetime(job_total['Submit'])
        job_total = job_total[['Submit', 'JobID']]

        Job_Total = job_total['Submit'].groupby([
            # job_total.Submit.dt.year.rename('year'),
            job_total.Submit.dt.month.rename('month'),
            # job_total.Submit.dt.week.rename('week'),
            # job_total.Submit.dt.day.rename('day')
        ]).agg({'count'})

        # Correct
        job_correct = self.ds1[~self.ds1['Done'].isin(['None'])]
        job_correct['Done'] = pd.to_datetime(job_correct['Done'])
        job_correct = job_correct[['Done', 'JobID']]

        Job_Correct = job_correct['Done'].groupby([
            # job_correct.Done.dt.year.rename('year'),
            job_correct.Done.dt.month.rename('month'),
            # job_correct.Done.dt.week.rename('week'),
            # job_correct.Done.dt.day.rename('day')
        ]).agg({'count'})

        # Error
        job_error = self.ds1[~self.ds1['Completed'].isin(['None'])]
        job_error['Completed'] = pd.to_datetime(job_error['Completed'])
        job_error = job_error[['Completed', 'JobID']]

        Job_Error = job_error['Completed'].groupby([
            # job_error.Completed.dt.year.rename('year'),
            job_error.Completed.dt.month.rename('month'),
            # job_error.Completed.dt.week.rename('week'),
            # job_error.Completed.dt.day.rename('day')
        ]).agg({'count'})

        # Result
        Job_Result = pd.concat([Job_Total, Job_Correct, Job_Error], axis=1)
        Job_Result.columns = ['Total', 'Correct', 'Error']
        Job_Result.fillna(0, inplace=True)
        Job_Result.eval('Rate = Correct / Total', inplace=True)
        Job_Result.index.rename('Month', inplace=True)
        Job_Result = Job_Result.round({'Rate': 2})

        #Draw
        x = np.arange(len(Job_Result.index))
        y = np.array(list(Job_Result['Total']))
        y1 = np.array(list(Job_Result['Correct']))
        y2 = np.array(list(Job_Result['Error']))
        y3 = np.array(list(Job_Result['Rate']))
        #构造y_y3 字符串，以便于标记
        Job_Result['Total'] = Job_Result['Total'].map(lambda x:str(x))
        Job_Result['Rate'] = Job_Result['Rate'].map(lambda x:str(x))
        y_y3 = Job_Result['Total'].str.cat(Job_Result['Rate'], sep='__')
        str_y_y3 = dict(zip(y, y_y3))

        x_ticks = list(Job_Result.index)
        plt.figure(figsize=(10, 6))
        # plt.bar(x, y, width = 0.7,align='center',color = 'blue',alpha=0.8)
        plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
        plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)

        plt.xticks(x, x_ticks, size='large', rotation=0)
        plt.yticks(size='large', rotation=0)
        plt.title(SubTitle + ' 不同月份的作业提交数及准确率统计', fontsize=20)
        plt.xlabel('月份值', fontsize=15)
        plt.ylabel('作业提交数', fontsize=15)
        # plt.text(7, 20, Job_Result, fontsize=15)
        #####为每个直方添加相应准确率值
        for a,b in zip(x, y):
            plt.text(a, b, str_y_y3[b], ha='center', va= 'bottom',fontsize=15)
        # for a,b in zip(x,y1):
        #     plt.text(a, b+3, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        # for a,b in zip(x,y2):
        #     plt.text(a, b, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        plt.grid(axis='y', linestyle='-.')
        plt.legend(['Correct', 'Error'], loc='upper left', fontsize=20)
        # plt.show()
        plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_accuracy.png', bbox_inches='tight')

        #Feature
        print(Job_Result)
        print("完成" + self.User + "用户每月的作业准确率分析 " + "\n")

    def analyse_job_runtime(self):
        """
        分析用户的作业运行时长，并绘图，分total, correct, error
        """
        # Total
        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total['Submit'] = pd.to_datetime(job_total['Submit'])
        job_total = job_total[['Submit', 'CPU_Time']]
        # 去除脏数据，并转换object数据类型为float
        job_total = job_total[~job_total['CPU_Time'].str.contains('unknown|None')]
        job_total['CPU_Time'] = pd.DataFrame(job_total['CPU_Time'], dtype=np.float)

        MAX_Total = "最大作业运行时长：" + str(job_total.CPU_Time.max() / 3600) + "h"
        MIN_Total = "最小作业运行时长：" + str(job_total.CPU_Time.min()) + "s"
        MEAN_Total = "平均作业运行时长：" + str(job_total.CPU_Time.mean() / 3600) + "h"
        print(MAX_Total, '\n', MIN_Total, '\n', MEAN_Total)

        # Correct
        job_correct = self.ds1[~self.ds1['Done'].isin(['None'])]
        job_correct['Done'] = pd.to_datetime(job_correct['Done'])
        job_correct = job_correct[['Done', 'CPU_Time']]
        # 去除脏数据，并转换object数据类型为float
        job_correct = job_correct[~job_correct['CPU_Time'].str.contains('unknown|None')]
        job_correct['CPU_Time'] = pd.DataFrame(job_correct['CPU_Time'], dtype=np.float)

        MAX_Correct = "最大正确完成的作业运行时长：" + str(job_correct.CPU_Time.max() / 3600) + "h"
        MIN_Correct = "最小正确完成的作业运行时长：" + str(job_correct.CPU_Time.min()) + "s"
        MEAN_Correct = "平均正确完成的作业运行时长：" + str(job_correct.CPU_Time.mean() / 3600) + "h"
        print(MAX_Correct, '\n', MIN_Correct, '\n', MEAN_Correct)

        # Error
        job_error = self.ds1[~self.ds1['Completed'].isin(['None'])]
        job_error['Completed'] = pd.to_datetime(job_error['Completed'])
        job_error = job_error[['Completed', 'CPU_Time']]
        # 去除脏数据，并转换object数据类型为float
        job_error = job_error[~job_error['CPU_Time'].str.contains('unknown|None')]
        job_error['CPU_Time'] = pd.DataFrame(job_error['CPU_Time'], dtype=np.float)

        MAX_Error = "最大错误退出的作业运行时长：" + str(job_error.CPU_Time.max() / 3600) + "h"
        MIN_Error = "最小错误退出的作业运行时长：" + str(job_error.CPU_Time.min()) + "s"
        MEAN_Error = "平均错误退出的作业运行时长：" + str(job_error.CPU_Time.mean() / 3600) + "h"
        print(MAX_Error, '\n', MIN_Error, '\n', MEAN_Error)

        # Result
        # 根据自定义的分组，划分数据
        length = [-1.0, 60, 300, 600, 1800, 3600, 3600 * 6, 3600 * 12, 3600 * 24, 3600 * 48, float('inf')]
        group_names = ["A:<1min", "B:1-5min", "C:5-10min", "D:10-30min", "E:30-60min", "F:1-6h", "G:6-12h",
                       "H:12-24h", "I:24-48h", "J:>48h"]

        runtime_total = pd.cut(job_total.CPU_Time, length, labels=group_names)
        runtime_correct = pd.cut(job_correct.CPU_Time, length, labels=group_names)
        runtime_error = pd.cut(job_error.CPU_Time, length, labels=group_names)

        Runtime_Total = pd.DataFrame(pd.value_counts(runtime_total))
        Runtime_Total.columns = ['Total_Tasks_Rank']
        Runtime_Correct = pd.DataFrame(pd.value_counts(runtime_correct))
        Runtime_Correct.columns = ['Correct_Tasks_Rank']
        Runtime_Error = pd.DataFrame(pd.value_counts(runtime_error))
        Runtime_Error.columns = ['Error_Tasks_Rank']

        Runtime_Result = pd.concat([Runtime_Total, Runtime_Correct, Runtime_Error], axis=1)
        Runtime_Result.columns = ['Total', 'Correct', 'Error']
        Runtime_Result.fillna(0, inplace=True)

        # Draw 绘制根据作业时长区段不同，所划分的作业提交数统计堆叠图 ———— 正确作业数 & 错误作业数的堆叠图
        x = np.arange(len(Runtime_Result.index))
        y = np.array(list(Runtime_Result['Total']))
        y1 = np.array(list(Runtime_Result['Correct']))
        y2 = np.array(list(Runtime_Result['Error']))
        x_ticks = list(Runtime_Result.index)
        plt.figure(figsize=(10, 6))
        # plt.bar(x, y, width = 0.7,align='center',color = 'blue',alpha=0.8)
        plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
        plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)
        plt.xticks(x, x_ticks, size='large', rotation=20)
        plt.yticks(size='large', rotation=0)
        plt.title(SubTitle + ' 在不同运行时长区段的作业数统计', fontsize=20)
        plt.xlabel('运行时长/CPU*h', fontsize=15)
        plt.ylabel('作业提交数', fontsize=15)
        # plt.text(10, 180, MAX_Total, fontsize=15)
        # plt.text(10, 160, MIN_Total, fontsize=15)
        # plt.text(10, 140, MEAN_Total, fontsize=15)
        # plt.text(10, 20, Runtime_Result, fontsize=15)
        ##为每个直方添加相应作业数标记
        for a, b in zip(x, y):
            plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=15)
        # for a,b in zip(x,y1):
        #     plt.text(a, b+3, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        # for a,b in zip(x,y2):
        #     plt.text(a, b, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        plt.grid(axis='y', linestyle='-.')
        plt.legend(['Correct', 'Error'], loc='upper left', fontsize=20)
        # plt.show()
        plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_runtime.png', bbox_inches='tight')

        #Feature
        print(Runtime_Result)
        print("完成" + self.User + "用户的作业运行时长分析 " + "\n")

    def analyse_job_total_CPU_time(self):
        """
        分析用户作业随月份变化的总的CPU×h数
        """
        # Total
        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total['Submit'] = pd.to_datetime(job_total['Submit'])

        job_total = job_total[['Submit', 'CPU_Time']]
        job_total = job_total[~job_total['CPU_Time'].str.contains('unknown|None')]
        job_total['CPU_Time'] = pd.DataFrame(job_total['CPU_Time'], dtype=np.float)

        # 计算job_total的耗时数/按月算
        job_total = job_total.set_index('Submit')
        job_total = job_total.resample('M').sum()
        job_total.eval('CPU_Time = CPU_Time / 3600', inplace=True)

        # Correct
        job_correct = self.ds1[~self.ds1['Done'].isin(['None'])]
        job_correct['Done'] = pd.to_datetime(job_correct['Done'])

        job_correct = job_correct[['Done', 'CPU_Time']]
        job_correct = job_correct[~job_correct['CPU_Time'].str.contains('unknown|None')]
        job_correct['CPU_Time'] = pd.DataFrame(job_correct['CPU_Time'], dtype=np.float)

        # 计算job_correct的耗时数/按月算
        job_correct = job_correct.set_index('Done')
        job_correct = job_correct.resample('M').sum()
        job_correct.eval('CPU_Time = CPU_Time / 3600', inplace=True)

        # Error
        job_error = self.ds1[~self.ds1['Completed'].isin(['None'])]
        job_error['Completed'] = pd.to_datetime(job_error['Completed'])

        job_error = job_error[['Completed', 'CPU_Time']]
        job_error = job_error[~job_error['CPU_Time'].str.contains('unknown|None')]
        job_error['CPU_Time'] = pd.DataFrame(job_error['CPU_Time'], dtype=np.float)

        # 计算job_error的耗时数/按月算
        job_error = job_error.set_index('Completed')
        job_error = job_error.resample('M').sum()
        job_error.eval('CPU_Time = CPU_Time / 3600', inplace=True)

        # Result
        Time_Total = job_total
        Time_Correct = job_correct
        Time_Error = job_error
        Time_Result = pd.concat([Time_Total, Time_Correct, Time_Error], axis=1)
        Time_Result.columns = ['Total', 'Correct', 'Error']
        Time_Result.index.rename('Month', inplace=True)
        Time_Result.fillna(0, inplace=True)

        # Draw   绘制根据月份值不同，所划分的CPU总耗时堆叠图 ———— 正确作业数 & 错误作业数的堆叠图
        x = np.arange(len(Time_Result.index))
        y = np.array(list(Time_Result['Total']))
        y1 = np.array(list(Time_Result['Correct']))
        y2 = np.array(list(Time_Result['Error']))
        # here we change the index from Datetimeindex to Intindex
        x_ticks = list(Time_Result.index.month)
        plt.figure(figsize=(10, 6))
        # plt.bar(x, y, width = 0.7,align='center',color = 'blue',alpha=0.8)
        plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
        plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)
        plt.xticks(x, x_ticks, size='large', rotation=0)
        plt.yticks(size='large', rotation=0)
        plt.title(SubTitle + ' 不同月份的作业总运行CPU*h统计', fontsize=20)
        plt.xlabel('月份值', fontsize=15)
        plt.ylabel('总运行CPU*h值', fontsize=15)
        # plt.text(7, 20, Time_Result, fontsize=15)
        # 为每个直方添加相应耗时数标记
        for a, b in zip(x, y):
            plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=15)
        # for a,b in zip(x,y1):
        #     plt.text(a, b+3, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        # for a,b in zip(x,y2):
        #     plt.text(a, b, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        plt.grid(axis='y', linestyle='-.')
        plt.legend(['Correct', 'Error'], loc='upper left', fontsize=20)
        # plt.show()
        plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_total_CPUtime.png', bbox_inches='tight')

        #Feature
        print(Time_Result)
        print("完成" + self.User + "用户作业随月份变化的总的CPU×h数分析" + "\n")

    def analyse_job_submit_moment(self):
        """
         分析一天24h中，不同时间段提交的作业数，按照小时区间 进行分析
        """
        # Total
        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total['Submit'] = pd.to_datetime(job_total['Submit'])
        job_total = job_total[['Submit', 'CPU_Time']]
        job_total = job_total[~job_total['CPU_Time'].str.contains('unknown|None')]

        # Correct
        job_correct = self.ds1[~self.ds1['Done'].isin(['None'])]
        # here we still use Submit time !!!
        job_correct['Submit'] = pd.to_datetime(job_correct['Submit'])
        job_correct = job_correct[['Submit', 'Done', 'CPU_Time']]
        job_correct = job_correct[~job_correct['CPU_Time'].str.contains('unknown|None')]

        # Error
        job_error = self.ds1[~self.ds1['Completed'].isin(['None'])]
        # here we still use Submit time !!!
        job_error['Submit'] = pd.to_datetime(job_error['Submit'])
        job_error = job_error[['Submit', 'Completed', 'CPU_Time']]
        job_error = job_error[~job_error['CPU_Time'].str.contains('unknown|None')]

        # Result
        # here we still use Submit time for total, correct and error jobs
        Moment_Total = job_total['Submit'].groupby([
            # job_total.Submit.dt.year.rename('year'),
            # job_total.Submit.dt.month.rename('month'),
            # job_total.Submit.dt.week.rename('week'),
            # job_total.Submit.dt.day.rename('day'),
            job_total.Submit.dt.hour.rename('hour')
        ]).agg({'count'})
        Moment_Correct = job_correct['Submit'].groupby([
            # job_correct.Submit.dt.year.rename('year'),
            # job_correct.Submit.dt.month.rename('month'),
            # job_correct.Submit.dt.week.rename('week'),
            # job_correct.Submit.dt.day.rename('day'),
            job_correct.Submit.dt.hour.rename('hour')
        ]).agg({'count'})
        Moment_Error = job_error['Submit'].groupby([
            # job_error.Submit.dt.year.rename('year'),
            # job_error.Submit.dt.month.rename('month'),
            # job_error.Submit.dt.week.rename('week'),
            # job_error.Submit.dt.day.rename('day'),
            job_error.Submit.dt.hour.rename('hour')
        ]).agg({'count'})

        Moment_Result = pd.concat([Moment_Total, Moment_Correct, Moment_Error], axis=1)
        Moment_Result.columns = ['Total', 'Correct', 'Error']
        ##替换掉 NaN值为0，并转换为 int 类型
        Moment_Result.fillna(0, inplace=True)
        Moment_Result = Moment_Result.astype(int64)

        #Draw  绘制一天24h中，不同时间段提交的作业数 图表
        x = np.arange(len(Moment_Result.index))
        y = np.array(list(Moment_Result['Total']))
        y1 = np.array(list(Moment_Result['Correct']))
        y2 = np.array(list(Moment_Result['Error']))
        x_ticks = list(Moment_Result.index)
        plt.figure(figsize=(10, 6))
        # plt.bar(x, y, width = 0.7,align='center',color = 'blue',alpha=0.8)
        plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
        plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)
        plt.xticks(x, x_ticks, size='large', rotation=0)
        plt.yticks(size='large', rotation=0)
        plt.title(SubTitle + ' 在一天不同时刻的作业提交数统计', fontsize=20)
        plt.xlabel('时刻值/h', fontsize=15)
        plt.ylabel('作业提交数', fontsize=15)
        ##为每个直方添加相应作业数标记
        for a, b in zip(x, y):
            plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=15)
        # # for a,b in zip(x,y1):
        # #     plt.text(a, b+3, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        # # for a,b in zip(x,y2):
        # #     plt.text(a, b, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        plt.grid(axis='y', linestyle='-.')
        plt.legend(['Correct', 'Error'], loc='upper right', fontsize=20)
        # plt.show()
        plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_Submit_moment.png', bbox_inches='tight')

        #Feature
        print(Moment_Result)
        print("完成" + self.User + "用户的24h不同时间段提交的作业数分析" + "\n")

    def analyse_job_pend_time(self):
        """
        分析用户的作业平均等待时长信息 : 分正确和错误
        """
        # Total
        #  Running has more 'None' than Submit , so drop the 'Running'
        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total = job_total[~job_total['Submit'].isin(['None'])]
        job_total = job_total[~job_total['Running'].isin(['None'])]

        job_total['Submit'] = pd.to_datetime(job_total['Submit'])
        job_total['Running'] = pd.to_datetime(job_total['Running'])

        job_total = job_total[['Submit', 'Running', 'CPU_Time']]
        job_total = job_total[~job_total['CPU_Time'].str.contains('unknown|None')]
        job_total['CPU_Time'] = pd.DataFrame(job_total['CPU_Time'], dtype=np.float)

        ##turn the timedelta type to a float type measured by seconds
        job_total['Pend'] = job_total['Running'] - job_total['Submit']
        job_total['Pend'] = job_total['Pend'] / np.timedelta64(1, 's')

        # Correct
        ## Here we need to drop the 'None' type jobs by Done
        job_correct = self.ds1[~self.ds1['Done'].isin(['None'])]
        job_correct = job_correct[~job_correct['Submit'].isin(['None'])]
        job_correct = job_correct[~job_correct['Running'].isin(['None'])]

        job_correct['Submit'] = pd.to_datetime(job_correct['Submit'])
        job_correct['Running'] = pd.to_datetime(job_correct['Running'])
        job_correct = job_correct[['Submit', 'Running', 'Done', 'CPU_Time']]

        job_correct = job_correct[~job_correct['CPU_Time'].str.contains('unknown|None')]
        job_correct['CPU_Time'] = pd.DataFrame(job_correct['CPU_Time'], dtype=np.float)

        ##turn the timedelta type to a float type measured by seconds
        job_correct['Pend'] = job_correct['Running'] - job_correct['Submit']
        job_correct['Pend'] = job_correct['Pend'] / np.timedelta64(1, 's')

        # Error
        ##### Here we need to drop the 'None' type jobs by Completed
        job_error = self.ds1[~self.ds1['Completed'].isin(['None'])]
        job_error = job_error[~job_error['Submit'].isin(['None'])]
        job_error = job_error[~job_error['Running'].isin(['None'])]

        job_error['Submit'] = pd.to_datetime(job_error['Submit'])
        job_error['Running'] = pd.to_datetime(job_error['Running'])
        job_error = job_error[['Submit', 'Running', 'Completed', 'CPU_Time']]

        job_error = job_error[~job_error['CPU_Time'].str.contains('unknown|None')]
        job_error['CPU_Time'] = pd.DataFrame(job_error['CPU_Time'], dtype=np.float)

        ##turn the timedelta type to a float type measured by seconds
        job_error['Pend'] = job_error['Running'] - job_error['Submit']
        job_error['Pend'] = job_error['Pend'] / np.timedelta64(1, 's')

        # Result
        length = [-0.1, 60, 120, 240, 480, 60 * 16, 60 * 32, 3600, 3600 * 6, 3600 * 12, float('inf')]
        group_names = ["A:<1min", "B:1-2min", "C:2-4min", "D:4-8min", "E:8-16min", "F:16-32min", "G:32min-1h",
                       "H:1-6h", "I:6-12h", "J:>12h"]

        pend_total = pd.cut(job_total.Pend, length, labels=group_names)
        pend_correct = pd.cut(job_correct.Pend, length, labels=group_names)
        pend_error = pd.cut(job_error.Pend, length, labels=group_names)

        Pend_Total = pd.DataFrame(pd.value_counts(pend_total))
        Pend_Correct = pd.DataFrame(pd.value_counts(pend_correct))
        Pend_Error = pd.DataFrame(pd.value_counts(pend_error))
        Pend_Total.columns = ['Pend_Tasks_Rank']
        Pend_Correct.columns = ['Pend_Tasks_Rank']
        Pend_Error.columns = ['Pend_Tasks_Rank']

        Pend_Result = pd.concat([Pend_Total, Pend_Correct, Pend_Error], axis=1)
        Pend_Result.columns = ['Total', 'Correct', 'Error']
        Pend_Result.fillna(0, inplace=True)

        # Draw  绘制根据作业等待时长区段不同，所划分的作业提交数堆叠图
        x = np.arange(len(Pend_Result.index))
        y = np.array(list(Pend_Result['Total']))
        y1 = np.array(list(Pend_Result['Correct']))
        y2 = np.array(list(Pend_Result['Error']))
        x_ticks = list(Pend_Result.index)
        plt.figure(figsize=(10, 6))
        # plt.bar(x, y, width = 0.7,align='center',color = 'blue',alpha=0.8)
        plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
        plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)
        plt.xticks(x, x_ticks, size='large', rotation=20)
        plt.yticks(size='large', rotation=0)
        plt.title(SubTitle + '在不同等待时长区段的相应作业数统计', fontsize=20)
        plt.xlabel('等待时长/h', fontsize=15)
        plt.ylabel('作业提交数', fontsize=15)
        # plt.text(12, 20, Pend_Result, fontsize=15)
        ##为每个直方添加相应作业数标记
        for a, b in zip(x, y):
            plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=15)
        # for a,b in zip(x,y1):
        #     plt.text(a, b+3, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        # for a,b in zip(x,y2):
        #     plt.text(a, b, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        plt.grid(axis='y', linestyle='-.')
        plt.legend(['Correct', 'Error'], loc='upper right', fontsize=20)
        # plt.show()
        plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_pend_time.png', bbox_inches='tight')

        #Feature
        print(Pend_Result)
        print("完成" + self.User + "用户的作业平均等待时长信息分析" + "\n")

    def analyse_job_memory_used(self):
        """
         获取用户的资源消耗数，此方法分析内存消耗示意图
        """
        def mem_M_to_G(x):

            if x.endswith('M'):
                x = float(x.split('M')[0]) / 1024
            elif x.endswith('G'):
                x = float(x.split('G')[0])
            else:
                x = 0.0
            return x

        # Total
        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total = job_total[~job_total['AVG_MEM'].isin(['None'])]

        job_total['Submit'] = pd.to_datetime(job_total['Submit'])
        job_total = job_total[['Submit', str('AVG_MEM')]]
        job_total['AVG_MEM'] = job_total['AVG_MEM'].apply(mem_M_to_G)

        # Correct
        job_correct = self.ds1[~self.ds1['Done'].isin(['None'])]
        job_correct = job_correct[~job_correct['AVG_MEM'].isin(['None'])]

        job_correct['Submit'] = pd.to_datetime(job_correct['Submit'])
        job_correct = job_correct[['Submit', str('AVG_MEM')]]
        job_correct['AVG_MEM'] = job_correct['AVG_MEM'].apply(mem_M_to_G)

        # Error
        job_error = self.ds1[~self.ds1['Completed'].isin(['None'])]
        job_error = job_error[~job_error['AVG_MEM'].isin(['None'])]

        job_error['Submit'] = pd.to_datetime(job_error['Submit'])
        job_error = job_error[['Submit', str('AVG_MEM')]]
        job_error['AVG_MEM'] = job_error['AVG_MEM'].apply(mem_M_to_G)

        # Result
        size = [-0.1, 1, 2, 4, 8, 16, 32, 64, float('inf')]
        group_names = ["A:<1G", "B:1-2G", "C:2-4G", "D:4-8G", "E:8-16G", "F:16-32G", "G:32-64G", "H:>64G"]

        mem_total = pd.cut(job_total.AVG_MEM, size, labels=group_names)
        mem_correct = pd.cut(job_correct.AVG_MEM, size, labels=group_names)
        mem_error = pd.cut(job_error.AVG_MEM, size, labels=group_names)

        Mem_Total = pd.DataFrame(pd.value_counts(mem_total))
        Mem_Correct = pd.DataFrame(pd.value_counts(mem_correct))
        Mem_Error = pd.DataFrame(pd.value_counts(mem_error))
        Mem_Total.columns = ['Mem_Tasks_Rank']
        Mem_Correct.columns = ['Mem_Tasks_Rank']
        Mem_Error.columns = ['Mem_Tasks_Rank']

        Mem_Result = pd.concat([Mem_Total, Mem_Correct, Mem_Error], axis=1)
        Mem_Result.columns = ['Total', 'Correct', 'Error']
        Mem_Result.fillna(0, inplace=True)

        # Draw 绘制根据作业消耗掉的内存使用量不同，其相应的作业提交数
        x = np.arange(len(Mem_Result.index))
        y = np.array(list(Mem_Result['Total']))
        y1 = np.array(list(Mem_Result['Correct']))
        y2 = np.array(list(Mem_Result['Error']))
        x_ticks = list(Mem_Result.index)
        plt.figure(figsize=(10, 6))
        # plt.bar(x, y, width = 0.7,align='center',color = 'blue',alpha=0.8)
        plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
        plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)
        plt.xticks(x, x_ticks, size='large', rotation=20)
        plt.yticks(size='large', rotation=0)
        plt.title(SubTitle + ' 不同内存使用量的相应作业数统计', fontsize=20)
        plt.xlabel('内存使用量/G', fontsize=15)
        plt.ylabel('作业提交数', fontsize=15)
        # plt.text(9, 20, Mem_Result, fontsize=15)
        ##为每个直方添加相应作业数标记
        for a, b in zip(x, y):
            plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=15)
        # for a,b in zip(x,y1):
        #     plt.text(a, b+3, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        # for a,b in zip(x,y2):
        #     plt.text(a, b, '%.0f' % b, ha='center', va= 'bottom',fontsize=15)
        plt.grid(axis='y', linestyle='-.')
        plt.legend(['Correct', 'Error'], loc='upper right', fontsize=20)
        # plt.show()
        plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_memory_used.png', bbox_inches='tight')

        #Feature
        print(Mem_Result)
        print("完成" + self.User + "用户的作业内存消耗数分析" + "\n")

    def prepare_for_job_submission_habit(self):
        """
        为后续的三个分析用户每天提交习惯的方法，做统一的数据预处理
        """
        def mem_M_to_G(x):
            if x.endswith('M'):
                x = float(x.split('M')[0]) / 1024
            elif x.endswith('G'):
                x = float(x.split('G')[0])
            else:
                x = 0.0
            return x

        job_total = self.ds1[~self.ds1['Submit'].isin(['None'])]
        job_total = job_total[~job_total['Running'].isin(['None'])]
        job_total['Submit'] = pd.to_datetime(job_total['Submit'])
        job_total['Running'] = pd.to_datetime(job_total['Running'])

        job_total = job_total[['User','Submit', 'Running', 'Completed', 'Done', 'CPU_Time', str('AVG_MEM')]]

        job_total = job_total[~job_total['CPU_Time'].str.contains('unknown|None')]
        job_total['CPU_Time'] = pd.DataFrame(job_total['CPU_Time'], dtype=np.float)
        ## Use the function mem_M_to_G again
        job_total['AVG_MEM'] = job_total['AVG_MEM'].apply(mem_M_to_G)
        job_total['AVG_MEM'] = pd.DataFrame(job_total['AVG_MEM'], dtype=np.float)

        ### 构建New_Done列数据，为None时，设置为Completed的值,
        correct_time = lambda job_total: job_total['Completed'] if job_total['Done'] == 'None' else job_total['Done']
        job_total['New_Done'] = job_total.apply(correct_time, axis=1)
        ### 这里可能Completed 和 Done 都有值，或者都为None，需要在New_Done序列中，删除掉科恩能够存在的 None值。
        job_total = job_total[~job_total['New_Done'].isin(['None'])]
        job_total['New_Done'] = pd.to_datetime(job_total['New_Done'])

        # 构建New_Completed列数据，为None时，设置为Running的值
        error_time = lambda job_total: job_total['Running'] if job_total['Completed'] == 'None' else job_total[
            'Completed']
        job_total['New_Completed'] = job_total.apply(error_time, axis=1)
        job_total['New_Completed'] = pd.to_datetime(job_total['New_Completed'])

        ### 假设任务全周期是  "投递——等待——错误——正确"。
        ### 正确完成，则error time为0， 错误完成，则correct time为0 ，黄-红-绿 堆叠起来即可，按照天数显示即可。

        job_total['Pend'] = job_total['Running'] - job_total['Submit']
        job_total['Pend'] = job_total['Pend'] / np.timedelta64(1, 's')

        job_total['Error'] = job_total['New_Completed'] - job_total['Running']
        job_total['Error'] = job_total['Error'] / np.timedelta64(1, 's')

        job_total['Correct'] = job_total['New_Done'] - job_total['New_Completed']
        job_total['Correct'] = job_total['Correct'] / np.timedelta64(1, 's')

        self.job_total = job_total
        return self.job_total

    def _analyse_job_full_states_by_day(self):
        """
        分析用户每一天的作业提交状态,用户提交习惯 ———— 只分析最近的有记录提交的三十天的数据图，否则程序运行很卡
        """
        # Call
        job_total = self.prepare_for_job_submission_habit()

        # Construct
        job_total = job_total[job_total['Submit'] > TimeNode.strftime('%Y-%m-%d %X')]
        if len(job_total) > 0:
            new_job_total = job_total[['Submit', 'Pend', 'Error', 'Correct']]
            new_job_total['Submit_YMD'] = new_job_total['Submit'].map(lambda x: str(x.strftime('%Y-%m-%d')))
            # Draw a picture when there is a need to draw.
            #创建新的文件夹,存储图片
            if not os.path.exists(SubTitle + '_job_full_states_of_last_' + str(DateRange) + '_days'):
                os.mkdir(SubTitle + '_job_full_states_of_last_' + str(DateRange) + '_days')
            #生成最近 DateRange 天的有效提交天的数据图
            Last_Days_Recorded_List = np.unique(new_job_total['Submit_YMD'])
            for dt in Last_Days_Recorded_List:
                new_job_total_by_Day = new_job_total[new_job_total["Submit_YMD"] == dt]
                x = new_job_total_by_Day['Submit']
                x_start = x.min() + datetime.timedelta(hours=-0.5)
                x_end = x.max() + datetime.timedelta(hours=0.5)
                y1 = new_job_total_by_Day['Pend']
                y2 = new_job_total_by_Day['Error'] + y1
                y3 = new_job_total_by_Day['Correct'] + y2

                plt.figure(figsize=(30, 15))
                plt.plot(x, y1, 'yo ', x, y2, 'r* ', x, y3, 'g^ ', markersize=25)
                plt.legend(['Pend', 'Error', 'Correct'], loc='upper left', fontsize=25)
                plt.title(SubTitle + '在最近' + str(DateRange) + '天的' + dt + '当天的作业提交情况', fontsize=20)
                plt.xlabel('作业具体提交时刻', fontsize=20)
                plt.ylabel('作业运行全周期', fontsize=20)
                plt.xticks(fontsize=20, rotation=0)
                plt.yticks(fontsize=25, rotation=0)
                plt.grid(axis='x', linestyle=':', linewidth=3)
                plt.grid(axis='y', linestyle=':', linewidth=3)
                plt.xlim(x_start, x_end)
                ##标记异常数据点
                df1 = new_job_total_by_Day[new_job_total_by_Day['Pend'] > 60.0]
                for i in range(len(df1)):
                    x = df1.iloc[i][0]
                    y = df1.iloc[i][1]
                    plt.text(x, y + 1, y, fontsize=25,
                             bbox=dict(boxstyle='round,pad=0.5', fc='blue', ec='k', lw=1, alpha=0.5))
                # 自定义刻度
                ax = plt.gca()
                ax.xaxis.set_major_locator(dates.HourLocator(interval=1))  # 主刻度为 每小时
                # ax.xaxis.set_major_formatter(dates.DateFormatter('00\n\n\t %H Hour\n%Y-%m-%d'))
                ax.xaxis.set_major_formatter(dates.DateFormatter('00\n\n\t %H Hour'))
                ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=30))  # 副刻度为 每30min
                ax.xaxis.set_minor_formatter(dates.DateFormatter('%M'))
                ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
                ##设置y轴为对数坐标轴
                ax.set_yscale('log', nonposy='mask', subsy=[0])
                # plt.show()
                plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_full_states_of_last_' + str(DateRange) + '_days'
                                  + "\\"  + SubTitle + '_job_full_states_on_' + dt + r'.png', bbox_inches='tight')
        elif len(job_total) == 0:
            pass
        print("完成" + self.User + "用户最近" + str(DateRange) + "天的作业提交状态分析" + "\n")

    def analyse_job_long_pending_by_day(self):
        """
        统一分析绘制所有一年中用户长时间等待的作业，并分析最近一段时间队列成员的习惯
        合并生成最近 DateRange 天活跃用户的长时等待任务的excel信息总表
        """
        # Call
        job_total = self.prepare_for_job_submission_habit()

        # Construct
        new_job_total = job_total[['User', 'Submit', 'Pend', 'Error', 'Correct']]
        # 注意，这里根据定义的 AnalysisDate 变量，拼接一下新构造出来的Submit_HMS数据
        new_job_total['Submit_HMS'] = new_job_total['Submit'].map(lambda x: str(AnalysisDate) + ' ' + str(x.strftime('%H:%M:%S')))
        new_job_total['Submit_HMS'] = pd.to_datetime(new_job_total['Submit_HMS'])
        #print(new_job_total['Submit_HMS'])

        job_long_pending_by_day = new_job_total[['User', 'Submit', 'Submit_HMS', 'Pend', 'Error', 'Correct']]
        Outliers = job_long_pending_by_day[job_long_pending_by_day['Pend'] > 60.0]
        True_Outliers = Outliers[Outliers['Error'] == 0.0]
        False_Outliers = Outliers[Outliers['Error'] > 0.0]

        # # Draw
        #如果没有值的话，绘图时会报错，这时候应该怎么做？加判断
        Current_Picture_1 = os.path.join(StorePath, SubTitle + '_job_long_pending_by_day.png')
        if os.path.exists(Current_Picture_1):  # I am joking here!
            os.remove(Current_Picture_1)
        if not os.path.exists(Current_Picture_1):
            if len(Outliers) > 0:
                x = Outliers['Submit_HMS']
                x_start = x.min() + datetime.timedelta(hours=-1)
                x_end = x.max() + datetime.timedelta(hours=1)

                x1 = True_Outliers['Submit_HMS']
                x2 = False_Outliers['Submit_HMS']

                y1 = True_Outliers['Pend']
                y2 = False_Outliers['Pend']

                # y2 = Outliers['Error'] + y1
                # y3 = Outliers['Correct'] + y2
                plt.figure(figsize=(25, 12))
                plt.plot(x1, y1, 'go ', x2, y2, 'r* ', markersize=25)
                plt.legend(['Correct', 'Error'], loc='upper left', fontsize=25)
                plt.title(SubTitle + ' 所有长时等待作业(>60s)的提交时刻汇总分析'
                          + '\n' + '<' + '提交作业总数: ' + str(len(job_long_pending_by_day))
                          + '  有记录的长时等待作业数: ' + str(len(Outliers)) + '>', fontsize=30)
                plt.xlabel('作业具体提交时刻', fontsize=20)
                plt.ylabel('长时等待作业的等待时间/s', fontsize=20)
                plt.xticks(fontsize=20, rotation=0)
                plt.yticks(fontsize=25, rotation=0)
                plt.grid(axis='x', linestyle=':', linewidth=3)
                plt.grid(axis='y', linestyle=':', linewidth=3)
                plt.xlim(x_start, x_end)

                # 标记异常数据点,等待时间超过三个小时的时候，标记一下
                df1 = Outliers[Outliers['Pend'] > 60 * 60 * 3]
                for i in range(len(df1)):
                    x = df1.iloc[i][2]
                    y = df1.iloc[i][3]
                    plt.text(x, y - 10, y, fontsize=20)
                # 自定义刻度
                ax = plt.gca()
                ax.xaxis.set_major_locator(dates.HourLocator(interval=1))  # 主刻度为 每小时
                ax.xaxis.set_major_formatter(dates.DateFormatter('\n00\n\n %H'))
                ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=30))  # 副刻度为 每30min
                ax.xaxis.set_minor_formatter(dates.DateFormatter('%M'))
                ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
                ##设置y轴为对数坐标轴
                ax.set_yscale('log', nonposy='mask', subsy=[0])
                # plt.show()
            else:
                plt.figure(figsize=(25, 12))
                plt.legend(['Correct', 'Error'], loc='upper left', fontsize=25)
                plt.title(SubTitle + ' 所有长时等待作业(>60s)的提交时刻汇总分析'
                          + '\n' + '<' + '提交作业总数: ' + str(len(job_long_pending_by_day))
                          + '  有记录的长时等待作业数: ' + str(len(Outliers)) + '>', fontsize=30)
                plt.xlabel('作业具体提交时刻', fontsize=20)
                plt.ylabel('长时等待作业的等待时间/s', fontsize=20)
                plt.xticks(fontsize=20, rotation=0)
                plt.yticks(fontsize=25, rotation=0)
                plt.grid(axis='x', linestyle=':', linewidth=3)
                plt.grid(axis='y', linestyle=':', linewidth=3)
                plt.text(0.4, 0.5, "无长时等待作业", fontsize=30, bbox=dict(boxstyle='round,pad=0.5', fc='blue', ec='k', lw=1, alpha=0.5) )
            plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_long_pending_by_day.png', bbox_inches='tight')
            print("完成" + self.User + "用户一年中长时间等待的作业统计分析" + "\n")

        ## 截取最近 DateRange 天的异常数据，并绘制相应用户的等待异常值(0-24h)，保存到Queue_Job_Long_Pending_Excel里面，留待绘制队列的总体图表

        latest_job_long_pending_by_day = job_long_pending_by_day[job_long_pending_by_day['Submit'] >= TimeNode]

        if len(latest_job_long_pending_by_day) > 0:
            Latest_Outliers = latest_job_long_pending_by_day[latest_job_long_pending_by_day['Pend'] > 60.0]
            Latest_True_Outliers = Latest_Outliers[Latest_Outliers['Error'] == 0.0]
            Latest_False_Outliers = Latest_Outliers[Latest_Outliers['Error'] > 0.0]
            # Notice here! we need to split the original excel twice: {1: by TimeNode 2: by Pend time > 60s}
            if len(Latest_Outliers) > 0: # 可能在相应时间节点只有有作业，但是可能作业等待时长没有超过 60s, 如果不判断，则会有空行出现
                append_df_to_excel(Queue_Job_Long_Pending_Excel, Latest_Outliers, header=False)
            # # Draw
            # 如果没有值的话，绘图时会报错，这时候应该怎么做？加判断
            Current_Picture_2 = os.path.join(StorePath, SubTitle + '_job_long_pending_of_last_' + str(DateRange) + '_days.png')
            if os.path.exists(Current_Picture_2):  # I am joking here!
                os.remove(Current_Picture_2)
            if not os.path.exists(Current_Picture_2):
                if len(Latest_Outliers) > 0:
                    x = Latest_Outliers['Submit_HMS']

                    # x_start = x.min() + datetime.timedelta(hours=-1)
                    # x_end = x.max() + datetime.timedelta(hours=1)
                    #此处,将时间统一为 0 ~ 24h 的时刻
                    # Use Label_Time as a boarder symbol !!
                    Label_Time = datetime.datetime.strptime(AnalysisDate.strftime('%Y-%m-%d %X'), "%Y-%m-%d %X")

                    x_start = Label_Time + + datetime.timedelta(hours=-0.5)
                    x_end = Label_Time + datetime.timedelta(hours=24.5)

                    x1 = Latest_True_Outliers['Submit_HMS']
                    x2 = Latest_False_Outliers['Submit_HMS']

                    y1 = Latest_True_Outliers['Pend']
                    y2 = Latest_False_Outliers['Pend']

                    # y2 = Latest_Outliers['Error'] + y1
                    # y3 = Latest_Outliers['Correct'] + y2
                    plt.figure(figsize=(25, 12))
                    plt.plot(x1, y1, 'go ', x2, y2, 'r* ', markersize=25)
                    plt.legend(['Correct', 'Error'], loc='upper left', fontsize=25)
                    plt.title(SubTitle + '最近' + str(DateRange) + '天的长时等待作业(>60s)的提交时刻汇总分析'
                              + '\n' + '<' + '提交作业总数: ' + str(len(latest_job_long_pending_by_day))
                              + '  有记录的长时等待作业数: ' + str(len(Latest_Outliers)) + '>', fontsize=30)
                    plt.xlabel('作业具体提交时刻', fontsize=20)
                    plt.ylabel('长时等待作业的等待时间/s', fontsize=20)
                    plt.xticks(fontsize=20, rotation=0)
                    plt.yticks(fontsize=25, rotation=0)
                    plt.grid(axis='x', linestyle=':', linewidth=3)
                    plt.grid(axis='y', linestyle=':', linewidth=3)
                    plt.xlim(x_start, x_end)

                    # 标记异常数据点,等待时间超过半小时的时候，标记一下
                    Latest_df1 = Latest_Outliers[Latest_Outliers['Pend'] > 60 * 60]
                    for i in range(len(Latest_df1)):
                        x = Latest_df1.iloc[i][2]
                        y = Latest_df1.iloc[i][3]
                        plt.text(x, y - 10, y, fontsize=25)
                    # 自定义刻度
                    ax = plt.gca()
                    ax.xaxis.set_major_locator(dates.HourLocator(interval=2))  # 主刻度为 每小时
                    ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n %H'))
                    ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=60))  # 副刻度为 每30min
                    ax.xaxis.set_minor_formatter(dates.DateFormatter('%M'))
                    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
                    ##设置y轴为对数坐标轴
                    ax.set_yscale('log', nonposy='mask', subsy=[0])
                    # plt.show()
                else:
                    plt.figure(figsize=(25, 12))
                    plt.legend(['Correct', 'Error'], loc='upper left', fontsize=25)
                    plt.title(SubTitle + '最近' + str(DateRange) + ' 天的长时等待作业(>60s)的提交时刻汇总分析'
                              + '\n' + '<' + '提交作业总数: ' + str(len(latest_job_long_pending_by_day))
                              + '  有记录的长时等待作业数: ' + str(len(Latest_Outliers)) + '>', fontsize=30)
                    plt.xlabel('作业具体提交时刻', fontsize=20)
                    plt.ylabel('长时等待作业的等待时间/s', fontsize=20)
                    plt.xticks(fontsize=20, rotation=0)
                    plt.yticks(fontsize=25, rotation=0)
                    plt.grid(axis='x', linestyle=':', linewidth=3)
                    plt.grid(axis='y', linestyle=':', linewidth=3)
                    plt.text(0.4, 0.5, "无长时等待作业", fontsize=30,
                             bbox=dict(boxstyle='round,pad=0.5', fc='blue', ec='k', lw=1, alpha=0.5))
                plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_long_pending_of_last_' + str(DateRange) + '_days.png', bbox_inches='tight')
                print("完成" + self.User + "用户" + "最近" + str(DateRange) + "天的长时间等待的作业统计分析" + "\n")

    def analyse_job_submission_counts_by_day(self):
        """
        分析用户每天的提交作业数随日期的变化
        合并生成最近 DateRange 天活跃用户的作业提交数excel信息总表
        """
        # Call
        job_total = self.prepare_for_job_submission_habit()

        # Construct
        new_job_total = job_total[['User', 'Submit', 'Pend', 'Error', 'Correct']]
        new_job_total['Submit_YMD'] = new_job_total['Submit'].map(lambda x: str(x.strftime('%Y-%m-%d')))
        new_job_total['Submit_YMD'] = pd.to_datetime(new_job_total['Submit_YMD'])

        new_job_total['Pend_Label'] = new_job_total['Pend'].map(lambda x: 1 if x > 60.0 else 0)
        new_job_total['Error_Label'] = new_job_total['Error'].map(lambda x: 1 if x != 0.0 else 0)
        new_job_total['Correct_Label'] = new_job_total['Error'].map(lambda x: 1 if x == 0.0 else 0)

        job_count_by_day = new_job_total[['User', 'Submit_YMD', 'Pend_Label', 'Error_Label', 'Correct_Label']]
        Job_Count = job_count_by_day.groupby(by='Submit_YMD').sum()

        ### 获取并返回近期的：日期统计值 和日均作业提交数，传给最后的 latest_feature 方法
        global Days_Recorded, MEAN_submission_Count_Recorded, MEAN_submission_Count
        latest_job_count_by_day = job_count_by_day[job_count_by_day['Submit_YMD'] >= TimeNode]
        if len(latest_job_count_by_day) > 0:
            Latest_Job_Count = latest_job_count_by_day.groupby(by='Submit_YMD').sum()
            #将有记录的数据直接追加到父目录的Queue_Job_Count_Excel里面，以供后续遍历做队列的总图 (能不能加CPU_Time这列？)
            #此处调用写入同一个sheet的方法
            # latest_job_count_by_day = latest_job_count_by_day.reset_index(drop=True)
            append_df_to_excel(Queue_Job_Count_Excel, latest_job_count_by_day, header=False)
            # print(Job_Count.index)
            # print(Latest_Job_Count.index)
            Days_Recorded = len(Latest_Job_Count.index)
            submission_Count = Latest_Job_Count.apply(lambda x: x['Error_Label'] + x['Correct_Label'], axis=1)
            MEAN_submission_Count_Recorded = format(submission_Count.sum() / Days_Recorded, '.2f')
            MEAN_submission_Count = format(submission_Count.sum() / DateRange, '.2f')

            Current_Picture_1 = os.path.join(StorePath, SubTitle + '_job_submission_counts_of_last_' + str(DateRange) + '_days.png')
            if os.path.exists(Current_Picture_1):  # I am joking here!
                os.remove(Current_Picture_1)
            if not os.path.exists(Current_Picture_1):
                x = Latest_Job_Count.index
                # x_start = x.min() + datetime.timedelta(days=-2)
                # x_end = x.max() + datetime.timedelta(days=2)
                #注意，这里的时间跨度是恒定的
                x_start = TimeNode + datetime.timedelta(days=-2)
                x_end = AnalysisDate + datetime.timedelta(days=2)

                y = np.array(list(Latest_Job_Count['Pend_Label']))
                y1 = np.array(list(Latest_Job_Count['Correct_Label']))
                y2 = np.array(list(Latest_Job_Count['Error_Label']))

                # plt.figure(figsize=(25, 12))
                plt.figure(figsize=(10, 6))
                plt.bar(x, -y, width=0.7, align='center', color='yellow', alpha=0.8)
                plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
                plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)

                plt.legend(['Pend_Count (>60s)', 'Correct_Count', 'Error_Count'], loc='upper left', fontsize=15)
                plt.title(SubTitle + ' 在最近' + str(DateRange) +'天的作业数提交数统计' + '\n'
                   + '<' + '时间跨度: ' + str(DateRange) + '  有记录的提交天数: ' + str(Days_Recorded) + '>', fontsize=20)
                plt.xlabel('作业提交日期', fontsize=15)
                plt.ylabel('每日任务数量统计', fontsize=15)
                plt.xticks(fontsize=15, rotation=0)
                plt.yticks(fontsize=15, rotation=0)
                plt.grid(axis='x', linestyle=':', linewidth=3)
                plt.grid(axis='y', linestyle=':', linewidth=3)

                plt.xlim(x_start, x_end)
                # 自定义刻度
                ax = plt.gca()
                ax.xaxis.set_major_locator(dates.DayLocator(interval=10))  # 主刻度为 每天
                ax.xaxis.set_major_formatter(dates.DateFormatter('\n%Y-%m-%d'))
                # plt.show()
                plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_submission_counts_of_last_' + str(DateRange) + '_days.png',
                            bbox_inches='tight')
                print("完成" + self.User + "用户最近" + str(DateRange) + "天的提交作业数随日期的变化分析" + "\n")
            else:
                print('我是' + self.User + '的analyse_job_submission_counts_by_day()，Picture_1 结果文件已存在' + '\n' +
                      '可能只是被analyse_job_latest_features()调用，并没重复画图' + "\n")

        elif len(latest_job_count_by_day) == 0:
            Days_Recorded, MEAN_submission_Count_Recorded, MEAN_submission_Count = 'None', 'None', 'None'

        #Draw 这里需要两张表，一张是用户全年的作业提交表，一张是从TimeNode之后的作业提交表，如果为空，就不画
        Current_Picture_2 = os.path.join(StorePath,  SubTitle + '_job_submission_counts_by_day.png')
        if os.path.exists(Current_Picture_2): # I am joking here!
            os.remove(Current_Picture_2)
        if not os.path.exists(Current_Picture_2):
            x = Job_Count.index
            x_start = x.min() + datetime.timedelta(days=-2)
            x_end = x.max() + datetime.timedelta(days=2)

            y = np.array(list(Job_Count['Pend_Label']))
            y1 = np.array(list(Job_Count['Correct_Label']))
            y2 = np.array(list(Job_Count['Error_Label']))

            plt.figure(figsize=(25, 12))
            plt.bar(x, -y, width=0.7, align='center', color='yellow', alpha=0.8)
            plt.bar(x, y1, width=0.7, align='center', color='green', bottom=y2, alpha=0.8)
            plt.bar(x, y2, width=0.7, align='center', color='red', alpha=0.8)

            plt.legend(['Pend_Count (>60s)', 'Correct_Count', 'Error_Count'], loc='upper left', fontsize=25)
            plt.title(SubTitle + ' 在一年中每日的作业数提交数统计' + '\n'
                      + '<' + '时间跨度: ' + str((x.max() - x.min()).days) + '  有记录的提交天数: ' + str(len(x)) + '>', fontsize=20)
            plt.xlabel('作业提交日期', fontsize=20)
            plt.ylabel('每日任务数量统计', fontsize=20)
            plt.xticks(fontsize=20, rotation=0)
            plt.yticks(fontsize=25, rotation=0)
            plt.grid(axis='x', linestyle=':', linewidth=3)
            plt.grid(axis='y', linestyle=':', linewidth=3)
            plt.xlim(x_start, x_end)
            # 自定义刻度
            ax = plt.gca()
            ax.xaxis.set_major_locator(dates.DayLocator(interval=30))  # 主刻度为 每天
            ax.xaxis.set_major_formatter(dates.DateFormatter('\n%Y-%m-%d'))
            # plt.show()
            plt.savefig(fname=StorePath + "\\" + SubTitle + '_job_submission_counts_by_day.png', bbox_inches='tight')
            print("完成" + self.User + "用户每天的提交作业数随日期的变化分析" + "\n")
        else:
            print('我是' + self.User + '的analyse_job_submission_counts_by_day()，Picture_2 结果文件已存在' + '\n' +
            '可能只是被analyse_job_latest_features()调用，并没重复画图' + "\n")

    def analyse_job_latest_features(self):
        """
        作废————获取最近100个作业的均值指标：准确率，等待时间，运行时间，内存使用量，日提交数
        这个数据指标不准确，应该分析最近一个月的队列作业数情况，和用户活跃情况
        """
        # Call
        job_total = self.prepare_for_job_submission_habit()
        self.analyse_job_submission_counts_by_day()

        #在这里，根据TimeNode时间戳，截取新的job_total列表
        job_total = job_total[ job_total['Submit'] > TimeNode.strftime('%Y-%m-%d %X')]
        # print(len(job_total))

        # Calculate
        Jobs_Recorded = len(job_total)
        latest_jt = job_total
        # print(latest_jt.columns)
        # print(latest_jt[['CPU_Time', 'AVG_MEM', 'Pend', 'Error', 'Correct', 'Done']])
        if Jobs_Recorded != 0:
            Accuracy = format((Jobs_Recorded - len(latest_jt[latest_jt['Done'] == 'None'])) / Jobs_Recorded, '.2f')
            MEAN_Memory = format(latest_jt['AVG_MEM'].sum() / Jobs_Recorded, '.2f')
            MEAN_CPU_Time = format(latest_jt['CPU_Time'].sum() / Jobs_Recorded, '.2f')
            MEAN_Real_Time = format(latest_jt['Correct'].sum() / Jobs_Recorded, '.2f')
            MEAN_Pend = format(latest_jt['Pend'].sum() / Jobs_Recorded, '.2f')
            Status = 'Active'
        elif Jobs_Recorded == 0:
            Accuracy, MEAN_Memory, MEAN_CPU_Time, MEAN_Real_Time, MEAN_Pend = 'None', 'None', 'None', 'None', 'None'
            Status = 'Inactive'

        print("------------------------------------------------------------", '\n')
        print("用户名：", self.User, '\n')
        print("分析的近期时间跨度为(单位：天)：", DateRange, '\n')
        print("该用户在最近的状态为：", Status, '\n')
        print("分析的近期作业量为(单位：个)：", Jobs_Recorded, '\n')
        print("最近", Jobs_Recorded, "个作业的提交准确率为：", Accuracy, '\n')
        print("最近", Jobs_Recorded, "个作业的平均内存使用量为(单位：G)：", MEAN_Memory, '\n')
        print("最近", Jobs_Recorded, "个作业的平均CPU*h使用量为(单位：s)：", MEAN_CPU_Time, '\n')
        print("最近", Jobs_Recorded, "个作业的平均实际耗时为(单位：s)：", MEAN_Real_Time, '\n')
        print("最近", Jobs_Recorded, "个作业的平均等待时间为(单位：s)：", MEAN_Pend, '\n')
        print("最近--有提交记录的--", Days_Recorded, "天的日均作业提交数为：", MEAN_submission_Count_Recorded)
        print("最近", DateRange, "天的日均作业提交数为：", MEAN_submission_Count)
        print("------------------------------------------------------------", '\n')

        #Construct
        user_feature = {'User': self.User,
                        'Status': Status,
                        'DateRange': DateRange,
                        'Days_Recorded': Days_Recorded,
                        'Jobs_Recorded': Jobs_Recorded,
                        'Accuracy': Accuracy,
                        'MEAN_Memory': MEAN_Memory,
                        'MEAN_CPU_Time': MEAN_CPU_Time,
                        'MEAN_Real_Time': MEAN_Real_Time,
                        'MEAN_Pend': MEAN_Pend,
                        'MEAN_submission_Count_Recorded': MEAN_submission_Count_Recorded,
                        'MEAN_submission_Count': MEAN_submission_Count,
                        }
        #Save
        print(self.User, "最近", Jobs_Recorded, "个作业相应的数据特征如下", '\n')
        print(list(user_feature.keys()))
        print(list(user_feature.values()))
        # print(DataFrame(list(user_feature.values())).T)
        append_df_to_excel(Queue_User_Feature_Collection_Excel, DataFrame(list(user_feature.values())).T, header=False)

    def run_all_job_func(self):
        """
        运行以上所有分析用户作业的方法
        """
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if func[0][:11] == 'analyse_job':
                func[1]()
        print("完成所有用户作业提交行为的分析" + "\n")

def main():
    ua = User_Analysis()

    # ua.analyse_job_accuracy()
    # ua.analyse_job_runtime()
    # ua.analyse_job_total_CPU_time()
    # ua.analyse_job_submit_moment()
    # ua.analyse_job_pend_time()
    # ua.analyse_job_memory_used()
    #
    # ua.prepare_for_job_submission_habit()
    #
    # ua.analyse_job_full_states_by_day()     # 此方法慎用，会比较耗时，可针对具体用户使用，使用前手动更新其方法名

    # 下面这三个方法在分析队列近期信息时使用，最好同时使用
    ua.analyse_job_long_pending_by_day()   #同时返回用户的长时等待的作业 excel
    ua.analyse_job_submission_counts_by_day()   #同时返回用户近期的作业提交数 excel
    ua.analyse_job_latest_features()   #返回近期的作业统计特征 excel, 如需单独执行这个，会同时执行上个job_submission_counts 方法

    # ua.run_all_job_func()  #执行以上所有的方法，建议先运行一个单个方法(memory_used 或 total_CPU_time)，排除很少作业量的用户(甚至可能用户的作业全对)，
                            # 或者完善程序，捕获异常，作者不想搞了

if __name__ == '__main__':

    # 记得将用户文件夹放置在正确命名的父文件夹下，父文件夹的命名格式为 QueueName-Year
    FolderName = r'D:\BYA_Project\HPC-log-analysis\HPC-DATA\JustQueue-2019'
    Title = os.path.basename(FolderName)

    #Method_1: 设定时间跨度，计算原始天
    DateRange = 15  #时间间隔
    AnalysisDate = datetime.date(2019, 12, 13)  #分析的截止日
    # AnalysisDate = datetime.date.today()

    Now = datetime.datetime.now()  # 当前时间
    TimeNode = AnalysisDate - datetime.timedelta(days=DateRange)  #分析的起始日
    print(TimeNode)
    print(TimeNode.strftime('%Y-%m-%d %X'))

    #Method_2: 设定起始天，计算时间跨度
        #   # Recent_Start_Time = '2019-11-16 00:00:00'
        #   # TimeNode = datetime.datetime.strptime(Recent_Start_Time, '%Y-%m-%d %X')
        # TimeNode = datetime.datetime(2019, 11, 16, 00, 00, 00)
        # AnalysisDate = datetime.date.today()
        # WorkDayCount = (AnalysisDate - TimeNode.date()).days
        # print(TimeNode)
        # print(TimeNode.strftime('%Y-%m-%d'))
        # print(WorkDayCount)

    os.chdir(FolderName)  # 进入文件目录

    # Queue Information Excels & Directory
    Queue_Job_Count_Excel = FolderName + '\\' + Title \
                            + '_last_' + str(DateRange) + '_days_job_count.xlsx'
    Queue_Job_Long_Pending_Excel = FolderName + '\\' + Title \
                            + '_last_' + str(DateRange) + '_days_long_pending_jobs.xlsx'
    Queue_User_Feature_Collection_Excel = FolderName + '\\' + Title \
                            + '_last_' + str(DateRange) + '_days_user_feature_collection.xlsx'
    Queue_Job_Information_Backup = FolderName + '\\' + Title \
                            + '_Queue_Info_of_last_' + str(DateRange) + '_days_from_' + AnalysisDate.strftime('%Y-%m-%d')

    # 如果存在已经解析过队列的 excel 表，则将其备份到队列文件夹里
    if not os.path.exists(Queue_Job_Information_Backup):
        os.mkdir(Queue_Job_Information_Backup)
    if os.path.exists(Queue_Job_Count_Excel):
        shutil.move(Queue_Job_Count_Excel, Queue_Job_Information_Backup + '\\' + "Stored_at_"
                    + Now.strftime('%Y-%m-%d_%H.%M.%S') + '_' + os.path.basename(Queue_Job_Count_Excel))
    if os.path.exists(Queue_Job_Long_Pending_Excel):
        shutil.move(Queue_Job_Long_Pending_Excel, Queue_Job_Information_Backup + '\\' + "Stored_at_"
                    + Now.strftime('%Y-%m-%d_%H.%M.%S') + '_' + os.path.basename(Queue_Job_Long_Pending_Excel))
    if os.path.exists(Queue_User_Feature_Collection_Excel):
        shutil.move(Queue_User_Feature_Collection_Excel, Queue_Job_Information_Backup + '\\' + "Stored_at_"
                    + Now.strftime('%Y-%m-%d_%H.%M.%S') + '_' + os.path.basename(Queue_User_Feature_Collection_Excel))

    # 获取所有用户的文件夹名，以便于后续遍历
    SubFolderList = sorted([i for i in os.listdir(os.getcwd()) if os.path.isdir(i) and i.startswith(Title + '-')])
    print("共计解析" + str(len(SubFolderList)) + "个用户的Excel，其相应文件夹列表如下：" + "\n")
    print(SubFolderList)

    for sub in SubFolderList:
        os.chdir(sub)
        Summary = os.path.basename(sub) + ".xlsx"
        StorePath = os.getcwd()
        # (filepath, tmpfilename) = os.path.split(Summary)
        # (filename, extension) = os.path.splitext(tmpfilename)
        # SubTitle = filename
        SubTitle = sub

        main()  #循环遍历主函数，里面的方法开关自行切换

        os.chdir(FolderName)


