#! /usr/bin/python

#Modules required to be installed
import ConfigParser
import traceback;

#Exalogic internal modules
from pylib.exalogic.config.exalogic_configuration import *;
from pylib.exalogic.server.exalogicserver import *;
from pylib.storage.zfs import *;
from pylib.networking.switch.infiniband.nm2 import *;
from tests.exalogic.ecu.ecutest_exceptions import *;

__author__ = "Chen"
__date__ = "$Jul 17, 2015 10:57:16 AM$"

class IBSwitchTests(object):
	"""
	Tests related to IBSwitch
	"""

	def __init__ (self,configurationDirectory,buildNumber=None,logger=None):
		"""
		Constructor for IBSwitch tests
		"""

		self.logger=logger;		
		
		self.rack_config=ExalogicConfiguration(configurationDirectory); 

		# Get rack name
		self.rackName=self.rack_config.getRackName();
		
		#switches is a dictionary object
		self.switches=self.rack_config.getIbSwitchInfo();

		#Get passwords
		self.passwords=self.rack_config.GetPasswords(); 
		switch_ilom_password_info=self.passwords["switch_ilom"];
		#switch_user=switch_ilom_password_info.keys()[1];
		self.switch_user = "root"
		self.switch_password=switch_ilom_password_info[self.switch_user];
		
		self.myswitch = nm2(self.switches[0]['ilom']['host'],self.switches[0]['ilom']['ip'],self.rackName,buildNumber,self.switch_user,self.switch_password,prompt=".*?~\]#",logger=self.logger,timeout=300);

		#Get partition test configurations
		self.test_config = ConfigParser.RawConfigParser();
		configFileNames=self.test_config.read(os.environ['GitSrcDir']+"/oeca/install/pqa/tests/exalogic/ecu/ibswitch/ibswitch_tests.properties");
		
		if(len(configFileNames)==0):
			raise ECUTestFailureError("No properties file found");

		self.test_config_sections = self.test_config.sections()
		
		#Set access types
		self.accesstype_list = ["full", "limited","both"]
		
		# Get compute node list from ECU config
		self.vnodes = self.rack_config.GetVirtualCnodesInfo()
		# Get storage node list from ECU config
		self.snodes = self.rack_config.GetStorageInfo()
		
	#Test:ECU_62	
	def checkOOBPartitionsTest(self,expectedTenants):
		"""
		Check if default partitions exist 
		"""
		try:
			self.logger.info("Checking OOB Partitions for OOB tenants")
			
			#hard coded tenant names for now
			tenantlist=expectedTenants.split(",");
			tenantlist.remove("cloud");
			tenantlist.remove("root");
			
			self.myswitch.makePartitionInfoFile()

			error = False
			#Check every tenant in tenantlist 
			for tenant in tenantlist:
				self.logger.info("Checking default tenant: " + tenant)
				publicname = "tenant-pub-" + tenant
				prvname = "tenant-prv-" + tenant
				pubexist = self.myswitch.doesPartitionExist(publicname)
				prvexist = self.myswitch.doesPartitionExist(prvname)
				if pubexist == 1:
					error = True
					self.logger.error(publicname+" does not exist")
				if prvexist == 1:
					error = True
					self.logger.error(prvname+" does not exist")
			if error:
				raise ECUTestFailureError("OOB Partition names is not as expected")
		except:
			raise ECUTestFailureError("OOB Partition names is not as expected")
		
	#Test:ECU_61
	#Test:ECU_63
	def checkPartitionNameTest(self):
		"""
		Check the name of the partition
		Raise an exception if the partition name doesn't meet expectation
		"""
		try:
			error = False
			self.myswitch.makePartitionInfoFile()
			for partition in self.test_config_sections:				
				#Get expected partition name
				partitionName_exp = self.test_config.get(partition,"name")
				#Get actual partition name
				self.logger.info("Checking partition " + partitionName_exp)
				#self.myswitch.makePartitionInfoFile()
				try:
					partition_obj = self.myswitch.getPartition(partitionName_exp)
					partitionName_act = partition_obj.getName()
					
					if partitionName_act != partitionName_exp:
						error = True
						self.logger.error("Partition name is not as expected"+partitionName_act)
				except:
					error = True
			if error:
				raise ECUTestFailureError("Partition name test fail")
		except:
			#Get partition might raise an error
			self.logger.error("Test result:Fail")
			self.logger.error(traceback.format_exc());
			raise ECUTestFailureError("Partition name test Fail")
	
	#Test:ECU_61
	#Test:ECU_63	
	def checkPartitionTypeTest(self):
		"""
		Check the network type of the partition
		Raise an exception if the network type doesn't meet expectation
		"""
		try:
			error = False
			for partition in self.test_config_sections:
				#Get expected network type
				networkType_exp = self.test_config.get(partition,"type")
				#Get actual network type
				partitionName = self.test_config.get(partition,"name")
				self.myswitch.makePartitionInfoFile()
				partition_obj = self.myswitch.getPartition(partitionName)
				networkType_act = partition_obj.getType()
				self.logger.info("Checking partition " + partition + "network type")
				if networkType_act != networkType_exp:
					error = True
					self.logger.error("Network type should be: " + networkType_exp + "; but is:" + networkType_act)
			if error:
				raise ECUTestFailureError("Network type is not as expected.")
		except:
			#Get partition might raise an error
			self.logger.error("Test result:Fail")
			raise ECUTestFailureError("Partition type test Fail")

	def deleteSwitchInfoFileTest(self):
		"""
		Delete the switch info file corresponding to the buildnumber
		"""
		self.myswitch.deleteSwitchInfoFile();
		self.logger.info("deleting switch info file")
	 
	def checkPartitionMemberAccessTest(self,username,password):
		"""
		Checks the partition member access type.
		Raise an exception if the access type doesn't match or 
		if the member can't be found in the partition
		"""
		
		try:
			error = False
			#Construct a dictionary with keys as hostnames and values as guid list
			#{sca06cn01:[guid1,guid2],sca06cn02:[guid3,guid4]}
			self._makeGuidDictionary(username,password)
			
			# Get expected partition data
			self.logger.info("Starting to check partition data")
			
			for partition in self.test_config_sections:
				self.logger.info("Processing "+str(self.test_config.get(partition,"name"))+" from test properties file");
				partitionName = self.test_config.get(partition,"name")
				# Get actual partition info from the switch
				self.myswitch.makePartitionInfoFile()
				partition_obj = self.myswitch.getPartition(partitionName)
				#Get actual partition member dictionary
				partition_member_act = partition_obj.getMembers()
				
				for accesstype in self.accesstype_list: 
					#Check only if the membership type exists
					self.logger.info("Processing " + accesstype + " in partition " + partitionName)
					if (self.test_config.has_option(partition,accesstype)):
						#Check partition members in access type
						steperror =  self._checkAccess(partition,accesstype,partitionName, partition_member_act)
						error = error or steperror
				
			if error:
				raise ECUTestFailureError("Partition member access type is not as expected")
		except:
			#Get partition might raise an error
			self.logger.error(traceback.format_exc());
			self.logger.error("Test result:Fail")
			raise ECUTestFailureError("Partition member access type test Fail")
			
	def _makeGuidDictionary(self,username,password):
		"""
		Make the Guid dictionary for compute, storage nodes and switches
		where dictionary key is hostname, value is a list of (port) guids
		"""
		try:
			self.serverGuidDict = {}
			error = False
			self.logger.info("Making dictionary of guids and hostnames")
			# Get guids from compute nodes
			for i in range(len(self.vnodes)):
				hostname = self.vnodes[i]['host']
				server=ExalogicServer(name=hostname,ip=self.vnodes[i]['eth-admin']['ip'],user=username,password=password,prompt=".*?\~\]\$",logger=self.logger);
				serverGuidList = server.getGuid()
				self.serverGuidDict[hostname] = serverGuidList
			# Get guids from storage nodes
			storage_username = "root"
			storage_password = self.passwords["storage"][storage_username]

			for i in range(len(self.snodes)):
				hostname = self.snodes["nodes"][i]['host']
				ip = self.snodes["nodes"][i]['eth-admin']['ip']
				server = ZFSController(name=hostname,ip=ip,user=storage_username,password=storage_password,logger=self.logger)
				serverGuidList = server.getGuid()
				self.serverGuidDict[hostname] = serverGuidList

			# Get guids from switches					
			for i in range(len(self.switches)):
				hostname = self.switches[i]['ilom']['host']
				server = nm2(hostname,self.switches[i]['ilom']['ip'],self.rackName,None,self.switch_user,self.switch_password,prompt=".*?~\]#",logger=self.logger)
				serverGuidList = server.getGuid()
				self.serverGuidDict[hostname] = serverGuidList
			
			self.logger.debug(self.serverGuidDict)

		except:
			error = True
			self.logger.error("Cannot log in to hosts")
		
		return error
		
	def _checkAccess(self, partition, accesstype, partitionName, partition_member_act):
		"""
		Check the partition member access given the access type
		partitionName_act is a dictionary with keys as guids and values as accesstype can be full,both,limited
		"""
		error = False
		# Get list of expected members
		member_exp = self.test_config.get(partition,accesstype)
		member_list = self._getMemberList(member_exp)
		for member in member_list:
			self.logger.debug("Checking " + member + " in partition " + partitionName)
			#Get member guids
			if member in self.serverGuidDict:
				member_guids = self.serverGuidDict[member]
				for guid in member_guids:
					#Check if the guid is a member in the partition
					self.logger.debug("Checking " + member + " guid " + guid)
					if guid in partition_member_act:
						if partition_member_act[guid] == accesstype:
							self.logger.debug(guid+"is in the network with "+accesstype+" as expected")
						else:
							error = True
							self.logger.error(guid+" does NOT have the right access type:, expected:"+accesstype+", actual "+partition_member_act[guid])
					else: 
						error = True
						self.logger.error(guid + " is not a member in partition " + partitionName)
			else:
				self.logger.error(member + " is not in server Guid dictionary")
				
		return error
		
	def _getMemberList(self,member_exp):
		"""
		Return a list of members given a string of members
		member_exp is in the following form:
		sn,1,8;cn1,6 
		"""
		# check if there are multiple groups of host names
		semicolonindex = member_exp.find(";")
		if semicolonindex > -1:
			groupList = member_exp.split(";")
		else:
			groupList = [member_exp]
		
		memberList = []
		for group in groupList:
			try: 
				rawlist = group.split(",")
				nodelist = []
				nodetype = rawlist[0]
				start = int(rawlist[1])
				# Check if the end number is a number or n
				if rawlist[2] == "n":
					end = len(self.vnodes)
				else:
					end = int(rawlist[2])
				#Generate full hostnames, e.g. sca06cn01
				for num in range(start,end+1):
					if (num < 10):
						nodename = self.rackName+nodetype+"0"+str(num)
					else:
						nodename = self.rackName+nodetype+str(num)
						
					nodelist.append(nodename)
				memberList += nodelist
			except:
				#Catches any format error
				self.logger.error("ibswitch test config file access type invalid format")
				break
		
		return memberList
		
