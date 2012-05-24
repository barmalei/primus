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
    
import os, unittest, ConfigParser

from primus.mysqlartifact import CheckDBEnvironment



class TestMySQL(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), 'dbtest.conf')
        self.config.read([ self.config_path ])
          
    def test_check_mysqlversion(self): pass
        # ch = CheckDBEnvironment(config = (self.config_path, 'db'), required_version=(8, 0))
        # def na(): ch.build()
        # self.assertRaises(CheckDBEnvironment.VersionException, na)
        #  
        # ch = CheckDBEnvironment(config = (self.config_path, ['db2', 'db']), required_version=(8, 0))
        # def na(): ch.build()
        # self.assertRaises(CheckDBEnvironment.VersionException, na)
        # 
        # ch = CheckDBEnvironment(config = (self.config_path, 'db'), required_version=(4, 0))
        # ch.build()

if __name__ == '__main__':
    unittest.main()
