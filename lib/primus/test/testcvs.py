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

from primus.cvsartifact import ExportSVNRepo

class Test(unittest.TestCase):

    def setUp(self):
        pass
          
    def test_svn_import(self):
        def na(): 
            d = ExportSVNRepo("tmp/cvs", None)
            d.what_it_does()
        self.assertRaises(BaseException, na)

        def na(): 
            d = ExportSVNRepo("tmp/cvs", '')
            d.what_it_does()
        self.assertRaises(BaseException, na)

        d = ExportSVNRepo("tmp/cvs", "svn+ssh://avishneu@ilps.science.uva.nl/scratch/svn/primus/trunk/lib/primus/test")
        try:
            d.build()
            self.assertTrue(os.path.exists(d.fullpath()))
        finally:
            d.cleanup()
            self.assertTrue(not os.path.exists(d.fullpath()))
                       

if __name__ == '__main__':
    unittest.main()
