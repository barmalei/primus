package primus; 

import org.junit.Test;
import org.junit.Before;
import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;


public class JavaUnitTest
{
    @Test
    public void test1() 
    throws Exception
    {
        assertTrue(true);
    }

    public static void main(String[] args)
    throws Exception
    {
		Result result = JUnitCore.runClasses(JavaUnitTest.class);
        for (Failure failure : result.getFailures()) {
            System.out.println("!!!" +  failure.toString());
        }
	}
}


