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
import copy
import pickle
import StringIO
from subprocess import Popen

ARTIFACTS = {}

def BUILD(artifact, shift = ''):
    if artifact == None: raise BaseException("Artifact cannot be None")
        
    def __IS_EXPIRED__(a):
        if a.is_expired(): return True
        for b in a.dependencies(): 
            if __IS_EXPIRED__(b) : return True     
        return False  
        
    try:   
        # !!!
        # ??? source code 
        # !!!
        try:
            condition = getattr(artifact, "condition")
            cond_art  = condition()
            res       = BUILD(cond_art, shift)
            if res != True: 
                print "%s%s" % (shift, artifact.fail_message())
                return False
        except AttributeError: pass 
    
        #  Print message
        lines = artifact.what_it_does()
        if lines != None:
            for line in lines.split('\n'): print "%s%s" % (shift, line)        
        
        b = __IS_EXPIRED__(artifact)
        if b: 
            for a in artifact.dependencies(): BUILD(a, shift + 4*' ')
            return artifact.build()
        else:
            print "%s'%s' had been built before." % (shift, artifact.name)
            return False
    except:
        artifact.cleanup()
        raise
        
def CLEANUP(artifact):
    if artifact == None: raise BaseException("Artifact cannot be none.")
    artifact.cleanup()

def ARTIFACT(name):
    if name == None or len(name.strip()) == 0: raise BaseException("Artifact name cannot be empty.")
    return ARTIFACTS[name]


class Mock(object):
    CLASSES = 0

    def _init_arguments(self, *args, **kargs):
        self.args  = args
        self.kargs = kargs

    @staticmethod
    def class_for(cls):
        new_cls = type('Abcdef' + str(Mock.CLASSES), (cls, Mock), {})
        new_cls._orig_init = new_cls.__init__
        new_cls.__init__   = Mock._init_arguments     
        Mock.CLASSES += 1
        return new_cls
     
    def __getattribute__(self, name): 
        parent = super(Mock, self)
        try:
            args    = parent.__getattribute__('args')
        except  AttributeError:
            pass
        else:    
            kargs   = parent.__getattribute__('kargs')
            init    = parent.__getattribute__('_orig_init')
            
            deleter = parent.__getattribute__('__delattr__')
            deleter('args')
            deleter('kargs')
            init(*args, **kargs)

        return super(Mock, self).__getattribute__(name)


class Artifact(object):
    """ Basic logical unit of deployment."""
    
    def __init__ (self, name, dependencies=[]):
        """ Class initialiser """
        if name == None or len(name.strip()) == 0:
            raise BaseException("Invalid artifact name '%s'" % (name))             
        self.__name = name.strip()
        if dependencies == None : raise BaseException("Dependencies cannot be none.")
        self.__dependencies = dependencies
        ARTIFACTS[name] = self

    def __new__(cls, *args, **kargs):
        ncls = Mock.class_for(cls)
        return object.__new__(ncls)

    def depends_on(self, artifact):
        for a in self.__dependencies:
            if artifact.name == a.name: raise BaseException("Duplicated artifact : " + artifact) 
        self.__dependencies.append(artifact)
    
    @property
    def name(self): return self.__name
    
    def dependencies(self): return copy.copy(self.__dependencies)
           
    def is_expired(self): return True
    
    def cleanup(self): pass    
        
    def msg(self, msg):
        """ Print message related to the given artifact """
        print  "%20s : %s" % (self.name, msg)
           
    def build(self): raise NotImplementedError()
    
    def what_it_does(self): return self.name
        
    @staticmethod
    def home_dir():
        rp = os.path.dirname(os.path.abspath(__file__))        
        pp = None       
        while pp != rp and rp != None and rp != '' and (not os.path.exists(os.path.join(rp, '.primus'))): 
            pp = rp
            rp = os.path.dirname(rp)
                    
        if rp == None or rp == '' or rp == pp:
            raise BaseException("Project home cannot be identify.")             

        return rp
                    

class DoGroup(Artifact): 
    def build(self): pass

     
class Project(Artifact):
    def __init__(self, name, dependencies = [], version = (1,0,0)):
        Artifact.__init__(self, name, dependencies)
        self.version = version
    
    def deploy(self): BUILD(self)
            
    def build(self): pass
                  
    def cleanup(self): pass
                  
    def what_it_does(self):
        return "Deploy project '%s' v%s.%s.%s" % (self.name, str(self.version[0]), str(self.version[1]), str(self.version[2]))                
                    
    
class DoIf(Artifact):   
    def __init__ (self, condition, fail_message = 'failed',  dependencies = []):
        assert condition and fail_message
        Artifact.__init__(self, condition.name, dependencies)
        self._fail_message = fail_message
        self._condition = condition
        
    def condition(self): return self._condition
    
    def fail_message(self): return self._fail_message
    
    def build(self): return True

    def what_it_does(self): return None
    

class DoIfNot(DoIf):
    class Hook(Artifact):
        def __init__(self, target):
            assert target
            Artifact.__init__(self, target.name, target.dependencies())
            self.target = target

        def build(self): return not self.target.build()
        
        def what_it_does(self): 
            return self.target.what_it_does()

    def __init__(self, condition, fail_message = 'failed', dependencies = []):
        DoIf.__init__(self, DoIfNot.Hook(condition), fail_message, dependencies)


class ReportError(Artifact):
    def __init__(self, message):
        Artifact.__init__(self, "Raise exception")
        assert message
        self.message = message 
    
    def what_it_does (self):
        return "Report error: %s" % self.message
        
    def build(self): raise BaseException(self.message)    


class LoggableArtifact(object):
    def __init__ (self):
        self.__log_path = self.__build_log_path__()       
        dir = os.path.dirname(self.__log_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    def get_log_path(self):
        return self.__log_path

    def cleanup_log(self):
        path = self.log_path
        if os.path.exists(path) : os.remove(path)
        
    def write_log(self, map):
        if map == None or (not isinstance(map, dict)): 
            raise BaseException("Only dictonary can be used as a log content.")  
        f = open(self.log_path, 'wb') 
        try: pickle.dump(map, f)
        finally: f.close()
        
    def read_log(self):
        if os.path.exists(self.log_path) :
            f = open(self.log_path, 'rb') 
            try: return pickle.load(f)
            finally: f.close()       
        return {}

    def __build_log_path__(self):
        return os.path.join(Artifact.home_dir(), "log", self.__class__.__name__ + ".log") 

    log_path = property(get_log_path)


class ShellScriptHelper(object):        
    @staticmethod
    def run(script, parameters='', change_dir = False, logger=None):
        if script == None or len(script.strip()) == 0:
            raise BaseException("Script name is empty.")
                  
        if change_dir and os.path.dirname(script) == '':
            raise IOError("Directory name cannot be fetched from '%s' script." % (script))
                                
        if change_dir: 
            dir    = os.path.dirname(script) 
            script = "./" + os.path.basename(script)
            os.chdir(dir)

        p = Popen("%s %s" % (script, parameters), stdout = logger, stderr = logger, shell=True)
        error = os.waitpid(p.pid, 0)           
        if error[1] > 0:
            raise BaseException("Script '%s' failed." % script)
    
