import sys, os, unittest



topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir))
sys.path.insert(0, topdir)


from test import *

if __name__ == '__main__':
    
    required_mod_dir = os.path.dirname(os.path.abspath(__file__))
    required_mod_dir = os.path.join(required_mod_dir, 'test')
    
    tested_modules = 0
    
    for key in dir():
        try:
            key = "test.%s" % key
            if not key in sys.modules: continue
            
            module = sys.modules[key]
            if module.__package__ == 'test':
                mpath = os.path.dirname(os.path.abspath(module.__file__))
                if mpath != required_mod_dir: continue
               
                tested_modules = tested_modules + 1  
                test   = unittest.TestLoader()
                result = unittest.TestResult()
                testcases = test.loadTestsFromModule(module)
                testcases.run(result)
                if result.wasSuccessful():
                    print "SUCCESS: Module '%s'(%s) testing has passed successfully."  % (key, result.testsRun)               
                else:
                    print "ERROR  : Module '%s' testing has failed." % (key)

                    for error in result.errors:
                        print "  Method '%s' error:" % (error[0]._testMethodName)
                        print "  " + error[1] + "\n"
               
                    for error in result.failures:
                        print "  Method '%s' failed:" % (error[0]._testMethodName)
                        print "  " + error[1] + "\n"
                    
                    print "BAD LUCK"
                    exit(1) 
        except AttributeError: pass
    
    if tested_modules > 0: print "CONGRATULATION! All tests have passed."
    else                 : print "No test cases have been found."  
    exit(0)
