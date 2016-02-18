package com.oracle.pqa.exalogic.zfs;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class Zfs {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )

		@Test
	    public void checkPools() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkPools"), true);
	    }
		/*
		Commented by Ramesh
		@Test
	    public void checkNTPServer() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkNTPServer"), true);
	    }
		**/		
		@Test
	    public void checkProjects() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkProjects"), true);
	    }
		
		@Test
	    public void checkDNSServers() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDNSServers"), true);
	    }
		/*
		Commented by Ramesh
		@Test
	    public void checkNetInterfaces() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkNetInterfaces"), true);
	    }
		**/
}
