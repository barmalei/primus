#!/usr/bin/env python
#
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
    
import unittest, os

from primus.repartifact import DownloadFile
from primus.fileartifact import FileArtifact

class Test(unittest.TestCase):

    def setUp(self):
        pass
          
    def test_repo_artifact(self):
        def na(): 
            d = DownloadFile("tmp/repo", "  ")
            d.name
        self.assertRaises(BaseException, na)
        
        def na(): 
            d = DownloadFile("tmp/repo", None)
            d.name
        self.assertRaises(BaseException, na)

        r = DownloadFile("tmp/repo", "bad url")
        def na(): r.build()
        self.assertRaises(BaseException, na)        
   
        def na(): 
            d = DownloadFile("lib", "bad url")
            d.name
        self.assertRaises(BaseException, na)        
   
        
        fa = FileArtifact("tmp/repo.html").fullpath()
        if os.path.exists(fa): os.remove(fa)
        r = DownloadFile("tmp/repo.html", "http://www.google.com/index.html")
        r.build()
     
        self.assertTrue(os.path.exists(r.fullpath()))
        self.assertFalse(os.path.isdir(r.fullpath()))
        self.assertTrue(len(open(r.fullpath()).read()) > 0)
                       
    def test_zrepo_artifact(self):   
        pass 

if __name__ == '__main__':
    unittest.main()
