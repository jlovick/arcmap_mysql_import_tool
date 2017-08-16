# Readme  

## Background
MySQL and its open source sibling MariaDB are the dominant web connected database systems used in the LAMP stack, though their spatial support is poor. I have encountered a number of situations where spatial columns (typically point data) are appended to legacy systems to provide minimal geospatial support in web applications. Thus there is significant need for a import capability from the database but currently ArcGIS mostly ignores this database (perhaps due to its poor spatial capabilities), and instead encourages people to use a fully integrated geospatial database connection like SQL server or PostGIS, and the Enterprise version of ArcMap; frequently this is overkill for simple problems, this script is designed to meet the needs of users who do not need an enterprise level solution. 

This tool provides a way of importing MySQL data into ArcMap. It provides this in a two prong approach. First a configuration creator tool, takes information about a connection to the database, and a table and creates from this a configuration YAML file that is easy to read and understand. A second tool  then takes that configuration file and then import the data, either into a feature class [if geospatial data is present] or into a table.

## Requirements
This tool expects the enviroment variable TEMP to be declared and pointing to a location the user has write access to, this should be default on most windows systems.

the oracle python mysql connector should be installed, https://dev.mysql.com/downloads/connector/python/
```
pip install mysql-connector-python-rf
```
the python YAML library is also neccesary
```
pip install PyYAML
```
You also need a mysql database that is accessible via the network , (no local sockets) to enable such a setup perhaps use http://sogoth.com/?p=99 though windows users may need to hunt to find their copy of my.cnf

You will need ArcMap version 10.1 or greater.

to use the tool you will need to know

*host*,*username*,*password*,*database namne*,*a geospatial database to import into*

## Installation
Copy the Mysql_importer into a suitble location, or get it out from github and place it directly where you want it, https://github.com/jlovick/arcmap_mysql_import_tool/archive/master.zip 

load up ArcMap, and confirm that you can find the toolbox in your file system.

