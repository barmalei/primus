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
import shutil
import ConfigParser

from artifactcore import Artifact, LoggableArtifact, Project 
from fileartifact import PermanentFileArtifact


class Configure(PermanentFileArtifact, LoggableArtifact):
    def __init__ (self, name=".primus/deploy.conf", configs = [], dependencies = []):
        PermanentFileArtifact.__init__(self, name, dependencies) 
        LoggableArtifact.__init__(self)
        self.target = configs
     
    def cleanup(self):
        # has to restore updated config to initial state 
        files_map = self.read_log()
        for original in files_map:
            if os.path.exists(original) and os.path.exists(files_map[original]):
                shutil.copy(files_map[original], original)    
            else:
                self.msg("File '%s' or\n     '%s' cannot be found." % (original, files_map[original]))        
                      
        self.cleanup_log()

    def build(self):    
        self.cleanup_log()
        config_path = self.fullpath()
        source_conf = ConfigParser.ConfigParser({'home_dir':Artifact.home_dir()})     
        source_conf.read([config_path])
                        
        for conf_file in self.generator():
            self.configure(source_conf, conf_file)            
 
    def _backup_file(self, path):
        dest_path = path + ".prev"  
        shutil.copy(path, dest_path)
        
        map = self.read_log();
        map[path] = dest_path
        self.write_log(map)
  
    def configure(self, source_conf, conf_file):            
        pkg_conf = ConfigParser.ConfigParser()
        pkg_conf.read([conf_file])
        
        for section in pkg_conf.sections():
            src_section = section                 
            if not source_conf.has_section(section):
                src_section = 'DEFAULT'

            for option in pkg_conf.options(section):    
                if source_conf.has_option(src_section, option):
                    pkg_conf.set(section, option, source_conf.get(src_section, option))
                else:
                    if option.find("__") != 0: pass
                        #!!!self.msg("Option '%s:%s' is not defined in deployment config." % (section,option))
                        #!!!self.msg("Keep this option value as is ('%s')." % pkg_conf.get(section, option))
                      
        self._backup_file(conf_file)  
        f = open(conf_file, 'w') 
        try: pkg_conf.write(f)    
        finally: f.close()
    
    def generator(self): 
        for conf in self.target:
            conf = os.path.join(Artifact.home_dir(), conf)
            yield conf
                
    def what_it_does(self):
        return "Update configurations: '%s'" %  ", ".join(self.target)
   
   
