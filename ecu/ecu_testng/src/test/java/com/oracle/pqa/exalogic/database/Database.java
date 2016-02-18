package com.oracle.pqa.exalogic.database;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class Database {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )
	    
		@Test
	    public void checkDatabaseRunning() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDatabaseRunning"), true);
	    }
	    
		@Test
		public void checkDatabaseListener() {
			Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"), System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDatabaseListener"),true);
		}
		
		@Test
		public void checkDatabaseConnection() {
			Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"), System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDatabaseConnection"),true);
		}
}
