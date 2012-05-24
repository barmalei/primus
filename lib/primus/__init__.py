

__all__ = ['artifactcore', 'fileartifact', 'pyartifact', 'repartifact', 'mysqlartifact', 'confartifact', 'javaartifact']
from artifactcore import Artifact
print "\n:: Primus - deployment tool"
print ":: v1.4.1, Apr 2012"
print ":: target project home: '%s'\n" % (Artifact.home_dir()) 
