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

import urllib2, os, urlparse, tempfile, zipfile

from artifactcore import Artifact
from fileartifact import AcquiredFile, AcquiredDirectory, UnzipFile

class RemoteFile(AcquiredFile):
    def __init__(self, name, url, dependencies = []):
        AcquiredFile.__init__(self, name, dependencies)

        if url and url.strip():
            url = url.strip()
            self.url_info = urlparse.urlparse(url)    
            self.url = url
            if self.url_info.scheme == None or len(self.url_info.scheme) == 0:
                raise BaseException("Wrong URL '%s'" % url)
        else:
            raise BaseException("Wrong URL '%s'" % url)
        
    def build(self): self.download(self.fullpath())
        
    def download(self, destination_path):
        if destination_path == None or len(destination_path.strip()) == 0:
            raise IOError("Invalid destination path : " + destination_path)

        if os.path.exists(destination_path) and os.path.isdir(destination_path):
            raise IOError("Destination file '%s' is existent directory" % destination_path)

        repo = urllib2.urlopen(self.url)
        try:
            data = repo.read()
            repo.close()
            file = open(destination_path, 'w') 
            try: file.write(data)             
            finally: file.close() 
        finally:
            repo.close()

 
class DownloadFile(RemoteFile):
    def __init__(self, name, url, dependencies=[]):
        p = os.path.join(Artifact.home_dir(), name)
        if os.path.isdir(p): name = os.path.join(name, url.split('/')[-1])
        RemoteFile.__init__(self, name, url, dependencies)

    def what_it_does(self):
        return "Download file '%s'" % self.fullpath()
 
    
class DownloadArchivedFiles(AcquiredDirectory):
    def __init__ (self, name, url, dependencies=[], do_if_absent = None):
        AcquiredDirectory.__init__(self, name, dependencies)
        self.url, self.use_shell_unzip, self.do_if_absent = url, True, do_if_absent
        
    # !!! python zip module does not keeps files rights
    def py_unzip (self, zippath):
        path = self.fullpath()
        
        zip = None
        try:
            zip      = zipfile.ZipFile(zippath, 'r')
            zipnames = zip.namelist()
         
            if len(zipnames) == 0: 
                raise BaseException("Empty ZIP.")
         
            for zipitem in zipnames:
                item_path = os.path.join(path, zipitem)            
                if item_path[-1] == '/':
                    if not os.path.exists(item_path): os.makedirs(item_path)
                else:
                    f = open(item_path, 'w')  
                    try: f.write(zip.read(zipitem))
                    finally: f.close() 
        finally:
            if zip != None: zip.close()

    def shell_unzip(self, zippath):
        unzip = UnzipFile(zippath, self.name)
        unzip.build()
    
    def build(self):            
        super(DownloadArchivedFiles, self).build()
        
        tmp = tempfile.mkstemp(dir = Artifact.home_dir())
        try:
            RemoteFile(os.path.basename(tmp[1]), self.url).build()
            if self.use_shell_unzip : self.shell_unzip(os.path.basename(tmp[1]))
            else:                     self.py_unzip(tmp[1]) 
        finally:
            os.remove(tmp[1]) 
        
        if self.do_if_absent != None:
            p = os.path.join(self.fullpath(), self.do_if_absent)
            if not os.path.exists(p): raise BaseException("File '%s' cannot be found after unzip" % p)
            
    def what_it_does(self):
        return "Download and unzip '%s' file" % self.name

    def is_expired(self):
        if self.do_if_absent != None:
            p = os.path.join(self.fullpath(), self.do_if_absent)
            if not os.path.exists(p): return True
        return super(DownloadArchivedFiles, self).is_expired() 
    
