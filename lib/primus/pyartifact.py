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

import sys
import os
import re
import py_compile
import shutil

from artifactcore import Artifact
from fileartifact import PermanentFileArtifact, ShellScriptHelper, RmFile, FileArtifact


class CheckPythonEnvironment(Artifact):
    def __init__ (self, required_version=(2,5), dependencies=[]):
        Artifact.__init__(self, ":checkpython", dependencies)
        self.required_version = required_version        
        
    def build(self):
        try:
            if sys.version_info >= self.required_version :
                return                   
        except: pass
        raise BaseException("Installed Python '%s' is too old, '%s' is required." % (sys.version_info, self.required_version))

    def what_it_does(self):
        return "Check Python version >= %s.%s" % (str(self.required_version[0]), str(self.required_version[1]))

      

class ValidatePythonCode(PermanentFileArtifact):
    def __init__ (self, path, dependencies = []):
        PermanentFileArtifact.__init__(self, path, dependencies)
        
    def build(self):
        path = self.fullpath()
        for r, dirs, files in os.walk(path):
            for file in files:
                if re.match(r".*\.py$", file):
                    self.check(os.path.join(r, file))     
               
    def check(self, file_path):
        py_compile.compile(file_path, doraise=True)
        
    def what_it_does(self):
        return "Validate Python code in '%s'" % self.name
        
        
class RunPythonCode(PermanentFileArtifact):
    def __init__ (self, name, dependencies = []):
        PermanentFileArtifact.__init__(self, name, dependencies)
  
    def build(self):
        ShellScriptHelper.run('python', self.fullpath())
    
    def what_it_does(self):
        return "Run Python script '%s'" % self.fullpath()


class SetupPythonPackage(PermanentFileArtifact):
    def __init__ (self, name, lib='lib', dependencies = []):
        assert lib
        PermanentFileArtifact.__init__(self, name, dependencies)
        self.lib = lib
         
    def is_expired(self): return True

    def build(self):
        path = self.fullpath()
        if os.path.isdir(path): 
            path = os.path.join(path, "setup.py")
            if not os.path.exists(path): raise BaseException("Setup file '%s' doesn't exist." % path)
        
        pkg_folder = os.path.dirname(path)
        lib_root   = os.path.join(Artifact.home_dir(), self.lib)
        if not os.path.exists(lib_root) or not os.path.isdir(lib_root): 
            raise BaseException("Lib folder '%s' doesn't exist." % path)
        
        os.chdir(pkg_folder)
        
        cmd = "python %s -q " % os.path.basename(path)
        ShellScriptHelper.run(cmd + " build  --build-lib %s" % lib_root)
        ShellScriptHelper.run(cmd + " install --install-lib %s  --install-headers %s" % (lib_root, lib_root))
        
        shutil.rmtree(os.path.join(pkg_folder, "build"))
        
    def what_it_does(self):
        return "Setup python package: '%s'" % self.name

