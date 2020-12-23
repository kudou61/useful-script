#!/usr/bin/python

# -*- coding: utf-8 -*-

import csv
import json
import re
import os
import shutil
import codecs
import pandas as pd

# 报告csv 文件
dupfile = '/volume2/file/synoreport/daily report/2020-12-22_23-03-53/csv/duplicate_file.csv'
# 删除暂存文件夹
removeDir = '/volume2/homes/aaron/Drive/dupfile/'
# 输出日志
output_log = '/volume2/homes/aaron/Drive/dupfile/remove_log.txt'
# 文件过滤
filter_type = ['.jpg$', '.mov$', '.JPG$', '.MOV$', '.mp4$', '.MP4$']
# 路径排序优先级，优先级低的优先删除，默认为10
path_priority = {
    "Action": 1,
    "DJI": 2,
    "Camera": 3,
    "\s2.JPG": 97,
    "\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])": 98,
    "Kaiqi’s iPhone": 99,
    "dupfile": 99
}


fileData = pd.read_csv(dupfile, encoding="UTF-16", sep='\t')
reserveFile = pd.DataFrame(columns=fileData.columns.values.tolist())
removeFile = pd.DataFrame(columns=fileData.columns.values.tolist())

if  not os.path.exists(removeDir):
    os.mkdir(removeDir)
output = open(output_log, "w")    
output.writelines("开始分析重复文件\n")

def priority(path):
    priority = 10
    for key in path_priority:
        if re.search(key, path):
            priority = path_priority[key]
    return priority


def priority_array(path_array):
    sort_values = []
    for path in path_array:
        sort_values.append(priority(path))
    return sort_values

def filter_row (row):
    match = False
    for key in filter_type:
        if re.search(key,row):
            match = True
    return match

fileData['sort_val'] = priority_array(fileData['File'])
sort_file = fileData.sort_values(by=['sort_val']).drop('sort_val', 1)

for index, row in sort_file.iterrows():
    groupId = row['Group']
    size = row['Size(Byte)']
    row_path = row['File']

    needRemove = False
    if groupId in reserveFile['Group'].values and size != 0 and filter_row(row_path):
        needRemove = True
    if needRemove:
        removeFile.loc[removeFile.shape[0]] = row.values
    else:
        reserveFile.loc[reserveFile.shape[0]] = row.values

print("分析的文件数有 " + str(sort_file.shape[0]) + " 行")
output.writelines("分析的文件数有 " + str(sort_file.shape[0]) + " 行：\n")

print("需要保留的文件有 " + str(reserveFile.shape[0]) + " 行")
print(reserveFile.to_string())
output.writelines("需要保留的文件有 " + str(reserveFile.shape[0]) + " 行：\n")
output.writelines(reserveFile.to_string())
output.writelines("\n")

print("需要删除的文件有 " + str(removeFile.shape[0]) + " 行")
print(removeFile.to_string())
output.writelines("需要删除的文件有 " + str(removeFile.shape[0]) + " 行：\n")
output.writelines(removeFile.to_string())
output.close()

for index, row in removeFile.iterrows():
    file_path = row['File']
    file_name = re.search('[^/\\\\]+$', file_path).group(0)

    if not os.path.exists(file_path):
        continue

    if os.path.exists(removeDir+file_name):
        new_path = removeDir + file_name + '_' + str(index)
        shutil.move(file_path, new_path)
    else:
        shutil.move(file_path, removeDir)