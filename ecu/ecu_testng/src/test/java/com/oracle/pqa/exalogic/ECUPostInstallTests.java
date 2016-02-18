package com.oracle.pqa.exalogic;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ECUPostInstallTests {
	
	public static boolean executePythonTest (String srcDir,String testPropertyFile, String ecuConfigDir,String method){
		
		int rc=1;
		List<String> cmd=new ArrayList<String>();
                  
		cmd=Arrays.asList("python", srcDir+"/oeca/install/pqa/tests/exalogic/ecu/ecu_test_driver.py","--config_file_dir",ecuConfigDir,"--test_properties",testPropertyFile,"--postinstall_validation",method);					
		rc=Utils.ExecuteOSCommand(cmd);
		
		if(rc==1){
			return false;
		}else{
			return true;
		}
		
		
	}
        
        public static boolean executePythonTest (String srcDir,String testPropertyFile, String ecuConfigDir,String method, int buildNumber){
		
		int rc=1;
		List<String> cmd=new ArrayList<String>();
                 
		cmd=Arrays.asList("python", srcDir+"/oeca/install/pqa/tests/exalogic/ecu/ecu_test_driver.py","--config_file_dir",ecuConfigDir,"--test_properties",testPropertyFile,"--postinstall_validation",method,"--build_number",String.valueOf(buildNumber));					
		rc=Utils.ExecuteOSCommand(cmd);
		
		if(rc==1){
			return false;
		}else{
			return true;
		}
		
		
	}
	

}
