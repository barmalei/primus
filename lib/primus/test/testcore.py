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

from primus.artifactcore import Artifact, LoggableArtifact

class Test(unittest.TestCase):

    def setUp(self):
        pass
          
    def test_artifact_creation(self):
        def na(name, dependencies = []):
            a = Artifact(name, dependencies)
            a.name
        
        self.assertRaises(BaseException, na, None)
        self.assertRaises(BaseException, na, '')
        self.assertRaises(BaseException, na, ' ')
        self.assertRaises(BaseException, na, 'test', None)
       
    def test_artifact_dependencies(self):   
        a = Artifact("Test")
        d = Artifact("Dependency")
        a.depends_on(d)
        def na(): a.depends_on(d)
        self.assertRaises(BaseException, na)
        
    def test_loggable(self):
        log = LoggableArtifact()
        map = { 1:2, 3:4, 5:6 }
        log.write_log(map)
        map2 = log.read_log()
        self.assertEqual(map, map2)
        
        path = log.get_log_path()
        self.assertTrue(os.path.exists(path)) 
        
        log.cleanup_log()
        self.assertFalse(os.path.exists(path)) 

    
if __name__ == '__main__':
    unittest.main()
