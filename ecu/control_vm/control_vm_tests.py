#! /usr/bin/python

#Exalogic internal modules
from pylib.exalogic.config.exalogic_configuration import *;
from tests.exalogic.ecu.ecutest_exceptions import *;
import re;
__author__ = "Biju"
__date__ = "$Apr 17, 2015 10:57:16 AM$"

class ControlVMTests(object):
	"""
	Test related to control VMs to be spun up & configured by ECU
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

	def checkControlVMStatus(self):
		"""
		Check if control VMs are up & functional
		"""

		pass;
