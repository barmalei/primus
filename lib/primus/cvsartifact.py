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

from artifactcore import Artifact
from fileartifact import ShellScriptHelper, AcquiredFileArtifact


class ExportSVNRepo(AcquiredFileArtifact):
    def __init__ (self, name, repo, dependencies=[]):
        if not repo:  
            raise BaseException, "Repository url has not been specified"
        AcquiredFileArtifact.__init__(self, name, dependencies)
        self.repo = repo

    def build(self):
        ShellScriptHelper.run('svn -q export %s  %s' % (self.repo, self.fullpath()))

    def what_it_does(self):
        return "Export SVN repository '%s' to '%s'" % (self.repo, self.fullpath())


class ExportGITRepo(AcquiredFileArtifact):
    def __init__ (self, name, repo,  dependencies=[]):
        AcquiredFileArtifact.__init__(self, name, dependencies)
        self.repo = repo

    def build(self):
        ShellScriptHelper.run('git archive --format=tar --remote=%s --prefix=%s master | tar -xf -' % (self.repo, self.fullpath()))

    def what_it_does(self):
        return "Export GIT repository '%s' to '%s'" % (self.repo, self.fullpath())

