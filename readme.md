## What does Primus
*Primus* is deployment tool that makes your project installation much more easy and clear for support and understanding. 
From the user point of view Primus requires minimal efforts to write and add installation script into context of a user 
project. Just one small python script plus installation instruction written in human readable format as step by step 
deployment procedure.  

Primus follows the following paradigm:
   * Has a way to describe a project deployment procedure less talkative way
   * Keep deployment script in human readable format
   * Make hands free from absolute paths. Make everything in a context of project home
   * Centralize configuration properties (for many configs) in one place

## Installation 
Primus itself doesn't require any installation activities. This is self deployed package that cares about itself.

## How it works
To put Primus in a context of your project dot the following:

   * Copy ".primus" folder into your project folder
   * Open ".primus/project.py" file and write down your deployment process scenario

## Writing a deployment process scenario
Imagine a user has the following dummy project:
   * User has a nice project “BigBang”
   * This project is written in python (code in “lib” folder) and java (code in “src” folder)
   * Project can work only with Python v2.5+
   * Project requires “time.jar” third party library (available in a http repo)
   * JUnit test has to be run

    	PROJECT=Project(“BigBang”,
    	[
        	CheckPythonEnvironment(version=(2,5)),
    		CompileJavaCode(“src”, “lib”),
    		ValidatePythonCode(“lib”),
    		DownloadFile(“lib/”, "http://somwhere/timer.jar"),
			RunJUnit("test/TestBigbang.class", classpath = ['test', 'lib', 'lib/junit/junit-4.8.2.jar'])
  		])


## Run a project deployment 
Run the following script located in context of your project:   
   $ python .primus/deploy.py

## More information:
   * Documentation: http://www.gravitysoft.org/doku.php?id=home:projects:primus
   * Primus presentation
      * In PDF: http://www.lw-zone.org/download/Primus.pdf
      * As keynote file: http://www.lw-zone.org/download/Primus.pdf

## Licensing
LGPL