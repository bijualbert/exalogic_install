#!/usr/bin/python

#Import test property files. 
from tests.exalogic.ecu.data.ecu_test_properties import *;

#Exalogic internal modules
from pylib.exalogic.config.exalogic_configuration import *;
from tests.exalogic.ecu.ecutest_exceptions import *;
from pylib.servers.server import *;
from pylib.exalogic.server.exalogicserver import *;

__author__ = "Shilpa"
__date__ = "$Apr 17, 2015 10:57:16 AM$"

class OVSTests(object):
	"""
	Tests check OVS layer configuration to be done by ECU
	"""
	def __init__ (self,configurationDirectory,logger=None):
		"""
		Constructor for PhysicalServerTests tests, initializes the server object
		"""
		
		self.logger=logger;

		# Get compute server host name,ip,username and password
		self.rack_config=ExalogicConfiguration(configurationDirectory);	
		# Get expected node list from ECU config
		self.vnodes=self.rack_config.GetVirtualCnodesInfo();
		
	def checkOVSOSType(self,expectedOVSOSType,ovsUser,ovsPassword):        
		"""
		Check if OVS OS type is as expected
		"""                
		failure=0;

		if ( self.logger is not None):
			self.logger.info("Expected OVS OS:"+expectedOVSOSType);

		for i in range(len(self.vnodes)): 

			### Get actual OS for every node and check against expected value
			server=Server(name=self.vnodes[i]['host'],ip= self.vnodes[i]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?\~\]\$",logger=self.logger);
			os = server.getOS();
			self.logger.debug("Actual OVS OS:"+os);           
					
			if(os!=expectedOVSOSType):                    
				failure=1;
				self.logger.error("OS Type is not as expected, expected OS type is "+expectedOVSOSType+", actual is "+os+ " for "+server.name);

		if ( failure ):
			self.logger.error("OS Type Verification Step result:Fail");
			raise ECUTestFailureError("OS Type is not as expected for some compute nodes");
		else:
			self.logger.info("OS Type Verification result:Pass");
					

	def checkOVSCPU(self,expectedOVSCpuCount,ovsUser,ovsPassword):        
		"""
		Check if OVS CPU Count is as expected
		"""                
		failure=0;

		if ( self.logger is not None):
			self.logger.info("Expected OVS CPU Count:"+expectedOVSCpuCount);

		for i in range(len(self.vnodes)): 

			### Get actual cpu count for every node and check against expected value
			server=Server(name=self.vnodes[i]['host'],ip= self.vnodes[i]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?\~\]\$",logger=self.logger);
			cpu = server.getCPU();
			self.logger.debug("Actual CPU count:"+cpu);           
					
			if(cpu!=expectedOVSCpuCount):                    
				failure=1;
				self.logger.error("OS CPU Count is not as expected, expected OS CPU Count is "+expectedOVSCpuCount+", actual is "+cpu+ " for "+server.name);

		if ( failure ):
			self.logger.error("OVS CPU Count Verification result:Fail");
			raise ECUTestFailureError("OVS CPU Count is not as expected for some compute nodes");
		else:
			self.logger.info("OVS CPU Count result:Pass");


	def checkOVSMemory(self,expectedOVSMemory,ovsUser,ovsPassword):        
		"""
		Check if OVS memory is as expected
		"""                
		failure=0;

		for i in range(len(self.vnodes)): 

			### Get actual Memory for every node and check against expected value
			server=Server(name=self.vnodes[i]['host'],ip= self.vnodes[i]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?\~\]\$",logger=self.logger);
			memory = server.getMemory();
			self.logger.debug("Actual Memory:"+memory);           
					
			if(memory not in expectedOVSMemory):                    
				failure=1;
				self.logger.error("OVS Memory is not as expected, expected OVS Memory is "+expectedOVSMemory+", actual is "+memory+ " for "+server.name);

		if ( failure ):
			self.logger.error("OVS Memory Verification result:Fail");
			raise ECUTestFailureError("OVS Memory is not as expected for some compute nodes");
		else:
			self.logger.info("OVS Memory result:Pass");			

				
	@staticmethod
	def checkOVSDNSServer(jsonConfigDirectory,logger=None):
		"""
		Check if OVS DNS Server details are as expected
		"""                
		
		### Instantiate a rack config object
		rack_config=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory);                

		### Get expected OVS DNS servers from json files using rack configuration instance
		### Get the value from common-host-config.json file with the property "dns_servers"
		OVSDNSServers=rack_config.GetDNSServers();
		expectedOVSDNSServers = OVSDNSServers;
		logger.debug("Expected DNS servers");        
		logger.debug(expectedOVSDNSServers);
		rackConfig=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory);                        
		
		# Get expected node list from ECU config
		cNodes=rack_config.GetCnodesInfo();
		
		bFlag=True;
		for iCnt in range(len(cNodes)): 
						
			### Get actual DNS Server for every node and check against expected value
			server=Server(name=cNodes[iCnt]['host'],ip=cNodes[iCnt]['eth-admin']['ip'],user=ovs_admin_user,password=ovs_admin_password,prompt=".*?\~\]\$",logger=logger);
			actualOVSDNSServer = server.getConfDNSServer();
			logger.debug("Actual DNS Server:");
			logger.debug(actualOVSDNSServer);           
			
			if(actualOVSDNSServer!=expectedOVSDNSServers):                    
				bFlag=False;
				logger.error("DNS servers are not as expected, expected OVS DNS Server is ");
				logger.error(expectedOVSDNSServers);
				logger.error(", actual is ");
				logger.error(actualOVSDNSServer);
				logger.error("for "+server.name);
				
		if ( bFlag==False ):
			logger.error("OVS DNS Server  Verification Step result:Fail");
			raise ECUTestFailureError("OVS DNS Server is not as expected for some compute nodes");
		else:
			logger.info("OVS DNS Server Verification result:Pass");
					
	@staticmethod
	def checkOVSNTPServer(jsonConfigDirectory,logger=None):        
		"""
		Check if OVS NTP Server details are as expected
		"""
		
		### Instantiate a rack config object
		rack_config=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory);                

		### Get expected NTP servers from json files using rack configuration instance
		### Get the value from common-host-config.json file with the property "dns_servers"		
		expectedOVSNTPServers=rack_config.GetNTPServerIP();		
		logger.debug("Expected OVS NTP servers");        
		logger.debug(expectedOVSNTPServers);
		
		rackConfig=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory);                        
		
		# Get expected node list from ECU config
		cNodes=rack_config.GetCnodesInfo();
		
		bFlag=True;
		for iCnt in range(len(cNodes)): 
			
			### Get actual NTP Server for every node and check against expected value
			server=Server(name=cNodes[iCnt]['host'],ip=cNodes[iCnt]['eth-admin']['ip'],user=ovs_admin_user,password=ovs_admin_password,prompt=".*?\~\]\$",logger=logger);
			actualOVSNTPServer = server.getConfNTPServer();
			logger.debug("Actual NTP Server:");
			logger.debug(actualOVSNTPServer);           
					
			if(actualOVSNTPServer!=expectedOVSNTPServers):                    
				bFlag=False;
				logger.error("NTP servers are not as expected, expected OVS NTP Server is ");
				logger.error(expectedOVSNTPServers);
				logger.error(", actual is ");
				logger.error(actualOVSNTPServer);
				logger.error("for "+server.name);
				
		if ( bFlag==False ):
			logger.error("OVS NTP Verification Step result:Fail");
			raise ECUTestFailureError("OVS NTP is not as expected for some compute nodes");
		else:
			logger.info("OVS NTP Verification result:Pass");
	
	def checkOVSImageStatus(self,ovsUser,ovsPassword):
		"""
		Check if OVS Image Status is as expected
		"""
		
		if ( self.logger is not None):
			self.logger.info("Checking OVS Image Status");

		result=True;
		for i in range(len(self.vnodes)):

			server=ExalogicServer(name=self.vnodes[i]['host'],ip= self.vnodes[i]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?\~\]\$",logger = self.logger);
			server.updateImageInfo()
			image = server.getImageStatus()
			self.logger.debug("Exalogic Image info :"+image);

			if(not re.search(r".*?SUCCESS.*?",image,re.S|re.I)):
				result=False;
 
		if (not result):
			if (self.logger is not None):
				self.logger.error("Exalogic Image Status Step result:Fail");
				raise ECUTestFailureError("Exalogic Image Status is not as expected");
			else:
				self.logger.info("Exalogic Image Status Step result:Pass");


