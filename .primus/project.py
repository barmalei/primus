from primus.artifactcore  import DoGroup, Project
from primus.pyartifact    import CheckPythonEnvironment, ValidatePythonCode, RunPythonCode
from primus.repartifact   import DownloadArchivedFiles, DownloadFile
from primus.javaartifact  import CompileJavaCode

#  Project deployment configuration file
REPO_URL    = 'http://repo.gravitysoft.org'
DEPLOY_CONF = '.primus/deploy.conf' 

#  Deployment configuration
PROJECT = Project("Primus", 
      [ 
        DoGroup("Test environnment", 
        [
          CheckPythonEnvironment(required_version=(2,5)),
          ValidatePythonCode('lib'),
        ]),

        DownloadFile('lib', "%s/junit/junit-4.8.2.jar" % REPO_URL),
        CompileJavaCode('lib/**/*.java'),
        RunPythonCode('lib/primus/test.py')
      ]) 

