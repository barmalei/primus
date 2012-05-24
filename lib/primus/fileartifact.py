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

import os, shutil, tempfile
from subprocess import Popen

from artifactcore import Artifact, ShellScriptHelper

class FileArtifact(Artifact):
    def __init__ (self, name, dependencies=[]):
        Artifact.__init__(self, name, dependencies)
        if os.path.isabs(self.name):
            raise BaseException("File artifact '%s' cannot have absolute path" % name)         
                            
    def fullpath(self): return os.path.join(Artifact.home_dir(), self.name)


class AcquiredFile(FileArtifact):
    def __init__(self, name, dependencies = []):
        FileArtifact.__init__(self, name, dependencies)
        p = self.fullpath()
        if os.path.isdir(p): raise BaseException("File cannot be directory")
        if not os.path.isdir(os.path.dirname(p)): raise BaseException("Wrong parent directory for '%s'" % p)

    def cleanup(self): 
        p = self.fullpath()
        if os.path.exists(p):
            if os.path.isfile(p): os.remove(p)
            else: raise BaseException("File '%s' is directory")

    def build(self): pass
    
    def is_expired(self): 
        return not os.path.exists(self.fullpath())
    
    
class PermanentFileArtifact(FileArtifact):
    def __init__ (self, name, dependencies=[]):
        FileArtifact.__init__(self, name, dependencies)
        if not os.path.exists(self.fullpath()): raise IOError("File artifact '%s' does not exist" %  name)


class CreateSymLink(FileArtifact):
    def __init__ (self, name, path, dependencies = []):
        FileArtifact.__init__(self, name, dependencies)            
        self.path = path      
      
    def build(self):
        realpath = os.path.join(Artifact.home_dir(), self.path)

        if not os.path.exists(realpath):
            raise IOError("Path '%s' link has to refer does not exist." % self.path)

        os.chdir(Artifact.home_dir())
        if os.path.exists(self.name):
            os.unlink(self.name)
            
        os.symlink(realpath, self.name)    

    def what_it_does(self):
        return "Create symlink: %s" % self.name


 
class AcquiredDirectory(FileArtifact):
    def __init__ (self, name, dependencies=[]):
        FileArtifact.__init__(self, name, dependencies)
        path = self.fullpath()
        if os.path.exists(path) and (not os.path.isdir(path)): 
            raise BaseException("File '%s' exists and the file is not a directory")

    def cleanup(self):
        path = self.fullpath()
        if os.path.exists(path):
            if os.path.isdir(path) : 
                os.chdir(Artifact.home_dir())
                shutil.rmtree(self.name)
            else: 
                raise IOError()
    
    def build(self):
        path = self.fullpath()
        if not os.path.exists(path): os.makedirs(path)
 
    def is_expired(self): 
        return not os.path.exists(self.fullpath())
   
    def what_it_does(self):
        return "Create directory '%s'" % self.fullpath()

 
class RunShellScript(PermanentFileArtifact):
    def __init__(self, name, parameters = '', dependencies = []):
        PermanentFileArtifact.__init__(self, name, dependencies)        
        self.parameters = parameters
    
    def build(self):
        ShellScriptHelper.run(self.fullpath(), self.parameters, True)
    
    def what_it_does(self):
        return "Run shell script '%s %s'" % (self.name, self.parameters)  


class RunMakefile(RunShellScript):
    def __init__ (self, name, parameters = '', dependencies = []):
        if os.path.basename(name) != 'Makefile': 
            name = os.path.join(name, 'Makefile')
        RunShellScript.__init__(self, name, parameters, dependencies)

    def build(self):
        os.chdir(os.path.dirname(self.fullpath()))
        ShellScriptHelper.run("make", self.parameters, False)

    def what_it_does(self):
        return "Run make file '%s %s'" % (self.name, self.parameters)
        

class UnzipFile(PermanentFileArtifact):
    def __init__ (self, name, destination = None, dependencies = []):
        PermanentFileArtifact.__init__(self, name, dependencies)
        if destination == None: destination = os.path.dirname(name)
        self.destination = AcquiredDirectory(destination)
        
    def build(self):
        self.destination.build()
        zippath     = self.fullpath()
        destination = self.destination.fullpath()

        tmp  = tempfile.mkstemp(dir=Artifact.home_dir())
        null = open(tmp[1], "w")
        try: 
            ShellScriptHelper.run('unzip', " %s -d %s " % (zippath, destination), False, null)   
        finally: 
            null.close()
            os.remove(tmp[1])
        
    def what_it_does(self):
        return "Unzip '%s' to '%s'" % (self.name, self.destination.name)
    

class CopyFile(AcquiredFile):    
    def __init__ (self, name, source, dependencies = []):
        assert source
        self.source = PermanentFileArtifact(source)
        AcquiredFile.__init__(self, name, dependencies)

    def is_expired(self): return True

    def build(self):
        if os.path.isdir(self.source.fullpath()): raise IOError("Copying directory ('%s') is not supported." % self.source.name)
        shutil.copyfile(self.source.fullpath(), self.fullpath())
     
    def what_it_does(self):
        return "Copy '%s' to '%s'" % (self.source.name, self.name)


class RmFile(FileArtifact):    
    def __init__ (self, name, dependencies = []):
        FileArtifact.__init__(self, name, dependencies)

    def is_expired(self): return True

    def build(self):
        path = self.fullpath()
        if path.os.exists():
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.path.remove(path) 
     
    def what_it_does(self):
        return "Remove '%s'" % self.name
