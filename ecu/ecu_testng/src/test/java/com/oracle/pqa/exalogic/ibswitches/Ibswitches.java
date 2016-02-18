package com.oracle.pqa.exalogic.ibswitches;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;
import java.lang.Integer;

public class Ibswitches {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir","buildNumber"} )
	    
		@Test
	    public void checkOOBPartitions() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkOOBPartitions",Integer.parseInt(System.getProperty("buildNumber"))), true);
	    }
	    
		@Test(dependsOnMethods = { "checkOOBPartitions" })
		public void checkPartitionName() {
			Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"), System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkPartitionName",Integer.parseInt(System.getProperty("buildNumber"))),true);
		}
		
		@Test(dependsOnMethods = { "checkPartitionName" })
		public void checkPartitionType() {
			Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"), System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkPartitionType",Integer.parseInt(System.getProperty("buildNumber"))),true);
		}
		
		@Test(dependsOnMethods = { "checkPartitionType" })
		public void checkPartitionMemberAccess() {
			Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"), System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkPartitionMemberAccess",Integer.parseInt(System.getProperty("buildNumber"))),true);
		}
}
