# -*- coding: utf-8 -*-
# -*- coding: us-ascii -*-

"""
功能：遍历用户的文件夹，并解析其 bhist 日志，根据需求，生成相应的excel数据表格
日期：2019/12/10
作者：Bai-Yong-an
备注：需要更改的参数有 FolderName 以及 parseTime中的Year参数
"""

import openpyxl
from openpyxl import Workbook
import os
import pandas as pd
from pandas import Series, DataFrame


def parseString(str, lab1, lab2, allstr):
    """
    解析作业日志参数（bhist or bjobs）
    """
    try:
        if lab1 in str:
            new_str = str.split(lab1)[1].split(lab2)[0]
        else:
            new_str = 'None'
        allstr.append(new_str)
    except:
        pass
    return allstr

def parseTime(str, exp1, exp2, timestr):
    """
    解析并转换时间戳字符串
    """
    try:
        if exp1 in str:
            timestring = str.split(exp1)[0].split(exp2)[-1]
            T = timestring[-8:]
            M = timestring[3:6]
            D = timestring.split(T)[0].split(M)[1]
            monthDic = {
                'Jan': '1',
                'Feb': '2',
                'Mar': '3',
                'Apr': '4',
                'May': '5',
                'Jun': '6',
                'Jul': '7',
                'Aug': '8',
                'Sep': '9',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12'
            }
            myTime = '{}-{}-{} {}'.format('2019', monthDic[M], D, T)  #Remember to modify the year parameter !!! in this script, the year is 2019.

        else:
            myTime = 'None'
        timestr.append(myTime)
    except:
        pass
    return timestr

##  Job Parameter related definitions
Job_ID = []
Job_Name = []
User = []
Project = []
Application = []
Status = []
Queue = []
# Start_Time = []
# Finish_Time = []
Submit_Host = []
Requested_Resources = []
Execute_Host = []
CPU_Time = []
Memory = []
SWAP = []
# Nthread = []
# PGID = []
# PIDs = []
MAX_MEM = []
AVG_MEM = []

Parameter_List = [[Job_ID, 'Job<', '>,'],
                  [Job_Name, 'JobName<', '>,'],
                  [User, 'User<', '>'],
                  #  [Project, ',Project<', '>,'],
                  #  [Application, 'Application<', '>,'],
                  # [Status, ',Status<', '>,'],
                  #  [Queue, ',Queue<', '>,'],
                  #  [Submit_Host, 'fromhost<', '>,'],
                  [Requested_Resources, 'RequestedResources<', '>,'],
                  [Execute_Host, 'onHost(s)<', '>,'],
                  [CPU_Time, 'CPUtimeusedis', 'seconds'],
                  # [Memory, 'MEM:', 'Gbytes;S'],
                  #  [SWAP, 'SWAP:', 'Gbytes;N'],
                  #  [MAX_MEM, 'MAXMEM:', 'Gbytes;A'],
                   [AVG_MEM, 'AVGMEM:', 'bytesSummary'],
                  ]

##  Job Status related definitions
Submit = []
Running = []
Completed = [] # 代表作业错误退出
Done = []  # 代表作业正常结束

Status_List = [[Submit, ':Submittedfromhost', '>'],
               [Running, ':Runningwith', ';'],
               [Completed, ':Completed<exit>', ';'],
               [Done, ':Donesuccessfully', ';'],
               ]


# 记得将用户文件夹放置在正确命名的父文件夹下，父文件夹的命名格式为 QueueName-Year
FolderName = r'D:\BYA_Project\HPC-log-analysis\HPC-DATA\JustQueue-2019'
os.chdir(FolderName)
Title = os.path.basename(os.getcwd())
SubFolderList = sorted([i for i in os.listdir(os.getcwd()) if os.path.isdir(i) and i.startswith(Title + '-')])
print("共计解析" + str(len(SubFolderList)) + "个用户的日志，其相应文件夹列表如下：" + "\n")
print(SubFolderList)

for sub in SubFolderList: # 循环遍历目录下的相应用户文件夹
    os.chdir(sub)
    SubTitle =  os.path.basename(os.getcwd())
    Summary = os.path.basename(sub) + ".xlsx"     #判断是否有已经解析好的 *.xlsx 文件
    LogFile = os.path.basename(sub) + ".log"      #判断是否存在用户的 *.log 文件
    if os.path.exists(Summary):
        # os.remove(Summary)  ## 如果需要删除Excel，可以反注释该行
        # print("已经删除 " + sub + " 的Excel文件···")
        print("可能已经解析过 " + sub + " 的日志信息，此处跳过···")
    else:
        if not os.path.exists(LogFile):
            print("用户 " + sub + " 的Log文件不存在···")
        else:
            with open(LogFile) as f:
                lines = f.readlines()
                f.flush()
                f.close()

            wb = Workbook()
            ws = wb.active

            for line in lines:
                for i in range(0, len(list(Parameter_List))):
                    parseString(line, Parameter_List[i][1], Parameter_List[i][2], Parameter_List[i][0])
                for i in range(0, len(list(Status_List))):
                    parseTime(line, Status_List[i][1], Status_List[i][2], Status_List[i][0])

            for name in range(0, len(list(Parameter_List))):
                ws.append(Parameter_List[name][0])
                Parameter_List[name][0].clear()  # remember to clear the list

            for name in range(0, len(list(Status_List))):
                ws.append(Status_List[name][0])
                Status_List[name][0].clear()     # remember to clear the list

            wb.save(Summary)

            # Modify the excel file to proper type
            try:
                dataset = pd.read_excel(Summary, header=None, sheet_name=None)
                ds = dataset['Sheet']
                new_ds = ds.T
                new_ds.columns = ['JobID', 'JobName', 'User', 'Requested_Resources', 'Execute_Host', 'CPU_Time',
                                  'AVG_MEM', 'Submit', 'Running', 'Completed', 'Done']
                new_ds.to_excel(Summary, sheet_name='Sheet')
                print(sub + " 的日志信息已解析完毕···" + '\n')
            except:
                print("There exists error when construct the excel file of User " + sub)

    os.chdir(FolderName)

