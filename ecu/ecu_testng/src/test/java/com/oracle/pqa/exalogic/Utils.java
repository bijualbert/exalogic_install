package com.oracle.pqa.exalogic;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class Utils {
	
	public static int ExecuteOSCommand(List<String> command){
		
		int rc=1;
                StringBuilder cmdOut=null;
                StringBuilder cmdError=null;
		
		System.out.println("Executing command:"+command.toString()+"\n");
		
		ProcessBuilder pb=new ProcessBuilder(command);
		
		try {
			Process p=pb.start();
			
			
			InputStream cmdOutStream=p.getInputStream();
			BufferedReader br1=new BufferedReader(new InputStreamReader(cmdOutStream));
			cmdOut=new StringBuilder();
			String line=null;
			while( (line=br1.readLine()) != null ){
				cmdOut.append(line+"\n");
			}
			
                        InputStream cmdErrorStream=p.getErrorStream();
			BufferedReader br2=new BufferedReader(new InputStreamReader(cmdErrorStream));
			cmdError=new StringBuilder();
			line=null;
			while( (line=br2.readLine()) != null ){
				cmdError.append(line+"\n");
			}
			
			p.waitFor();
			rc=p.exitValue();
			
		} catch (IOException e) {			
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
                
                System.out.println("Command output (if any):"+cmdOut);
                System.out.println("Command error (if any):"+cmdError);
		System.out.println("Return code:"+rc);
		
		return rc;
	
	}	

}
