package com.oracle.pqa.exalogic.ovs;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class Ovs {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )

		@Test
	    public void checkOVSOSType() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOVSOSType"), true);
	    }
		
		@Test
	    public void checkOVSCPU() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOVSCPU"), true);
	    }
		
		@Test
	    public void checkOVSMemory() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOVSMemory"), true);
	    }
		/*
		Commented by Ramesh
		
		@Test
	    public void checkOVSDNSServer() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOVSDNSServer"), true);
	    }
		@Test
	    public void checkOVSNTPServer() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOVSNTPServer"), true);
	    }
		**/
		@Test
	    public void checkOVSImageStatus() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOVSImageStatus"), true);
	    }


}
