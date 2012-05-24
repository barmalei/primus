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
    
import unittest

from primus.javaartifact import CompileJavaCode, RunJavaClass, RunJUnit

class Test(unittest.TestCase):
    def setUp(self):
        pass
          
    def test_compilation(self):
        c = CompileJavaCode()
        c.build()
        
    def test_run(self):   
        c = RunJavaClass("lib/primus/JavaTest.class")
        c.build()

    def test_junit(self):   
        c = RunJUnit("lib/primus/JavaUnitTest.class", classpath = ['lib' ] )
        c.build()


if __name__ == '__main__':
    unittest.main()
