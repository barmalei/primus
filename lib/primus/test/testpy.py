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

from primus.pyartifact import RunPythonCode, CheckPythonEnvironment, ValidatePythonCode

class Test(unittest.TestCase):
    def setUp(self):
        pass
          
    def test_py(self):
        v = (2, 5)
        def n():
            c = CheckPythonEnvironment(v) 
            c.build()

        n()    
        v = (3,5)
        self.assertRaises(BaseException, n)
        
        v = ValidatePythonCode("lib")
        v.build()
        
        r = RunPythonCode('lib/primus/pyartifact.py')
        r.build()

                       
if __name__ == '__main__':
    unittest.main()
