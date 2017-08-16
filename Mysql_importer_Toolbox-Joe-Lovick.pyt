import arcpy
import contextlib
import math
import os
import re
import time
import logging
import mysql
import yaml
import datetime
from mysql.connector import errorcode
#from mysql_interface import MysqlInterface


class MysqlInterface(object):
    def __init__(self,  host, port, user, password, database):
        self.connection = None
        self.cursor = None
        self.tables = None
        self.connect( host, port, user, password, database)
        


    def connect(self, host, port, user, password, database):
        try:
            logging.info("connetion info : user {0}, pw {1}, host {2}, port {3}, database {4}".format(user,password,host,port,database ))
            self.connection = mysql.connector.connect(user = user,
                                                      password = password,
                                                      host = host,
                                                      port = port,
                                                      database= database,
                                                      raise_on_warnings= True )
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
            else:
                logging.error("Other Error in connecting {0}".format(err))
        else:
            pass

    def list_tables(self):
        try:
            logging.info("list tables")
            self.cursor = self.connection.cursor()
            query = "SHOW TABLES"
            if not hasattr(self.cursor,'execute'):
                logging.error(" connection does not exist,no execute method ")
                return
            self.cursor.execute(query)

            tp = self.cursor.fetchall()
            self.tables =  [i[0] for i in tp]
            logging.info(" cursor returned :{0}".format( self.tables ))
            return self.tables

        except Exception as e:
            logging.error("error in querying tables {0}".format(e))
            raise e
        finally:
            del self.cursor

    def describe_table(self, tablename):
        try:
            logging.info("describe table")
            self.cursor = self.connection.cursor()
            query = "DESCRIBE {0}".format(tablename)
            if not hasattr(self.cursor,'execute'):
                logging.error(" connection does not exist,no execute method ")
                return
            self.cursor.execute(query)

            tp = self.cursor.fetchall()
            self.tables =  ["{0} - {1}".format(i[0],i[1]) for i in tp]
            logging.info(" describe table returned :{0}".format( self.tables ))
            return self.tables

        except Exception as e:
            logging.error("error in querying tables {0}".format(e))
            raise e
        finally:
            del self.cursor

    def read_table(self, tablename, fields):
        try:
            logging.info(" read table {0}".format(tablename))
            self.cursor = self.connection.cursor()
            query = "SELECT {0} FROM {1}".format( fields, tablename)
            logging.info(" Query is :{0}".format(query))
            if not hasattr(self.cursor,'execute'):
                logging.error(" connection does not exist,no execute method ")
                return
            self.cursor.execute(query)

            self.tables =  self.cursor.fetchall()
            logging.info(" read table returned :{0} records".format( len(self.tables) ))
            return self.tables

        except Exception as e:
            logging.error("error in read tables :{0}".format(e))
            raise e
        finally:
            del self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
            logging.info("destroying mysql connection")
            self.connection.close()


class BaseTool(object):
    def __init__(self):
         self.named_parameters = {}

    def deleteFC(self, fc):
        if arcpy.Exists(fc):
            arcpy.management.Delete(fc)

    def  getParamProto(self,
                         name="name",
                         display_name="Label",
                         value="",
                         required="Required",
                         datatype="String",
                         multiValue=False,
                         direction="Input"):
        #if multiValue and datatype=="String": #multivalue strings dont work see #https://gis.stackexchange.com/questions/139307/creating-list-of-strings-as-parameter-to-python-script-tool
        #    datatype = "GPType"

        param = arcpy.Parameter(
            name=name,
            displayName=display_name,
            direction= direction,
            datatype= datatype,
            parameterType=required,
            multiValue=multiValue
            )
        param.value = value
        return param

    def getParamString(self,
                         name="name",
                         display_name="Label",
                         value="",
                         required="Required",
                         multiValue=False,
                         direction="Input"):
        return self.getParamProto(name=name,
                         display_name=display_name,
                         value=value,
                         required=required,
                         datatype="String",
                         multiValue=multiValue,
                         direction=direction)
        

    def getParamBoolean(self,
                        name="name",
                        display_name="Label",
                        value=False,
                        required="Required",
                        direction="Input"):    
         return self.getParamProto(name=name,
                         display_name=display_name,
                         value=value,
                         required=required,
                         datatype="Boolean",
                         direction=direction)


    def getParamFC(self):
        output_fc = arcpy.Parameter(
            name="output_fc",
            displayName="output_fc",
            direction="Output",
            datatype="Feature Layer",
            parameterType="Derived")
        return output_fc

    def remap_params(self, parameters):
        try:
            # save all parameters to the configuration file so it is ready to be edited
            self.named_parameters = {}
            params = range(len(parameters))
            for pi in params:
                logging.info(" remapping parameters {0}".format(pi))
                self.named_parameters[ parameters[pi].name ] = parameters[pi]
            return
        except:
            e = sys.exc_info()[0]
            logging.exception(' error remapping parameters : {0}'.format(e))
            raise

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        logging.info("update params super")
        logging.info(" update params child")
        self.remap_params(parameters)
        return

    def updateMessages(self, parameters):
        return


class Toolbox(object):
    def __init__(self):
        self.label = "MysqlImportToolbox"
        self.alias = "MysqlImportToolbox"
        self.tools = [MysqlImportTool_configuration,  MysqlImportTool]

        tempdir = os.environ['TEMP']
        fname =   'D:\GIS_DATA\Advanced_Python\Final Project\myapp.log' # "{0}\mysql_import.log".format(tempdir) 
        #truncate log file before we start
        fo = open(fname,'w')
        fo.truncate()
        fo.close

        logging.basicConfig(filename=fname,
                            format='%(levelname)s %(message)s',
                            level=logging.DEBUG)
        logging.info('Started, {0}'.format( time.strftime("%c") ))
        


class MysqlImportTool_configuration(BaseTool):
    def __init__(self):
        super(MysqlImportTool_configuration, self).__init__()
        self.label = "Mysql Import Tool configuration creator"
        self.description = "Tool to query a mysql database and import tables, writes configuration to file [for further refinement]"
        self.canRunInBackground = True
        self.mysql_obj = {}
        self.geometry_assigned = False

    def getParameterInfo(self):
        UP = os.environ['USERPROFILE']
        
        params = [#  self.getParamProto(name="configuration", display_name="Load configuration from file [to edit]", value="{0}\Desktop".format(UP), required="Optional", datatype="File"),
                  #  self.getParamBoolean(name="UseConfiguration",display_name="Use Configuration file",value=False, required="Required"),
                    self.getParamString(name="host", display_name="mysql host", value="orca.anatexis.net", required="Required"),
                    self.getParamString(name="port", display_name="mysql listening on port ", value="3306", required="Required"),
                    self.getParamString(name="user", display_name="Mysql Username", value="jlovick", required="Required"),
                    self.getParamString(name="database", display_name="Database to connect to", value="ant", required="Required"),
                    self.getParamString(name="password", display_name="Mysql Password", value="", required="Required"),
                    self.getParamString(name="tables", display_name="Tables availible [type wanted table below]", value="", required="Optional", multiValue=True),
                    self.getParamString(name="table", display_name="Mysql table to convert", value="", required="Required"),
                    self.getParamString(name="referencesystem", display_name="Coordinate System Code [4326 is WGS1984]", value="4326", required="Required"),
                    self.getParamString(name="columns", display_name="these columns will be imported", value="", required="Optional", multiValue = True),
                    self.getParamProto(name="saveconfiguration", display_name="Save configuration to file", value="{0}\Desktop".format(UP), required="Required", datatype="File", direction="Output"),
                    ]
        
        return params
  


    # def configuration_change(self):
    #     logging.info("configuration change")
        
    # def useconfiguration_change(self):
    #     logging.info("configuration change")
        
    def host_change(self):
        logging.info("host change")
        if not len( self.named_parameters["host"].value) > 2 :
            logging.info("host name not valid ")
            arcpy.messages.addErrorMessage("no host name.")
            raise arcpy.ExecuteError
            return
        self.user_change()
        
    def user_change(self):
        logging.info("user change")
        if not len( self.named_parameters["user"].value) > 0 :
            logging.info("user name not valid ")
            return
        self.port_change()
        
    def port_change(self):
        logging.info("port change")
        try:
            prt = int(self.named_parameters["port"].value)
        except ValueError:
            logging.info("port number not valid ")
            return
        self.database_change()
        
    def database_change(self):
        logging.info("database change")
        if not len( self.named_parameters["database"].value) > 0 :
            logging.info("database not valid ")
            return
        self.password_change()

    def password_change(self):
        logging.info("password change")
        try:
            if not len( self.named_parameters["password"].value) > 0 :
                logging.info("database not valid ")
                return
        except TypeError:
            #at initializatation hidden strings are set to none
            logging.info("password is not valid ? none? ")
            return
        try:
            self.mysql_obj = MysqlInterface(        host = self.named_parameters["host"].value,
                                          port = self.named_parameters["port"].value,
                                          user = self.named_parameters["user"].value,
                                          password = self.named_parameters["password"].value,
                                          database = self.named_parameters["database"].value)
            logging.info("Connected OK")
            table = self.mysql_obj.list_tables()
            
            self.named_parameters["tables"].value = ";".join(table) # cant set value... because its a copy?
            if (self.named_parameters["table"].value == None):
                self.named_parameters["table"].value = table[0]
        except:
            e = sys.exc_info()[0]
            logging.exception('password change threw an error. {0}'.format(e))
            #clear downwind
            self.named_parameters["tables"].value = ""
            self.named_parameters["columns"].value = ""
            self.named_parameters["password"].setErrorMessage(e) # for some reason this does nothing
            

    def tables_change(self):
        # we dont use this control for anything bu helping the user
        logging.info(" We have the following values {0}".format(self.named_parameters["tables"].valueAsText ))
        

        pass
    def table_change(self):
        logging.info("table change")
        try:
            # query mysql for the table description and then populate colunms
            table = self.named_parameters["table"].value
            logging.info(" working with table {0} ".format(table))
            fields = self.mysql_obj.describe_table(table)
            self.named_parameters["columns"].value = ";".join(fields)
        except:
            e = sys.exc_info()[0]
            logging.exception('table change threw an error. {0}'.format(e))
            #clear downwind values
            self.named_parameters["columns"].value = ""
    def columns_change(self):
        logging.info("columns change")
    def saveconfiguration_change(self):
        logging.info("save configuration change")
    def saveconfigurationnow_change(self):
        logging.info("save configuration now change")
    def referencesystem_change(self):
        logging.info("reference system change")
      

    def updateParameters(self, parameters, messages):
        try:

            super(MysqlImportTool_configuration, self).updateParameters(parameters)
            logging.info(" update params child")
  #          self.remap_params(parameters)

            for pi in range(len(parameters)):
                #go through trigger change code for each control
                if (parameters[pi].altered):
                    getattr( self , "{0}_change".format( parameters[pi].name.lower() ))() #this doesnt work, if were call self do no know why
           
            return
        except:
            e = sys.exc_info()[0]
            logging.exception('Update Parameters threw an error. {0}'.format(e))
            raise
    def convert_field_type(self, intype):
        try:
            dswap = {   "int": "LONG",
                        "integer": "LONG",
                        "smallint": "LONG",
                        "tinyint": "LONG",
                        "mediumint": "LONG",
                        "bigint": "LONG",
                        "double": "DOUBLE",
                        "decimal": "DOUBLE",
                        "numeric": "DOUBLE",
                        "float": "DOUBLE",
                        "varchar": "TEXT",
                        "text": "TEXT",
                        "year" : "LONG",
                        "time" : "DATE",
                        "date" : "DATE",
                        "datetime" : "DATE",
                        "timestamp": "DATE", #need to check this one
                        "point" : "POINT",
                        "polygon" : "POLYGON",
                        "linestring":"POLYLINE",
                        "geometry":"MULTIPATCH"
                      }
                      
            it = intype.strip()
            otype= "UNKNOWN"
            it = re.sub("unsigned","", it)
            it = re.sub("\(|\)|\d+","", it)
            it = it.strip()
            if it in dswap:
                otype = dswap[it]
            else:
                otype = "UNKNOWN"
            logging.info(" matching {0} --> {1}".format(it, otype))
            return otype
        except:
            e = sys.exc_info()[0]
            logging.exception('Convert Field Type thew an error. {0}'.format(e))
            raise
    def is_geometry_field(self, field):
        try:
            logging.info("is geometry called")
            geometry_list = [   "geometry",
                                "point",
                                "linestring",
                                "polygon",
                                "multipoint",
                                "multilinestring",
                                "multipolygon",
                                "geometrycollection"    ]
            if not field.lower().strip() in geometry_list:
                return False
            if not self.geometry_assigned:
                self.geometry_assigned = True
                return self.geometry_assigned
            else:
                return False
        except:
            e = sys.exc_info()[0]
            logging.exception('Convert Field Type thew an error. [{0}] {1}'.format(field,e))
            raise
    def execute(self, parameters, messages):
        try:
            # save all parameters to the configuration file so it is ready to be edited
            self.remap_params(parameters)
            file_has_geometry = False
            configuration = {}
            configuration["host"] = str(self.named_parameters["host"].value)
            configuration["port"] = str(self.named_parameters["port"].value)
            configuration["user"] = str(self.named_parameters["user"].value)
            configuration["password"] = str(self.named_parameters["password"].value)
            configuration["database"] = str(self.named_parameters["database"].value)
            configuration["table"] = str(self.named_parameters["table"].value)
            configuration["referencesystem"] = str(self.named_parameters["referencesystem"].value)
            raw_fields = self.named_parameters["columns"].values

            fields= []
            for j in raw_fields:
                logging.info("fields {0}".format(j))
                name = str(j.split("-")[0]).strip()
                dtype =  str(j.split("-")[1]).strip()
                logging.info("to {0} ....... {1}".format(name,dtype))
                fields.append({ "name": name, "from": dtype, "to": self.convert_field_type(dtype), "geometry": self.is_geometry_field(dtype), "import": True} )
            
            configuration["fields"] = fields
            configuration["file_has_geometry"] = self.geometry_assigned
            yaml_str= yaml.dump(configuration, explicit_start = True, default_flow_style=False)
            logging.info("{0}".format(yaml_str))
            fn = self.named_parameters["saveconfiguration"].valueAsText
            f = open(fn, 'a')
            f.write(yaml_str)
            f.close
            arcpy.AddMessage("please check it {0}\n\n".format(yaml_str))
            arcpy.AddMessage("Successfully written configuration file")
            arcpy.AddMessage("please check it {0}".format(fn))
            arcpy.AddMessage("Finnished")
        except Exception as e:
            ri = sys.exc_info()[0]
            arcpy.AddError("error :{0}\n{1}".format(str(e),ri))



class MysqlImportTool(BaseTool):
    def __init__(self):
        super(MysqlImportTool, self).__init__()
        self.label = "Mysql Import Tool"
        self.description = "Tool to query a mysql database and import tables"
        self.config = {}
        self.insert_details = []
        self.mysql_obj = None
        self.field_order = []

    def getParameterInfo(self):
        UP = "" # os.environ['USERPROFILE']  
        params = [  self.getParamProto(name="configuration", display_name="Load configuration from file ", value="{0}".format(UP), required="Required", datatype="File"),
                    self.getParamProto(name="output", display_name="output dataset", value="{0}".format(UP), datatype="File", required="Required", direction="Output"), 
                    self.getParamString(name="table", display_name="FYI: Importing this table", value="", required="Optional", multiValue=True),
                    ]
        return params

    def load_config(self):
        try:
            fn = self.named_parameters["configuration"].valueAsText
            with open(fn) as conf:
                self.config = yaml.load(conf)
        except:
            e = sys.exc_info()[0]
            logging.exception('load config threw an error. {0}'.format(e))
            raise            
    def configuration_change(self):
        try:
            self.load_config()
            self.mysql_obj = MysqlInterface(  host = self.config["host"],
                                              port = self.config["port"],
                                              user = self.config["user"],
                                              password = self.config["password"],
                                              database = self.config["database"])
            logging.info("Connected OK")
            fields = self.mysql_obj.describe_table(self.config["table"])
            self.named_parameters["table"].value = ";".join(fields)
            #if ((self.named_parameters["name"].value == None) or (len(self.named_parameters["name"].value) == 0)):
            #    self.named_parameters["name"].value = self.config["table"]
        except:
            e = sys.exc_info()[0]
            logging.exception('Update Parameters threw an error. {0}'.format(e))
            raise
    def output_change(self):
        pass
    def table_change(self):
        pass


    def updateParameters(self, parameters):
        try:
            super(MysqlImportTool, self).updateParameters(parameters)
            for pi in range(len(parameters)):
                #go through trigger change code for each control
                if (parameters[pi].altered):
                    getattr( self , "{0}_change".format( parameters[pi].name.lower() ))() #this doesnt work, if were call self do no know why
            return
        except:
            e = sys.exc_info()[0]
            logging.exception('Update Parameters threw an error. {0}'.format(e))
            raise

    def setup_new_table(self, fc, ws,name):
        try:
            
            self.insert_details = []
            geometry = None
            fields = self.config["fields"]
            logging.info(" fields : {0}".format(fields))
            for field in fields:
                if field["import"]:
                    if field["geometry"]:  geometry = field["to"]
            
            sr = arcpy.SpatialReference(self.config["referencesystem"])
            

            if  geometry is None:           
                arcpy.CreateTable_management(ws, name)
            else:  
                logging.info("create new feacture clase {0},{1},{2}".format(ws,name,geometry))
                arcpy.management.CreateFeatureclass(ws, name, geometry,spatial_reference=sr)

            for field in fields:
                if field["import"]:
                    
                    if not field["geometry"]:
                        self.field_order.append( "`{0}`".format(field["name"]))
                        arcpy.AddField_management(fc, field["name"], field["to"])
                        self.insert_details.append(field["name"] )
                        logging.info("insert description {0} --> {1}".format(field["to"],field["name"]))
                    else:
                        self.field_order.append( "ST_AsText(`{0}`)".format(field["name"]))
                        self.insert_details.append("SHAPE@WKT")
            logging.info("insert description {0}".format(self.insert_details))
        except:
            e = sys.exc_info()[0]
            logging.exception('Setup new table threw an error. {0}'.format(e))
            raise
    def populate_table(self, fc):
        try:
            if self.mysql_obj is None:
                self.mysql_obj = MysqlInterface(  host = self.config["host"],
                                                  port = self.config["port"],
                                                  user = self.config["user"],
                                                  password = self.config["password"],
                                                  database = self.config["database"])
            field_order_string = (",").join(self.field_order)
            data = self.mysql_obj.read_table(self.config["table"], field_order_string)
            logging.info(" insert_details = {0}".format(self.insert_details))

            #fixme this nasty nasty hack
            # da.insert_cursor has difficulties causeing system error without exception
            if self.config["file_has_geometry"]:
                with arcpy.da.InsertCursor(fc, self.insert_details) as insert_cursor:
                    for row in data:
                       logging.info(" row data = {0}".format(row))
                       insert_cursor.insertRow(row)
            else:
                rows  = arcpy.InsertCursor(fc)
                for ndata in data:
                    ndata = list( ndata )
                    row = rows.newRow()
                    for x in range(len(self.insert_details)):
                        logging.info("description : {0} , data: {1}".format(self.insert_details[x], ndata[x]))
                        row.setValue(self.insert_details[x], ndata[x])
                    rows.insertRow(row)
                del rows
        except:
            e = sys.exc_info()[0]
            logging.exception('Setup new table threw an error. {0}'.format(e))
            raise

    def execute(self, parameters, messages):
        try:
            self.remap_params(parameters)
            self.load_config()
            MXD = arcpy.mapping.MapDocument("CURRENT")
            DF = arcpy.mapping.ListDataFrames(MXD, '*')[0]

            name =  os.path.basename(self.named_parameters["output"].valueAsText)
            
            fc = self.named_parameters["output"].valueAsText
            ws = os.path.dirname("{0}".format(fc))

            arcpy.AddMessage("writing out to file")
            if self.config["file_has_geometry"]:
                new_extension = "shp"
            else:
                new_extension = "dbf"
            filename, file_extension = os.path.splitext(fc) # rip off existing extension and dont use it
            full_fc = "{0}.{1}".format(filename,new_extension)

            arcpy.AddMessage("fc : {0}, full_fc:{1} ws : {2}".format(fc, full_fc, ws))
            self.setup_new_table(full_fc, ws, name)
            self.populate_table(fc)

            if self.config["file_has_geometry"]:
#                arcpy.mapping.AddLayer(DF, fc, "AUTO_ARRANGE")
                arcpy.RefreshActiveView()
            else:
#                arcpy.mapping.AddTableView(DF, fc)
                pass
            del fc
            del DF
            del MXD
        except:
            e = sys.exc_info()[0]
            logging.exception('Execute threw an error. {0}'.format(e))
            raise