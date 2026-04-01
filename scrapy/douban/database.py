#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql

# ================= 统一数据库配置区 (演示时改这里即可) =================
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306  # 统一改为 3306
MYSQL_USER = 'root'
MYSQL_PASS = '123456'
MYSQL_DB = 'flask_douban_comment'
# ======================================================================

connection = pymysql.connect(
    host=MYSQL_HOST, 
    user=MYSQL_USER,
    password=MYSQL_PASS, 
    db=MYSQL_DB,
    charset='utf8mb4',
    port=MYSQL_PORT,
    cursorclass=pymysql.cursors.DictCursor
)