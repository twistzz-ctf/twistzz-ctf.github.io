---
title: Mssql Enumeration
date: 2025-11-20 18:59:31
categories:
  - Active Directory
  - Enumeration
  - Service-Enumeration
  - MSSQL
tags:
  - Enumeration
  - MSSQL
---

# Connect To The Data Base

## SQL Authentication

### Windows

##### sqlcmd

```cmd
sqlcmd -S target -U username -P 'password' -y 30 -Y 30
```

### Linux

##### sqsh

```bash
sqsh -S target -U username -P 'password' -h
```

##### mssqlclient

```bash
impacket-mssqlclient username@target
```

## Windows Authentication (Local Account)

### Linux

##### sqsh

```bash
sqsh -S target -U .\\username -P 'password' -h
```

```bash
sqsh -S target -U HOSTNAME\\username -P 'password' -h
```

##### mssqlclient

```bash
impacket-mssqlclient username@target -windows-auth
```

## Domain Authentication (With DC)

### Linux

##### sqsh

```shell
sqsh -S target -U domain\username -P password
```

##### mssqlclient

```bash
impacket-mssqlclient domain/username:password@target
```

# Enumerate Data Base

## Windows

### sqlcmd

When using `sqlcmd`, each query must be followed by `GO` to trigger its execution.

##### List Databases

```powershell
1> SELECT name FROM master.dbo.sysdatabases
2> GO
```

##### Select Database

```powershell
1> USE htbusers
2> GO
```

##### List Tables

```powershell
1> SELECT table_name FROM htbusers.INFORMATION_SCHEMA.TABLES
2> GO
```

##### Dump Specific Table

```powershell
1> SELECT * FROM users
2> go
```

## Linux

### Mssqlclient

##### List Databases

```bash
SQL (htbdbuser  guest@master)> SELECT name FROM sys.databases;
```

##### Select Database

```bash
SQL (htbdbuser  guest@master)> use database-name
```

##### List Tables

```bash
SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

##### Dump Specific Table

```bash
mysql> SELECT * FROM table-name;
```
