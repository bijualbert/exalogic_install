#! /usr/bin/python

from json import*
import ConfigParser
import traceback;

#Exalogic internal modules
from pylib.linux.networkutils import *;
from pylib.exalogic.config.exalogic_configuration import *;
from pylib.exalogic.nimbula.nimbula import *;
from tests.exalogic.ecu.ecutest_exceptions import *;

__author__ = "Arvind"
__date__ = "$Apr 17, 2015 10:57:16 AM$"

class NimbulaTests(object):
	"""
	Tests related to Nimbula as a IAAS framework
	"""

	def __init__ (self,configurationDirectory,logger=None):
		"""
		Constructor for Nimbula tests, initializes an Nimbula object
		"""
		
		self.logger=logger;
		
		# Get nimbula instance & passwords
		self.rack_config=ExalogicConfiguration(configurationDirectory);                
		self.nimbula_info=self.rack_config.GetNimbulaInfo();        
		passwords=self.rack_config.GetPasswords();                

		self.nimbula=Nimbula(host_api=self.nimbula_info['host_api_ip'],nimbula_user="/cloud/administrator",nimbula_password=passwords['api_password']['root'],logger=logger);
	
		#Get nimbula test properties
		self.test_config = ConfigParser.RawConfigParser();
		configFileNames=self.test_config.read(os.environ['GitSrcDir']+"/oeca/install/pqa/tests/exalogic/ecu/iaas/nimbula_tests.properties");
		
		if(len(configFileNames)==0):
			raise ECUTestFailureError("No properties file found");
		
		self.test_config_sections = self.test_config.sections()
		
	def checkNimbulaAPI(self):
		"""
		Test to check if the Nimbula API is up & functional
		"""
		error=1;		
			
		self.logger.info("Checking Nimbula API");
		
		try:				
			self.nimbula.authenticate();
		except:			
			e = sys.exc_info()[1];
			self.logger.error(e);
			self.logger.error("Error connecting to Nimbula API");
			raise ECUTestFailureError("Error connecting to Nimbula API");			
			

	def checkNimbulaVersion(self,expectedNimbulaVersion):        
		"""
		Check if Nimbula version is as expected
		"""

		self.logger.info("Checking Nimbula version");
		self.logger.info("Expected nimbula version from test properties/data:"+expectedNimbulaVersion);

		nimbulaVersion=self.nimbula.getVersion();

		self.logger.info("Actual nimbula version from node:"+self.nimbula_info['host_api_ip']+" is "+nimbulaVersion);

		if(nimbulaVersion!=expectedNimbulaVersion):                    
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Nimbula version is not as expected");
		else:
			self.logger.info("Step result:Pass");

	def checkNimbulaNodes(self):        
		"""
		Check if all virtual compute nodes are in Nimbula cluster and are in active state
		"""        

		if ( self.logger is not None):
			self.logger.info("Checking if compute nodes designated to be virtual are a part of Nimbula cluster");

		# Get expected node list from ECU config
		vnodes=self.rack_config.GetVirtualCnodesInfo();
		physicalNodes=self.rack_config.GetPhysicalCnodesInfo();
		
		nimbulaNodes=self.nimbula.getNodes();
		
		# Check if all expected nodes are in Nimbula cluster and active
		result=1;
		passed=1;
		for i in range(len(vnodes)):        
			if ( self.logger is not None):
				self.logger.debug("Checking if "+vnodes[i]['IPoIB-management']['ip']+" is part of the Nimbula cluster");
				found=0;
				for nNode in nimbulaNodes:
					if (nimbulaNodes[nNode]['ip']==vnodes[i]['IPoIB-management']['ip']):
						found=1;
				if(found!=1):
					if ( self.logger is not None):
						self.logger.error("No, it is not !!...");
					passed=0;

		if (not passed):
			result=0;
			if ( self.logger is not None):
				self.logger.error("Some nodes not a part of Nimbula cluster");
			else:
				self.logger.info("All nodes are in the Nimbula cluster");
					
		#Check if there are any extra nodes in cluster !! (If nodes designated Physical have been added by mistake..)        
		passed=1;
		for nNode in nimbulaNodes:
			found=1;
			for i in range(len(physicalNodes)):
				if (nimbulaNodes[nNode]['ip']==physicalNodes[i]['IPoIB-management']['ip']):
					self.logger.debug("Found "+ nimbulaNodes[nNode]['ip']);
					found=0;                    
			if(not found):
				passed=0;
				result=result and 0;

		if (not passed):
			self.logger.error("Some physical nodes found in Nimbula cluster");
		else:
			self.logger.info("No nodes marked physical found in Nimbula cluster");
						
		#Check if all nodes are active
		passed=1;
		for nNode in nimbulaNodes:
				if (nimbulaNodes[nNode]['state']!="active"):
					if ( self.logger is not None):
						self.logger.error("Node "+nimbulaNodes[nNode]['ip']+" not active");
					result=result and 0;
					passed=0;

		if (not result):
			raise ECUTestFailureError("Nimbula nodes number/state not as expected");
		else:
			self.logger.info("All & only virtual nodes are in the Nimbula cluster and in active state");
			self.logger.info("Step result:Pass");	

	#Test:ECU_64		
	def checkDefaultTenant(self,expectedNimbulaNames):
		"""
		Test to list default or out of box tenant names using Nimbula API 
		"""
		error=1;
		self.logger.info("Listing Nimbula API Tenant");
		defaultTenantNames = self.nimbula.getTenant();
		#print "defaultTenant Names :";
		#print defaultTenantNames;
		TenantNames = re.findall(r"\bname.*?(\w{1,20}-*\w{1,20})",defaultTenantNames,re.M|re.I);
		self.logger.info("Checking Nimbula API actual Tenant Names");
		self.logger.info(TenantNames);lstExpectedNimbulaNames=expectedNimbulaNames.split(',');
		expectedNimbulaNames1=expectedNimbulaNames.split(",");
		self.logger.info("Checking Nimbula API expected Tenant Names");
		self.logger.info(expectedNimbulaNames1);
		error = False
		for x in expectedNimbulaNames1:
			if not x in TenantNames:
				error = True
				self.logger.error(x+" is not in nimbula")
		
		if error:
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Nimbula tenant names is not as expected");

	#Test:ECU_66
	def checkDefaultVethernet(self,expectedNimbulaVnet):
		"""
		Test to Check default vethernet on Nimbula using Nimbula API
		"""
		try:
			#Process the expected vethernet names
			self.logger.info("Processing expected Vethernet names")
			expectedVethernetNameList=expectedNimbulaVnet.split(",")
			
			#Get actual vethernet information from Nimbula API
			self.logger.info("Getting actual Vethernet names")
			actualVnetstring = self.nimbula.getVethernet()
			decoder = JSONDecoder()
			#Process the response
			actualVnetstringDic = decoder.decode(actualVnetstring)
			key =  actualVnetstringDic.keys()[0]
			actualvnetnamelist =[]
			#Make a list of actual vethernet names
			for vnetdict in actualVnetstringDic[key]:
				actualvnetnamelist.append(vnetdict["name"])
			
			Vneterror = False
			#Check if expected Vetherenet shows up in actual
			for vethernet in expectedVethernetNameList:
				if not vethernet in actualvnetnamelist:
					Vneterror = True
					self.logger.error("Expected Vetherenet " + vethernet + " is not in Nimbula")
			if Vneterror:
				raise ECUTestFailureError("Expected Vetherenet not in Nimbula")
			
		except:
			raise ECUTestFailureError("Default Vetherenet test fail")

	#Test:ECU_67		
	def checkDefaultVnet(self,expectedvnetnames):
		"""
		Test to check default Vnet
		"""
		try:			
			
			#Process the expected vNet names
			self.logger.info("Processing expected vNet names")
			expectedvnetNameList=expectedvnetnames.split(",")
			
			#Get actual Vnet
			self.logger.info("Getting actual vNet names")
			actual_vnet_string = self.nimbula.getVnet()
			decoder = JSONDecoder()
			#Process the response
			actualVnetstringDic = decoder.decode(actual_vnet_string)
			key =  actualVnetstringDic.keys()[0]
			actualvnetnamelist =[]
			#Make a list of actual vNet names
			for vnetdict in actualVnetstringDic[key]:
				actualvnetnamelist.append(vnetdict["name"])
				#self.logger.info(vnetdict["name"])
			Vneterror = False
			#Check if expected Vetherenet shows up in actual
			for vnet in expectedvnetNameList:
				if not vnet in actualvnetnamelist:
					Vneterror = True
					self.logger.error("Expected vNet " + vnet + " is not in Nimbula")
			if Vneterror:
				raise ECUTestFailureError("Expected vnet not in Nimbula")
			
		except:
			raise ECUTestFailureError("Default Vetherenet test fail")
		
		
	def checkDefaultVnetReservation(self,expectedNimbulaVnetreservation):
		"""
		Test to list default or out of box Vnetreservation names using Nimbula API
		"""
		try:
			#Process the expected vNet names
			self.logger.info("Processing expected vNet names")
			expectedvnetNameList=expectedNimbulaVnetreservation.split(",")
			
			# Get actual vNet reservation names
			defaultVnetreservationNames = self.nimbula.getVnetReservation();
			processed = json.loads(defaultVnetreservationNames)
			key = processed.keys()[0]

			actualvnetnamelist =[]
			#Make a list of actual vNet reservation names
			for vnetdict in processed[key]:
				actualvnetnamelist.append(vnetdict["name"])
			
			Vneterror = False
			#Check if expected Vetherenet shows up in actual
			for vnet in expectedvnetNameList:
				if not vnet in actualvnetnamelist:
					Vneterror = True
					self.logger.error("Expected vNet " + vnet + " is not in Nimbula")
			if Vneterror:
				raise ECUTestFailureError("Expected vnet not in Nimbula")
				
		except:
			raise ECUTestFailureError("Default Vetherenet test fail")
	
	#Test:ECU_68
	def checkDefaultOrchestrationName(self,expectedOrchestrationName):
		"""
		Check if the orchestration name is as expected
		"""
		try:
			#Process the expected orchestration names
			self.logger.info("Processing expected Orchestration names")
			expectedNameList=expectedOrchestrationName.split(",")
			
			# Get actual orchestration names
			actualdata = self.nimbula.listOrchestrationData()
			processed = json.loads(actualdata)
			key = processed.keys()[0]
			
			actualnamelist =[]
			#Make a list of actual orchestration names
			for dict in processed[key]:
				actualnamelist.append(dict["name"])
			
			error = False
			#Check if expected orchestration name shows up in actual
			for name in expectedNameList:
				if not name in actualnamelist:
					error = True
					self.logger.error("Expected orchestration " + name + " is not in Nimbula")
			if error:
				raise ECUTestFailureError("Expected orchestration not in Nimbula")
			
		except:
			raise ECUTestFailureError("Default orchestration name test fail")
	
	
	def checkNimbulaVersion(self,expectedNimbulaVersion):        
		"""
		Check if Nimbula version is as expected
		"""
		self.logger.info("Checking Nimbula version");
		self.logger.info("Expected nimbula version from test properties/data:"+expectedNimbulaVersion);

		nimbulaVersion=self.nimbula.getVersion();

		self.logger.info("Actual nimbula version from node:"+self.nimbula_info['host_api_ip']+" is "+nimbulaVersion);

		if(nimbulaVersion!=expectedNimbulaVersion):                    
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Nimbula version is not as expected");
		else:
			self.logger.info("Step result:Pass");
	
	#Test:ECU_72	
	def checkNimbulaShape(self):
		"""
		Check if Nimbula shapes are expected
		"""
		
		self.logger.info("Checking Nimbula Shapes");
		expectedNimbulaShape = {};
		
		#file_data = open("./data/shapes.dat", 'r');
		file_data = open(os.environ['GitSrcDir']+"/oeca/install/pqa/tests/exalogic/ecu/data/shapes.dat", 'r');
		rows=file_data.readlines();
		file_data.close();
		
		#check file cotains some data
		if rows is None:
			self.logger.warn("Unable to list the nimbula Shapes. ");
			return None;
		
		#Split the rows for NAMES, CPUS, RAM
		iCnt = 0; rCnt=0;
		row = { };
		
		# Keep the heading in an array
		expectedNimbulaShape={};
		sHead = rows[0].split();
		sHead.pop(0);
		for iVal in rows:
			if ( len(rows[iCnt].split()) == 4 and iCnt > 0 ): 
				row[rCnt]=rows[iCnt].split();
				row[rCnt].pop(0);
				expectedNimbulaShape[rCnt] = dict(zip(sHead,row[rCnt]))  ;
				rCnt = rCnt+1;
			iCnt = iCnt+1;
		
		retNimbulaShape={};
		retNimbulaShape=self.nimbula.getNimbulaShapes();
		
		decoder = JSONDecoder()
		actNimbulaShapeDic = decoder.decode(retNimbulaShape)
		lstKeys =  actNimbulaShapeDic.keys()[0]
		actualNimbulaShape = {};
		iCnt =0;
		for nimbulaShapesDist in actNimbulaShapeDic[lstKeys]:
			nimbulaShapesDist.pop("uri");
			lstNimbulaShapes=[str(nimbulaShapesDist[sHead[0]]),str(nimbulaShapesDist[sHead[1]]),str(nimbulaShapesDist[sHead[2]])];
			actualNimbulaShape[iCnt]= dict(zip(sHead,lstNimbulaShapes));
			iCnt = iCnt+1;
		
		self.logger.info("Actual nimbula Shapes from test properties/data:" );
		self.logger.info(actualNimbulaShape);
		self.logger.info("Expected nimbula Shapes from test properties/data:" );
		self.logger.info(expectedNimbulaShape);
		
		# compares and returns 0 if same; else returns 1
		bEqual = False; 
		for exp_value in expectedNimbulaShape:
			bEqual = False; 
			exp_value = str(exp_value).replace("\'","");
			#exp_value = exp_value.replace("<system_name>",rackName);
			for act_value in actualNimbulaShape:
				act_value = str(act_value).replace("\'","");
				if exp_value == act_value:
					bEqual = True;
		if bEqual:
			self.logger.info("Step result:Passed");
		else:
			self.logger.error("Step result:Fail");
			raise ECUTestFailureError("Nimbula shapes are  not as expected");
		return bEqual;

	#Test:ECU_69
	def checkControlVMPlacement(self,expectedinstances):
		"""
		Checks for placement of all control Vms on virtual management nodes
		"""
		try: 
			#Get cn01,cn02 info on instances
			node_one_two_info= self._makeComputeNodeinstancedict()
			one_two_instances = node_one_two_info.values()
			
			#Process expected VM instances
			expected = expectedinstances.split(",")
			expectedinstances = {}
			for ins in expected:
				expectedinstances[ins]=0
			
			#Get control VM info
			self.logger.info("Getting nimbula instance info...")
			raw_instance_info = self.nimbula.getInstanceInfo()
			uni_key = raw_instance_info.keys()[0]
			instance_infolist = raw_instance_info[uni_key]
			
			#Check the instance name
			error = False
			for instance in instance_infolist:
				if instance["label"] in expected:
					self.logger.info("Checking " + instance["label"])
					ins_name = instance["name"]
					expectedinstances[instance["label"]]=1
			
					if not (ins_name in one_two_instances[0] or ins_name in one_two_instances[1] ):
						error = True
						self.logger.error("instance " + instance["label"] + " is not in cn01 or cn02")
			#Check if every expected instance is visited
			for ins in expected:
				if expectedinstances[ins] == 0:
					error = True
					self.logger.error("Expected instance "+ins+" is not in actual instance")
			if error:
				raise ECUTestFailureError("Control VM test fail")
		except:
			self.logger.error("Test result:Fail")
			raise ECUTestFailureError("Control VM test Fail")
	
	def _makeComputeNodeinstancedict(self):
		"""
		:return: a dictionary with id as key and a list of instance names as value
		"""
		#Get node one and two uuid
		node_one_two_info = self._makeComputeNodedict()
		node_one_two_uuid = node_one_two_info.values()
		
		#Get actual node info
		no_complete = 0
		all_node_info = self.nimbula.listNode()
		#make a dict
		node_one_two_instance_info = {}
		for node in all_node_info:
			if node["uuid"] in node_one_two_uuid:
				no_complete += 1
				node_one_two_instance_info[node["uuid"]]=node["instances"]
			if no_complete == 2:
				break
		return node_one_two_instance_info		
		
		
	def _makeComputeNodeipdict(self):
		"""
		:return: a dictionary with id as key and EoIB-management ip as value
		"""
		vnodes=self.rack_config.GetVirtualCnodesInfo()
		no_complete = 0
		node_ip_dict = {}
		for node in vnodes:
			if node['type'] == 'VirtualMgmt':
				#Get EoIB-management ip address
				eoib = node["EoIB-management"]
				eoib_ip = eoib["ip"]
				node_ip_dict[node['id']] = eoib_ip
				no_complete += 1
			if no_complete == 2:
				break
		return node_ip_dict
	
	def _makeComputeNodedict(self):
		"""
		:return: a dictionary with virtual management nodes EoIB-management ip as key 
		and uid as value
		"""
		#Get ip for virtual management nodes
		node_ip_dict = self._makeComputeNodeipdict()
		#Make a dict with ip as key and UUID as values
		#Get actual uid info for all nodes
		actualnodeinfo = self.nimbula.getNodeUUIDInfo()
		no_complete = 0
		node_one_two_info = {}
		for ip in actualnodeinfo.keys():
			if ip == node_ip_dict[2] or ip == node_ip_dict[1]:
				node_one_two_info[ip] = actualnodeinfo[ip]
				no_complete += 1
			if no_complete == 2:
				break
		return node_one_two_info
	
	#Test 70
	def checkVMRelationship(self):
		"""
		Check for Management Control Vms Relationships
		"""
		try:
			error = False
			
			for orch in self.test_config_sections:	
				#Get orchestration name
				orch_name = self.test_config.get(orch,"name")
				self.logger.info("Checking " + orch_name)
				#Get expected instances
				expected_instances = self.test_config.get(orch,"instances").split(",")
				#Get expected type
				expected_type = self.test_config.get(orch,"type")
				
				#Get actual orchestration data
				actual_orch = self.nimbula.getOrchestration(orch_name)
				actual_instance_info = actual_orch["oplans"][0]["objects"][0]["relationships"][0]
				#Get actual instances
				actual_instances = actual_instance_info["instances"]
				
				#Check instances
				for ins in expected_instances:
					if not ins in actual_instances:
						error = True
						self.logger.error("Expected " + ins + " not in actual instances")
				if len(expected_instances) < len(actual_instances):
					error = True
					self.logger.error("There are unexpected instances")
					self.logger.error("Expected instances: " + expected_instances)
					self.logger.error("Actual instances: " + actual_instances)
					
				#Get actual type
				actual_type = actual_instance_info["type"]
				#Check type
				if not expected_type in actual_type:
					error = True
					self.logger.error("Expected: " + expected_type + " but actually: "+actual_type)
			if error:
				raise ECUTestFailureError("Management Control VM test fail")
		except:
			self.logger.error(traceback.format_exc());
			raise ECUTestFailureError("Management Control VM test fail")
	
	#Test 71
	def checkControlVMNodePlacement(self,expected):
		"""
		Check for Control VM Node Placement
		"""
		try:
			# Get vm name: nimbula name dictionary
			vmnamedict = self._makevmnamedict(expected)
			vmnamelist = vmnamedict.values()
			#print vmnamedict
			# Get node info
			node_info_ip = self._makeComputeNodedict()
			node_one_two_info = dict(zip(node_info_ip.values(),node_info_ip.keys()))
			# Get actual node info from Nimbula API
			node_infolist = self.nimbula.listNode()
			
			# Check if the instances are running
			error = False
			nodesum = 0
			instance_node_dict={}
			for node in node_infolist:
				if node["uuid"] in node_one_two_info.keys():
					nodesum+=1
					ip = node_one_two_info[node["uuid"]]
					self.logger.info("Checking compute node with ip: " + ip)
					actual_instances = node["instances"]
					#Make the server representation of this node
					server = Server(name="cn01",ip=ip,user="oracleadmin",password="welcome1",prompt=".*?~\]\$",logger=self.logger)
					# Check instances on this node
					for instance in actual_instances:
						if instance in vmnamedict.keys():
							#self.logger.info("Checking instance: "+vmnamedict[instance])
							instance_node_dict[vmnamedict[instance]] = ip
							instance_list = instance.split("/")
							instance_name = instance_list[len(instance_list)-1]
							(rc,cmdOut) = server.execCmd("sudo xm list "+instance_name)
							#Process command output
							dataline = cmdOut.split("\r\n")[1]
							status = dataline.split()[4]
							if not ("r" in cmdOut or "b" in status):
								error = True
								self.logger.error(vmnamedict[instance]+"is not running on "+ ip)
				if nodesum == 2:
					break
			
			# Check the actual node type: different/same
			self.logger.info("Checking actual node type...")
			for orch in self.test_config_sections:
				expected_instances = self.test_config.get(orch,"instances").split(",")
				expected_type = self.test_config.get(orch,"type")
				if ("different" in expected_type):
					ip0 = instance_node_dict[expected_instances[0]]
					ip1 = instance_node_dict[expected_instances[1]]
					if ip0 is ip1:
						error = True
						orch_name = self.test_config.get(orch,"name")
						self.logger.error(orch_name + " instances do not run on different nodes as expected")
						self.logger.info(instance_node_dict)
				if ("same" in expected_type):
					ip0 = instance_node_dict[expected_instances[0]]
					for inst in expected_instances:
						if not (ip0 is instance_node_dict[inst]):
							error = True
							orch_name = self.test_config.get(orch,"name")
							self.logger.error(orch_name + " instances do not run on the same node as expected")
							self.logger.info(instance_node_dict)
				
			if error:
				raise ECUTestFailureError("Control VM Node Placement test fail")
		except:
			self.logger.error(traceback.format_exc());
			raise ECUTestFailureError("Control VM Node Placement test fail")
			
			
	def _makevmnamedict(self,expectedinstances):
		"""
		: return: a dictionary with VM name as value and nimbula name as key
		"""
		#Process expectedlist
		expected = expectedinstances.split(",")
		#expected.remove("exalogic-grill-server-vm")

		#Get instance info
		self.logger.info("Getting nimbula instance info...")
		raw_instance_info = self.nimbula.getInstanceInfo()
		uni_key = raw_instance_info.keys()[0]
		instance_infolist = raw_instance_info[uni_key]
		
		#Check every instance
		vmnamedict = {}
		for instance in instance_infolist:
			if instance["label"] in expected:
				vmnamedict[instance["name"]] = instance["label"]
				
		error = False
		#Check if every expected instance is visited
		for exp in expected:
			if not exp in vmnamedict.values():
				error = True
				self.logger.info("Expected instance " + exp + " does not exist")
		if error:
			raise ECUTestFailureError("Some expected instances are missing.")
		
		return vmnamedict
	
	def checkBlacklistComponent(self,expected):
		"""
		Check all the blacklisted component where all operations are blacklisted
		Operations: get for now
		"""
		#Process expectedlist
		blacklist = expected.split(",")
		operations = ['GET']
	
		errorlist = []
		error = False
		#Check every component
		for comp in blacklist:
			self.logger.info("Checking " + comp)
			obj = '/' + comp +'/'
			for op in operations:
				try:
					res = self.nimbula.doRESTOp(obj,op)
					#this is no error below this line
					errorlist.append(op+" "+obj)
					error = True
				except:
					self.logger.info(op+ " "+obj + " is blacklisted")
		
		if error:
			self.logger.error("List of not blacklisted component:")
			print errorlist
			raise ECUTestFailureError("Some components are not blacklisted")