package com.oracle.pqa.exalogic.physicalserver;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class PhysicalServer {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )

		@Test
	    public void checkFirmVersion() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkFirmVersion"), true);
	    }		
}
