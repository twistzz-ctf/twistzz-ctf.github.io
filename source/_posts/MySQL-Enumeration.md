---
title: MySQL Enumeration
date: 2025-11-21 01:01:33
categories:
  - Active Directory
  - Enumeration
  - Service-Enumeration
  - MySQL
tags:
  - MySQL
  - Enumeration

cover: /img/mysql-en.png
top_img: /img/bg-img.jpg
description: Enumerate MySQL.
---



# Connect To The Server

### mysql

```bash
mysql -u username -p<password> -h target
```


# Enumerate Version

```sql
SELECT @@version;
```

# Enumerate Database

### List Databases

```sql
SHOW DATABASES; 

SELECT SCHEMA_NAME FROM information_schema.SCHEMATA;
```
### Check Current Database

```sql
SELECT DATABASE();
```

### List tables in current database  

```sql
SHOW TABLES;  
SELECT table_name FROM information_schema.TABLES WHERE table_schema=DATABASE();  
```
### List columns in specific table  

```sql
SHOW COLUMNS FROM table_name;  
SELECT column_name, data_type FROM information_schema.COLUMNS WHERE table_name='users';  
```
### Find sensitive columns  

```sql
SELECT table_name, column_name FROM information_schema.COLUMNS  
WHERE column_name LIKE '%password%'  
OR column_name LIKE '%pass%'  
OR column_name LIKE '%pwd%'  
OR column_name LIKE '%secret%'  
OR column_name LIKE '%token%';  
```
### Count rows in tables  

```sql
SELECT table_name, table_rows FROM information_schema.TABLES  
WHERE table_schema = DATABASE();
```




# Users Enumeration


#### List MySQL users

```sql
SELECT user, host FROM mysql.user;
```

#### Check Current User  

```sql
SELECT USER();  
SELECT CURRENT_USER();
```

#### List users with FILE privilege  

```sql
SELECT user, host FROM mysql.user WHERE File_priv = 'Y';  
```

Or

```sql
SELECT file_priv FROM mysql.user WHERE user='current_user';
```
#### List users with SUPER privilege  

```sql
SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';
```

