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

import os, glob, re

from artifactcore import Artifact
from fileartifact import ShellScriptHelper, PermanentFileArtifact


class JavaArtifact(PermanentFileArtifact):
    def __init__ (self, name, classpath = [],  dependencies=[]):
        PermanentFileArtifact.__init__(self, name, dependencies)
        self.classpath = classpath

    def class_path(self):
        classpath = []
        for path in self.classpath:
            path = os.path.join(Artifact.home_dir(), path)
            
            if not os.path.exists(path):
                raise BaseException("Invalid classpath item '%s'" % path)
            
            if os.path.isdir(path):
                for jar in self.collect_jars(path):
                    classpath.append(jar)
            else: 
                classpath.append(path)
        
        return ":".join(classpath)

    def collect_jars(self, path):
        jars = [ path ]
        for p in os.listdir(path):
            name = p
            p = os.path.join(path, p)
            if os.path.isfile(p) and len(name) > 4 and name.find('.jar') == len(name)- 4:
                jars.append(p)
        return jars

    def form_cmd(self, what):
        # form classpath
        class_path = self.class_path()

        # form command line and run it
        return what + " -cp " + class_path
    

class CompileJavaCode(JavaArtifact):
    def __init__ (self, name="lib", destination = 'lib', classpath = [],  dependencies=[]):
        assert  destination 

        m = re.compile(r"[\*\[\]]").search(name)
        if m:
            self.fmask = name[m.start():len(name)]
            name = name[0:m.start()]
        else:
            self.fmask = "*/*.java"
         
        JavaArtifact.__init__(self, name, classpath, dependencies)
        self.destination = PermanentFileArtifact(destination)
        self.classpath.append(destination)
        
    def build(self):
        destination = self.destination.fullpath()
        source      = self.fullpath()
        
        # collect java files if the source is directory
        if os.path.isdir(source):
            sources = " ".join(self.collect_sources(source))
            if len(sources) == 0: raise BaseException("No Java source files found in '%s'", source)
        else:
            sources = source 
        
        # form command line and run it
        cmd =  self.form_cmd('javac') + " -d " + destination + " " + sources
        ShellScriptHelper.run(cmd)

    def collect_sources(self, path):
        p = os.path.join(path, self.fmask)
        return glob.glob(p)

    def what_it_does(self):
        return "Compile Java code located in '%s' into '%s' directory." % (self.name, self.destination.name)


class RunJavaClass(JavaArtifact):
    def __init__ (self, name, destination = None, classpath = [],  dependencies=[]):
        JavaArtifact.__init__(self, name, classpath, dependencies)
        if destination == None: self.destination = name.split('/')[0]
        else: self.destination = destination
        classpath.append(self.destination)

    def build(self):
        cmd =  self.form_cmd('java') + " " + self.class_name()
        ShellScriptHelper.run(cmd)

    def class_name(self):
        fdir = os.path.dirname(self.name)
        (fname, fext) = os.path.splitext(os.path.basename(self.name))
        fdir = fdir[fdir.find(self.destination + "/") + len(self.destination) + 1:]
        return fdir.replace('/', '.') + "." + fname

    def what_it_does(self):
        return "Run Java code '%s'." % self.class_name()



class  RunJUnit(RunJavaClass):
    def __init__ (self, name, destination = None, classpath = [],  dependencies=[]):
        RunJavaClass.__init__(self, name, destination, classpath, dependencies)

    def form_cmd(self, what):
        class_path = self.class_path()
        return what + " -cp " + class_path  + "org.junit.runner.JUnitCore"

    def what_it_does(self):
        return "Run JUnit tests '%s'." % self.class_name()
        