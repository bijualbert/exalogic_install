package com.oracle.pqa.exalogic.ecu;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class Ecu {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )
	    
		@Test
	    public void checkECUArchive() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkECUArchive"), true);
	    }
		@Test(dependsOnMethods = { "checkECUArchive" })
	    public void checkECUArchiveContents() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkECUArchiveContents"), true);
	    }
        @Test(dependsOnMethods = { "checkECUArchiveContents" })
	    public void checkEcuRunStatus() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkEcuRunStatus"), true);
	    }
        @Test(dependsOnMethods = { "checkECUArchive","checkECUArchiveContents","checkEcuRunStatus" })
	    public void deleteEculogs() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"deleteEculogs"), true);
	    }
}
