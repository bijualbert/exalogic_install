package com.oracle.pqa.exalogic.nimbula;

import org.testng.Assert;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.oracle.pqa.exalogic.*;

public class Nimbula {
	              
        @Parameters( {"srcDir", "testProperties", "ecuConfigDir"} )
	    
		@Test
	    public void checkDefaultVethernet() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDefaultVethernet"), true);
	    }
		
		@Test
	    public void checkDefaultVnet() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDefaultVnet"), true);
	    }
		
		@Test
	    public void checkDefaultVnetReservation() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDefaultVnetReservation"), true);
	    }
		
		@Test
	    public void checkDefaultOrchestrationName() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDefaultOrchestrationName"), true);
	    }
		
		@Test
	    public void checkDefaultTenant() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkDefaultTenant"), true);
	    }
		
		@Test
	    public void checkNimbulaVersion() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkNimbulaVersion"), true);
	    }
	    
	    @Test
	    public void checkNimbulaNodes() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkNimbulaNodes"), true);
	    }
		
	    @Test
	    public void checkNimbulaShape() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkNimbulaShape"), true);
	    }
		
		@Test
	    public void checkControlVMPlacement() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkControlVMPlacement"), true);
	    }
		
		@Test
	    public void checkVMRelationship() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkVMRelationship"), true);
	    }
		
		@Test
	    public void checkControlVMNodePlacement() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkControlVMNodePlacement"), true);
	    }
		
	    @Test
	    public void checkNimbulaAPI() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"checkNimbulaAPI"), true);
	    }
	    @Test
	    public void getTenantAPI() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"getTenantAPI"), true);
	    }
	    @Test
	    public void getVethernetAPI() {
	  		Assert.assertEquals(ECUPostInstallTests.executePythonTest(System.getProperty("srcDir"),System.getProperty("testProperties"),System.getProperty("ecuConfigDir"),"getVethernetAPI"), true);
	    }
}
