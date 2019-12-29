# -*- coding: utf-8 -*-
# -*- coding: us-ascii -*-

"""
功能：获取用户的Log文件
日期：2019/12/10
作者：Bai-Yong-an
备注：暂时用不上，可以用Shell脚本进行解析，需要手动分析用户清单 namelist.txt
"""

from __future__ import print_function
import os
import sys
import multiprocessing as mp
import threading as td

def get_user_bhist_log(Number, Year, Month, User, Queue):
    try:
        os.system(r'''bhist -n {0} -S {1}/{2} -u {3} -a -l -q {4}|
                          tr '\n' ' '| sed 's/ //g' | sed 's/------Job</\nJob</g' \
                          >> bhist-{4}-{1}-{2}-{3}.log'''.format(Number, Year, Month, User, Queue))
    except:
        pass

def main():
    Number = 1000
    Year = [2017, 2018, 2019]
    Month = [i for i in range(1, 13)]
    User = ['60056206']
    Queue = ['CST']

    os.mkdir("{0}-{1}-{2}".format(Queue[0], Year[2], User[0]))
    os.chdir("{0}-{1}-{2}".format(Queue[0], Year[2], User[0]))
    for i in Month:
        # thread = td.Thread(target=get_user_bhist_log, args=(Number, Year[2], i, User[0], Queue[0]))
        # thread.start()
        p1 = mp.Process(target=get_user_bhist_log, args=(Number, Year[2], i, User[0], Queue[0]))
        p1.start()

if __name__ == '__main__':
    main()
