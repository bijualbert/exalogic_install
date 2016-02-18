#! /usr/bin/python

### Default python modules
import sys;
import re;

#Exalogic internal modules
from pylib.exalogic.config.exalogic_configuration import *;
from pylib.exalogic.nimbula.nimbula import *;
from tests.exalogic.ecu.data.zfs_test_properties import *;
from tests.exalogic.ecu.ecutest_exceptions import *;
from pylib.storage import *;


__author__ = "Arvind"
__date__ = "$Apr 17, 2015 10:57:16 AM$"

class ZFSTests(object):
	"""
	Test Related to ZFS storage validation.
	"""
	
	def __init__ (self,configurationDirectory,logger=None):
	
		"""
		Constructor for ZFS tests, initializes the ZFS object
		"""

		self.logger=logger;

		# Get ZFS host name,ip,username and password
		self.rack_config=ExalogicConfiguration(configurationDirectory);
		self.storage=self.rack_config.GetStorageInfo();
		passwords=self.rack_config.GetPasswords();
		self.storageAccountInfo=passwords["storage"];
		self.storageUser=self.storageAccountInfo.keys()[0];
		self.storagePassword=passwords["storage"][self.storageUser];
		
		#instantiate a ZFSController 
		self.zfsServer1=zfs.ZFSController(name=self.storage['nodes'][0]["host"],ip=self.storage['nodes'][0]["eth-admin"]["ip"],user=self.storageUser,password=self.storagePassword,prompt=".*?:>",logger=logger);        
		#Check if the first controller is active or not
		if not self.zfsServer1.isactive():
			# if controller not active, the other one is active
			self.zfsServer1=zfs.ZFSController(name=self.storage['nodes'][1]["host"],ip=self.storage['nodes'][1]["eth-admin"]["ip"],user=self.storageUser,password=self.storagePassword,prompt=".*?:>",logger=logger);        
		
	def checkPools(self):
		"""
		Check if pools name is as expected
		"""

		# Print ZFS storage node name,ip,user & passwords

		self.logger.debug("Storage node 0 name:"+self.storage['nodes'][0]["host"]);
		self.logger.debug("Storage node 0 IP:"+self.storage['nodes'][0]["eth-admin"]["ip"]);
		self.logger.debug("Storage user:"+self.storageUser);
		self.logger.debug("Storage password:"+self.storagePassword);

		# Print expected pool name
		expectedPoolNames=self.rack_config.GetPoolsInfo();		
		self.logger.info("Expected Pools Name:"+expectedPoolNames);        

		
		# Call your getPoolNames method which is actual values		
		poolNames=self.zfsServer1.getPoolNames();	
		self.logger.debug("Pools:");
		self.logger.debug(poolNames);
		
		# Compare and print pass / fail
		self.logger.info("Actual pools name from ZFS storage is:"+(poolNames[0]));

		if(poolNames[0]!=expectedPoolNames):                    
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Pool name  is not as expected");
		else:
			self.logger.info("Step result:Pass");

	def checkShareName(self):
		"""
		Check if share names are as expected
		"""
		try:
			# for testing purpose only
			#print self.zfsServer1.getGuid()
		
		
			#make expected share names
			rackName=self.rack_config.getRackName();
			expected_share_names = ["EPC_ARTIFACTS","EPC_"+rackName]
			
			#Get actual share names
			actual_share_names = self.zfsServer1.getShareNames()

			#Check expected share names
			error = False
			for name in expected_share_names:
				self.logger.info("Checking share " + name)
				if not name in actual_share_names:
					error = True
					self.logger.error("Share " + name + " does not exist")
			if error:
				raise ECUTestFailureError("ZFS share names are not as expected");
		except:
			raise ECUTestFailureError("ZFS share name test failed to execute");

	def checkNTPServer(self):        
		"""
		Check if NTP Server IP is as expected
		"""

		# Print ZFS storage node name,ip,user & passwords
		self.logger.debug("Storage node 0 name:"+self.storage['nodes'][0]["host"]);
		self.logger.debug("Storage node 0 IP:"+self.storage['nodes'][0]["eth-admin"]["ip"]);
		self.logger.debug("Storage user:"+self.storageUser);
		self.logger.debug("Storage password:"+self.storagePassword);
		
		#Expected NTP Server
		expectedNTPServer=self.rack_config.GetNTPServerIP();
		
		# Call your getNTPServerIP method which get actual value from ZFS
		NTPServer=self.zfsServer1.getNTPServerIP();
        
		self.logger.debug("Expected NTP Server IP:");
		self.logger.debug(expectedNTPServer[0]);
		self.logger.info("Actual NTP Server IP is:"+(NTPServer));
		
		# Compare and print pass / fail

		if(NTPServer!=expectedNTPServer[0]):                    
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("NTP Server is not as expected");
		else:
			self.logger.info("Step result:Pass");
			
	
	def checkProjects(self):
		"""
		Check if project names configured in ZFS is as expected
		"""
		### Get the storage project name (Expected value)
		storageConfigInfo=self.rack_config.GetStorageConfigInfo();
		for key in storageConfigInfo["projects"]:			
			projectName=key;			
		self.logger.info("Expected project name is:"+projectName);
			
		#### Getting the actual list of projects from ZFS (Actual values)
		project_List=self.zfsServer1.getProjects();	

		self.logger.debug("Actual projects from ZFS storage is:");
		self.logger.debug(project_List);

		if(projectName not in project_List):                    
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Project is not available in ZFS as expected");
		else:
			self.logger.info("Step result:Pass");
	
	def checkDNSServers(self):
		"""
		Check if DNS Servers are as expected
	    """		
		### Get expected DNS servers from json files using rack configuration instance
		### Get the value from common-host-config.json file with the property "dns_servers"		
		expectedDNSServers=self.rack_config.GetDNSServers();		
		self.logger.debug("Expected DNS servers");        
		self.logger.debug(expectedDNSServers);
				
		# Call your getPoolNames method which is actual values		
		actualDNSServers=self.zfsServer1.getConfiguredDNSServers();	
		self.logger.debug("Actual DNSServer details:");
		self.logger.debug(actualDNSServers);
						
		# Check Actual and Expected values are equal
		if(actualDNSServers.sort() !=expectedDNSServers.sort()):                    
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("DNS Servers is not as expected");
		else:
			self.logger.info("Step result:Pass");
					


	def checkNetInterfaces(self):
		"""
		Check if Net Interfaces ( ipmp1, ipmp2, ipmp3, ipmp4 and igb0 ) values are as expected
		"""
		# Expected Dictionary Values
		# Interface name
		# STATE   : 'up' should be always up
		# CLASS   : 'ip' for igb0 and for all other IPoIB it should be "ipmp"
		# LINKS   : -- Not checked .
		# ADDRESS : 'd.d.d.d'
		# LABEL   :

		r1_details = self.storage["nodes"][0][net_eth];
		igb_values =(net_status,net_ip_class,r1_details["ip"],net_eth_label);

		r2_values=self.storage["ipoib"][0][net_ib_default];
		default_values = (net_status,net_class,r2_values["ip"],net_ib_default_label);

		r3_values=self.storage["ipoib"][1][net_ib_mgt];
		mgt_values = (net_status,net_class,r3_values["ip"],net_ib_mgt_label);

		r4_values = self.storage["ipoib"][2][net_ib_storage];
		storage_values = (net_status,net_class,r4_values["ip"],net_ib_storage_label);

		r5_values = self.storage["ipoib"][3][net_ib_inst_storage];
		istorage_values = (net_status,net_class,r5_values["ip"],net_ib_inst_storage_label);

		expectedNetInterfaces = {r1_details["device"]:igb_values, r2_values["device"]:default_values, r3_values["device"]:mgt_values, r4_values["device"]:storage_values, r5_values["device"]:istorage_values }

		self.logger.debug("Expected Net Interfaces ");
		self.logger.debug(expectedNetInterfaces);

		### Get actual network interfaces from ZFS
		# Call your getConfiguredNetInterfaces to get actual interfaces from ZFS
		self.logger.info("Fetching actual interfaces from ZFS");
		netInterfaces=self.zfsServer1.getConfiguredNetInterfaces();
		self.logger.debug("received net Interfaces :");
		self.logger.debug(netInterfaces);

		# Selecting only the rows defined in the property file
		rowListValues=net_ib_rows.split(",");
		
		iNetRow=0;
		iActNetRow=0;
		actualNetInterfaces={};
		for rowValue in rowListValues:
			for key, value in netInterfaces.iteritems():
				iNetRow=0;
				if key==rowValue:
					actualNetInterfaces[key]=(value[0],value[1],value[2].split('/')[0],value[3]);
					iActNetRow=iActNetRow+1;
					break;
				iNetRow=iNetRow+1;
		self.logger.debug("Actual Net Interfaces ");
		self.logger.debug(actualNetInterfaces);

		self.logger.debug("Expected Net Interfaces ");
		self.logger.debug(expectedNetInterfaces.keys());
		self.logger.debug("Actual Net Interfaces ");
		self.logger.debug(actualNetInterfaces.keys());
		
		if expectedNetInterfaces.keys()!=actualNetInterfaces.keys():
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Network interfaces are not as expected");
		else:
			bFlag=False;
			for sKey in expectedNetInterfaces:
				sLstVal=list(set(expectedNetInterfaces[sKey]).intersection(actualNetInterfaces[sKey]));
				eLstVal=list(expectedNetInterfaces[sKey]);
				if  (sorted(sLstVal)==sorted(eLstVal)):
					bFlag=True;
				else :
					bFlag=False;
					break;
		sys.stdout.flush();
		if bFlag:
			self.logger.info("Step result:Pass");
		else:
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Net Interfaces are not as expected"); 			



