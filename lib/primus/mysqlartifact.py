#       
#       Copyright 2009 Andrei <vish@gravitysoft.org>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os
import ConfigParser
        
from artifactcore import Artifact, ShellScriptHelper
from fileartifact import FileArtifact, PermanentFileArtifact

class DBModuleException(BaseException):
    def __init__(self, msg):
        BaseException.__init__(self, msg)
        

def load_mysql_parameters(obj, config_path, section = 'DEFAULT'):   
    if not os.path.isabs(config_path):
        config_path = os.path.join(Artifact.home_dir(), config_path)
   
    if not os.path.exists(config_path) : 
        raise IOError("Configuration file '%s' cannot be found." % config_path)
    c = ConfigParser.ConfigParser()
    c.read([config_path])
    obj.username = c.get(section, 'user') 
    obj.password = c.get(section, 'passwd')
    obj.hostname = c.get(section, 'host')
    obj.dbname   = c.get(section, 'db')
            
def mysql_connect(config):
    assert config    
    class dbinfo(object): pass
    
    config_name = config[0]
    sections    = config[1]
    errors      = []
    if isinstance(sections, list) == False: sections = [ sections ]
    
    for section in sections:
        data = dbinfo()
        load_mysql_parameters(data, config_name, section)
        try:
            import MySQLdb
            conn = MySQLdb.connect (host   = data.hostname,
                                    user   = data.username,
                                    passwd = data.password)
            return conn
        except ImportError, e:
            raise DBModuleException("MySQL Python database module (MySQLdb) has not been found.") 
        except Exception, e: 
            errors.append(str(e))

    raise BaseException("Cannot connect to DB:\n%s " % '\n'.join(errors))
    
        
class CheckDBEnvironment(Artifact):
    class VersionException(BaseException):
        def __init__(self, msg):
            BaseException.__init__(self, msg)
        
    def __init__(self, name=":checkmysql", config=('.primus/deploy.conf', 'DBADMIN'), required_version=(5,0)):
        assert config
        Artifact.__init__(self, name)
        self.required_version = required_version
        self.config = config
        
    def build(self):
        conn = None
        try:
            conn = mysql_connect(self.config)
            cursor = conn.cursor ()
            cursor.execute ("SELECT VERSION()")
            row = cursor.fetchone()
            version = (int(row[0].split('.')[0]), int(row[0].split('.')[1]))
            if version < self.required_version:
                raise CheckDBEnvironment.VersionException("MySQL Data base server is too old (%s). Version '%s' is required." % (version, self.required_version)) 

            cursor.close ()
        finally: 
            if conn != None: conn.close()         
    
    def what_it_does(self):
        return "Check if MySQL version >= %s.%s" % (str(self.required_version[0]), str(self.required_version[1]))


class LoadDBSchema(PermanentFileArtifact):
    def __init__ (self, name, config=('.primus/deploy.conf', 'DEFAULT'), dependencies=[]):
        PermanentFileArtifact.__init__(self, name, dependencies)        
        if os.path.isdir(self.fullpath()): 
            raise BaseException("Script cannot be a directory '%s'" % self.fullpath())
        
        load_mysql_parameters(self, config[0], config[1])
        
    def cleanup(self):
        script = "grep -i '^DROP TABLE' '%s' | mysql --host='%s' --user='%s' --password='%s' %s" % (self.fullpath(),
                                                 self.hostname, 
                                                 self.username,
                                                 self.password, 
                                                 self.dbname)
        ShellScriptHelper.run(script)
          
    def build(self):
        path = self.fullpath()
        if not os.path.exists(path):
            raise IOError("Script '%s' doesn't exist." % (path))
        
        script = "mysql --host='%s' --user='%s' --password='%s' %s < %s" % (self.hostname, 
                                                 self.username,
                                                 self.password, 
                                                 self.dbname,   
                                                 self.fullpath())
        ShellScriptHelper.run(script)          
                
    def what_it_does(self):
        return "Deploy DB schema '%s'" % self.name
        
        
class CreateDB(Artifact):
    def __init__(self, config=('.primus/deploy.conf', 'DBADMIN', 'DEFAULT'), dependencies=[]):
        Artifact.__init__(self, ':createdb', dependencies)
        load_mysql_parameters(self, config[0], config[2])
        class Credentials(object) : pass
        self.credentials = Credentials()
        load_mysql_parameters(self.credentials, config[0], config[1])
    
    def build(self):            
        mysql = "mysql -h %s -u%s" % (self.credentials.hostname, self.credentials.username)
        if self.credentials.password != None and len(self.credentials.password.strip()) > 0: 
            mysql = mysql + " -p" + self.credentials.password 

        # create data base
        create_db_cmd = "echo 'CREATE DATABASE IF NOT EXISTS %s;' | %s" % (self.dbname, mysql)
        try: ShellScriptHelper.run(create_db_cmd)
        except: 
            return False
            #raise BaseException("Cannot create '%s' data base." % self.dbname)  
            
        # grant permission
        create_db_cmd = "GRANT ALL ON %s.* TO '%s'@'%s'" % (self.dbname, self.username, self.hostname)
        if self.password != None and len(self.password.strip()) > 0: 
            create_db_cmd = create_db_cmd + (" IDENTIFIED BY '%s'" % self.password)

        create_db_cmd = "echo \"%s;\" | %s"  % (create_db_cmd, mysql) 
        try: ShellScriptHelper.run(create_db_cmd) 
        except: 
            return False
            #raise BaseException("Cannot grant permission to '%s' data base." % self.dbname)
        
        return True

    def what_it_does(self):
        return "Create MySQL DB: %s" % self.dbname
        
        
class CheckDBSchema(Artifact):
    def __init__(self, config=('.primus/deploy.conf', 'DEFAULT'), tables=(), dependencies=[]):
        Artifact.__init__(self, ':checkdbschema',  dependencies)
        load_mysql_parameters(self, config[0], config[1])
        assert tables and len(tables) > 0
        self.tables = tables
     
    def build(self):        
        conn = None
        import MySQLdb
        try:
            conn = MySQLdb.connect (db     = self.dbname,
                                    host   = self.hostname,
                                    user   = self.username,
                                    passwd = self.password)
            # if one of the table exists schema should not be touched
            for table in self.tables:
                if self._table_exists(conn, table) >= 0: return True
        finally: 
            if conn != None: conn.close()
        return False        

    def what_it_does(self):
        return "Check if '%s' MySQL DB schema exists." % self.dbname

    def _table_exists(self, conn, table_name):
        cur = None
        try:
            sql = "SELECT count(*) FROM %s" % table_name
            cur = conn.cursor()
            res = cur.execute(sql)
            return res
        except:
            return -1
        finally: 
            if cur : cur.close()    
    
    
class TestDBExistance(Artifact):
    def __init__(self, config=('.primus/deploy.conf', 'DEFAULT'), dependencies=[]):
        Artifact.__init__(self, ':checkdb',  dependencies)
        load_mysql_parameters(self, config[0], config[1])

    def build(self):  
        conn = None
        import MySQLdb
        try:
            conn = MySQLdb.connect (db     = self.dbname,
                                    host   = self.hostname,
                                    user   = self.username,
                                    passwd = self.password)
        except: 
            return False  
        finally: 
            if conn != None: conn.close()
        return True        

    def what_it_does(self):
        return "Check if '%s' MySQL DB exists." % self.dbname
