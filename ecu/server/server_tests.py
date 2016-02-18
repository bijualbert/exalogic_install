#! /usr/bin/python

import sys;
import logging;
import tarfile;
import re;
from pylib.exalogic.config.exalogic_configuration import *;
from pylib.storage import *;
from pylib.servers.server import *;
from pylib.linux.osutils import *;

from pylib.exalogic.ecu.ecu_install import *;
from tests.exalogic.ecu.ecutest_exceptions import *;
#Import test property files. 
from tests.exalogic.ecu.data.ecu_test_properties import *;
global logger;
import requests;
__author__ = "Shilpa"
__date__ = "$Apr 17, 2015 10:57:16 AM$"

class ServerTests(object):
	"""
	Test related to configuration to be done by ECU on the physical Exalogic servers
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

	def checkInterfaceName(self,ovsUser,ovsPassword,interfaceName):
		"""
		Check if Interface Name is as expected
		"""                
		failure=0;
		
		for i in range(len(self.vnodes)): 

			### Get interface name, compares the ip and the status for every node and check against expected value
			server = Server(name=self.vnodes[i]['host'],ip= self.vnodes[i]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?\~\]\$",logger=self.logger);
			n = server.getNetworkInterfaces();
			self.logger.info(n);
								
			strInterface = interfaceName.split(',');

			failureBond2=0;
			failureBond3=0;
			failureBond6=0;
			failureeth0=0;
			 
			for key in n:
				A = key;
				if A["name"] == strInterface[0]:
					failureBond2=1;
					val1 = A["ip"];
					val2 = self.vnodes[i]['IPoIB-management']['ip'];
					ipoib_mgmt = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',val1,re.M);
					final = ipoib_mgmt.group(0);
					if final == val2:
						self.logger.debug("IP of ipoib-management ie bond1 is :"+val2+" IP retrieved is : "+final);
					else:
						self.logger.error("IP mismatch ipoib-management ie bond1 ip :"+val2+"IP retrieved is : "+final);
					if A["status"] == "UP":
						self.logger.debug("The interface Bond2 is UP");
					else:
						self.logger.error("The interface Bond2 is Down");

				if A["name"] == strInterface[1]:
					failureBond3=1;
					val3 = A["ip"];	
					val4 = self.vnodes[i]['IPoIB-storage']['ip'];
					ip_storage = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',val3,re.M);
					final = ip_storage.group(0);					
					if final == val4:
						self.logger.debug("IP of ip_storage ie bond3 is :"+val4+" IP retrieved is : "+final);
					else:
						self.logger.error("IP mismatch ip_storage ie bond3 ip :"+val4+"IP retrieved is : "+final);
					
					if A["status"] == "UP":
						self.logger.debug("The interface Bond3 is UP");
					else: 
						self.logger.error("The interface Bond3 is Down");
				if A["name"] == strInterface[2]:
					failureBond6=1;
					val5 = A["ip"];
					val6 = self.vnodes[i]['EoIB-management']['ip'];
					eoib_mgmt = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',val5,re.M);
					final = eoib_mgmt.group(0);					
					if final == val6:
						self.logger.debug("IP of eoib-management ie bond6 is :"+val6+" IP retrieved : "+final);
					else:
						self.logger.error("IP mismatch eoib-management ie bond6 ip :"+val6+"IP retrieved : "+final);
					if A["status"] == "UP":
						self.logger.debug("The interface Bond6 is UP");
					else: 
						self.logger.error("The interface Bond6 is Down");
				if A["name"] == strInterface[3]:
					failureeth0=1;
					val7 = A["ip"];
					val8 = self.vnodes[i]['eth-admin']['ip'];
					eth_admin = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',val7,re.M);
					final = eth_admin.group(0);					
					if final == val8:
						self.logger.debug("IP of br-eth0-0 is :"+val8+" IP retrieved is : "+final);
					else:
						self.logger.error("IP mismatch br-eth0-0 ip :"+val8+"IP retrieved is : "+final);					
					if A["status"] == "UP":
						self.logger.debug("The interface br-eth0-0 is UP");
					else: 
						self.logger.error("The interface br-eth0-0 is Down");
		
		
		if ( failureBond2==0 ):
			self.logger.error("Network Interface Bond2 is down");
			raise ECUTestFailureError("Network interface is not up over some compute nodes");
		if ( failureBond3==0 ):
			self.logger.error("Network Interface Bond3 is down");
			raise ECUTestFailureError("Network interface is not up over some compute nodes");
		if ( failureBond6==0 ):
			self.logger.error("Network Interface Bond6 is down");
			raise ECUTestFailureError("Network interface is not up over some compute nodes");	
		if ( failureeth0==0 ):
			self.logger.error("Network Interface br-eth0 is down");
			raise ECUTestFailureError("Network interface is not up over some compute nodes");					

		if ( failure==0 ):
			self.logger.error("Network Interface Verification result:Fail");
			raise ECUTestFailureError("Network interface is not up over some compute nodes");
		else:
			self.logger.info("Network Interface Verification result:Pass");							
					


		
