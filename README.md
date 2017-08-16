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

## Usage
### Configuration creation
![Image of Configuration writer](https://s3-us-west-2.amazonaws.com/jlovick-gis/mysql_importer/config_window.jpg)

Upon populating the mysql password field, the tool will connect to the database and download a list of tables, and will choose the first to further list the fields of that table. Mysql views, are treated as tables and can be used in the same manor.

![Image of list of Table](https://s3-us-west-2.amazonaws.com/jlovick-gis/mysql_importer/config-2.jpg)

you can change the table to import by replacing the Mysql table to convert text.

Most of the tools use Latitude Longitude coordinates in line with a WGS 1984 spatial reference system, coded as 4326, if however your data is in an alternate system you can change the code ( http://spatialreference.org/ ) is a good source for alternate projection codes.

**Neither** the tables *availible* list or the *columns to be imported* list currently allow user interaction and are included for reference puropses only.

When you are satisfied you have the correct table, and coordinate system, choose a file to save the configuration to, by default no file extension is selected, however as this file is in YAML format, **.yml** is not a bad choice.

```
---
database: ant
fields:
- from: int(10) unsigned
  geometry: false
  import: true
  name: id
  to: LONG
- from: double
  geometry: false
  import: true
  name: Lat
  to: DOUBLE
- from: double
  geometry: false
  import: true
  name: Long
  to: DOUBLE
file_has_geometry: true
host: orca.anatexis.net
password: my_not_secret_password
referencesystem: '4326'
port: '3306'
table: spatial_point_lat_long
user: jlovick
---
```
The congfiguration file will need to be edited if you wish to exclude a column.
```
import: false
```
or if you have multiple geometry columns, you will need to pick one.
Finally if you are unhappy about the field conversion type choosen, you can change it 

### Importing a table


