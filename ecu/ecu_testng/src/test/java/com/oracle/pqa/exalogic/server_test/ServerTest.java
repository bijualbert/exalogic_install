package com.oracle.pqa.exalogic.servertest;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class ServerTest {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )

		@Test
	    public void checkInterfaceName() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkInterfaceName"), true);
			}		
}
