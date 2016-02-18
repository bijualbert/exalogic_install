#!/usr/bin/python

#Exalogic internal modules
from pylib.exalogic.config.exalogic_configuration import *;
from pylib.servers.server import *;
from tests.exalogic.ecu.ecutest_exceptions import *;
from tests.exalogic.ecu.ovs.firmware_properties import *;

__author__ = "Shilpa"
__date__ = "$Apr 17, 2015 10:57:16 AM$"

class PhysicalServerTests(object):
	"""
	Tests check physical server configuration to be done by ECU
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
	
	def checkFirmVersion(self,ovsUser,ovsPassword):        
		"""
		Check if Firmware Version is as expected
		"""                
		failure=0;

		if ( self.logger is not None):
			self.logger.info("Expected Firmware Version");
		

		for i in range(len(self.vnodes)): 

			### Get the firmware version for every node and check against expected value
			server=Server(name=self.vnodes[i]['host'],ip= self.vnodes[i]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?\~\]\$",logger=self.logger);
			pName = server.getServerModel();
			
			self.logger.debug("Model:"+pName);
			
			fware = server.getFirmWare();
			self.logger.debug("Firmware Version: "+fware);  
			
			if pName == "M2":				
				self.logger.debug("Actual Firmware version is :"+fware+" Expected version is :"+X2_version);
				if(fware!=X2_version):                    
					failure=1;
					self.logger.error("Firmware version is not as expected, expected version is "+X2_version+", actual is "+fware+ " for "+server.name);
			elif pName == "M3":
				
				self.logger.debug("Firmware version is :"+fware+" Expected version is :"+X3_version);
				if(fware!=X3_version):                    
					failure=1;
					self.logger.error("Firmware version is not as expected, expected version is "+X3_version+", actual is "+fware+ " for "+server.name);
			elif pName == "X4":
				
				self.logger.debug("Firmware version is :"+fware+" Expected version is :"+X4_version);	
				if(fware!=X4_version):                    
					failure=1;
					self.logger.error("Firmware version is not as expected, expected version is "+X4_version+", actual is "+fware+ " for "+server.name);
			elif pName == "X5":
				
				self.logger.debug("Firmware version is :"+fware+" Expected version is :"+X5_version);	
				if(fware!=X5_version):                    
					failure=1;
					self.logger.error("Firmware version is not as expected, expected version is "+X5_version+", actual is "+fware+ " for "+server.name);
			else:
				self.logger.error("Unknown model of server");	
				failure=1;
					
		if ( failure ):
			self.logger.error("Firmware Version Verification result:Fail");
			raise ECUTestFailureError("Firmware version is not same over some compute nodes");
		else:
			self.logger.info("Firmware Version result:Pass");	
