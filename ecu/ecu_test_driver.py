import sys
import re
import os
import time
import subprocess
import logging

#export PATH=/usr/local/bin:${PATH}
#Modules required to be installed
import pexpect
import json
from netaddr import *
import getopt
import ConfigParser 

#Exalogic internal modules
from tests.exalogic.ecu import *;
from tests.exalogic.ecu.ecutest_exceptions import *;
from tests.exalogic.ecu.iaas import *;
from tests.exalogic.ecu.iaas.nimbula_tests import *;
from tests.exalogic.ecu.ovs import *;
from tests.exalogic.ecu.ovs.ovs_tests import *;
from tests.exalogic.ecu.zfs import *;
from tests.exalogic.ecu.zfs.zfs_tests import *;
from tests.exalogic.ecu.ecu import *;
from tests.exalogic.ecu.ecu.ecu_run_tests import *;
from tests.exalogic.ecu.server.physical_server_tests import *;
from tests.exalogic.ecu.ibswitch.ibswitch_tests import *;
from pylib.servers.server import *;
from tests.exalogic.ecu.server.server_tests import *;
from tests.exalogic.ecu.paas.db.database_tests import *;


def main ():

	### Print sys path
	print "Sys path is:"+str(sys.path);
	### Setup logging

	logger = logging.getLogger("mylog")
	formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
	logger.setLevel(logging.DEBUG)

	streamLogger = logging.StreamHandler(sys.stdout)
	streamLogger.setLevel(logging.DEBUG)
	streamLogger.setFormatter(formatter)

	logFilePath = "my.log"
	fileLogger = logging.FileHandler("ecu_test.log",mode="w");
	fileLogger.setFormatter(formatter)
	fileLogger.setLevel(logging.DEBUG)

	logger.addHandler(fileLogger)
	logger.addHandler(streamLogger)

	### Check inputs
	"Function to check the inputs passed"
	if ( len(sys.argv) < 2 ) :
		logger.error("Number of arguments passed is wrong:"+str(len(sys.argv)));
		logger.error("Usage: ecu_test_driver.py --config_file_dir --seed_node_image_path --physical_image_path \
		--prep_cnodes --install_mode=[factory|notAtFactory] --start_node --end_node --node_list--seed_node=0 --mock_install --configure_network_only \
		--prep_ecu --run_ecu \
		 --test_properties \
		 --preinstall_validation --postinstall_validation");
		sys.exit(1);

	config_file_dir=seed_node_image_path=physical_image_path=artifacts_url=prep_cnodes=prep_ecu=test_properties=configure_network_only=preinstall_validation=postinstall_validation=install_mode="";
	
	(start_node,end_node,seed_node,mock_install,run_ecu,build_number,node_list)=(0,0,1,0,0,0,0);
		
	logger.debug('Arguments');
	logger.debug(sys.argv[1:]);
	
	options, remainder = getopt.getopt(sys.argv[1:], 'a:b:c:d:e:f:g:hij:klm:no:pq:r:', [
		'config_file_dir=', #a
		'seed_node_image_path=', #b
		'physical_image_path=', #c
		'artifacts_url=', #d
		'start_node=', #e
		'end_node=', #f
		'seed_node_index=', #g
		'prep_cnodes', #h
		'prep_ecu', #i
		'test_properties=', #j
		'configure_network_only', #k
		'preinstall_validation', #l
		'postinstall_validation=', #m
		'mock_install', #n
		'install_mode=', #o
		'run_ecu', #p
		'build_number=', #q
		'node_list=' #r
		])


	for opt, arg in options:
			if opt in ('--config_file_dir'):
					config_file_dir= arg;
			elif opt in ('--seed_node_image_path'):
					seed_node_image_path=arg;
			elif opt in ('--physical_image_path'):
					physical_image_path=arg;                    
			elif opt in ('--artifacts_url'):
					artifacts_url=arg;                  
			elif opt in ('--start_node'):
					start_node=arg;
			elif opt in ('--end_node'):
					end_node=arg;
			elif opt in ('--seed_node_index'):
					seed_node=arg;
			elif opt in ('--prep_cnodes'):
					prep_cnodes=1;
			elif opt in ('--prep_ecu'):
					prep_ecu=1;
			elif opt in ('--test_properties'):
					test_properties=arg;					
			elif opt in ('--configure_network_only'):
					configure_network_only=1;
			elif opt in ('--preinstall_validation'):
					preinstall_validation=1;
			elif opt in ('--postinstall_validation'):
					postinstall_validation=arg;    
			elif opt in ('--mock_install'):
					mock_install=1;    
			elif opt in ('--install_mode'):
					install_mode=arg;    
			elif opt in ('--run_ecu'):
					run_ecu=1;    
			elif opt in ('--build_number'):
					build_number=arg; 
			elif opt in ('--node_list'):
					node_list=arg; 
					
	if (end_node==0):
		end_node=start_node;
		
	logger.debug('config_file_dir:'+config_file_dir);
	logger.debug('seed_node_image_path:'+seed_node_image_path);
	logger.debug('start_node:'+str(start_node));
	logger.debug('end_node:'+str(end_node));
	logger.debug('physical_image_path:'+physical_image_path);
	logger.debug('artifacts_url:'+artifacts_url);
	logger.debug('seed_node:'+str(seed_node));
	logger.debug('prep_cnodes:'+str(prep_cnodes));
	logger.debug('configure_network_only'+str(configure_network_only));
	logger.debug('prep_ecu:'+str(prep_ecu));
	logger.debug('test_properties:'+str(test_properties));
	logger.debug('preinstall_validation:'+str(preinstall_validation));
	logger.debug('postinstall_validation:'+str(postinstall_validation));
	logger.debug('mock_install:'+str(mock_install));
	logger.debug('install_mode:'+str(install_mode));
	logger.debug('node_list:'+str(node_list));

	### Get default properties
	config = ConfigParser.RawConfigParser();
	config.read(test_properties);
	
	exitCode=0;
	
	### Check input options    
	if (not config_file_dir):
		logger.error("ECU Json configuration file is mandatory");
		raise InvalidInputsError("ECU Json configuration file is mandatory");

	if (not re.search("^\s*$",postinstall_validation) and ( re.search("^\s*$",test_properties) or not os.path.isfile(test_properties) ) ):
	
		logger.error("ECU test data/properties file is mandatory");
		raise InvalidInputsError("ECU test data/properties file is mandatory");
		
	if ( not prep_cnodes and not prep_ecu and not postinstall_validation and not preinstall_validation ):
		logger.error("Need to provide one of these options: prep_cnodes, prep_ecu, postinstall_validation, preinstall_validation");
		raise InvalidInputsError("Need to provide one of these options: prep_cnodes, prep_ecu, postinstall_validation, preinstall_validation");
		
	if(not re.search("^.*$",install_mode) and install_mode not in ['factory','notAtFactory']):
		logger.error("install_mode should be either factory or notAtFactory");
		raise InvalidInputsError;
		
	if (prep_cnodes):
		
		if ( not physical_image_path or not seed_node_image_path):
			logger.error("Need to provide at least physical image path and seed node image path");
			raise InvalidInputsError;
		
		if (seed_node and not seed_node_image_path):
			logger.error("Need to provide seed node image path");
			raise InvalidInputsError;

		if (re.search("^\s*?$",install_mode)):
			logger.error("Need to provide install_mode as either factory or notAtFactory");
			raise InvalidInputsError("Need to provide install_mode as either factory or notAtFactory");

		if(  (start_node!= 0 or end_node!=0) and node_list!=0):
			logger.error("Cannot provide start_node/end_node and node_list");
			
		EcuRunTests.prepNodes(config_file_dir,None,artifacts_url,seed_node_image_path,physical_image_path,install_mode,seed_node,int(start_node),int(end_node),node_list,configure_network_only,int(mock_install),logger);

			
		
	### Get default properties
	config = ConfigParser.RawConfigParser();
	config.read(test_properties);

	if (prep_ecu):			
		EcuRunTests.ecuPrep(config_file_dir,None,artifacts_url,seed_node_image_path,physical_image_path,install_mode,seed_node,logger);		
	
	if (run_ecu):
		EcuRunTests.ecuInstall(config_file_dir,None,artifacts_url,seed_node_image_path,physical_image_path,install_mode,seed_node,logger);

	if (postinstall_validation!=""):
		
		#########################
		### OVS related tests
		#########################				
		
		ovsTests=OVSTests(config_file_dir,logger);
		
		#Check if OVS OS type is as expected
		if (postinstall_validation=="checkOVSOSType"):
			try:
				ovsTests.checkOVSOSType(expectedOVSOSType=config.get('TestData','ovs_os_type'),ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'));
			except ECUTestFailureError:
				logger.error("OVS OS check failed");
				exitCode=1;
			else:
				logger.info("OVS OS check passed");        
				
		#Check if OVS CPU Count is as expected
		if (postinstall_validation=="checkOVSCPU"):
			try:
				ovsTests.checkOVSCPU(expectedOVSCpuCount=config.get('TestData','ovs_cpu_count'),ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'));
			except ECUTestFailureError:
				logger.error("OVS CPU Count check failed");
				exitCode=1;
			else:
				logger.info("OVS CPU Count check passed");    
		
		#Check if OVS Memory is as expected
		if (postinstall_validation=="checkOVSMemory"):
			try:
				ovsTests.checkOVSMemory(expectedOVSMemory=config.get('TestData','ovs_memory'),ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'));
			except ECUTestFailureError:
				logger.error("OVS Memory check failed");
				exitCode=1;
			else:
				logger.info("OVS Memory check passed");  
				
		#Check if OVS DNS Server is as expected
		if (postinstall_validation=="checkOVSDNSServer"):
			try:
				ovsTests.checkOVSDNSServer(jsonConfigDirectory=config_file_dir,logger=logger);
			except ECUTestFailureError:
				logger.error("OVS DNS Server check failed");
				exitCode=1;
			else:
				logger.info("OVS DNS Server check passed");
		
		#Check if OVS NTP Server is as expected
		if (postinstall_validation=="checkOVSNTPServer"):
			try:
				ovsTests.checkOVSNTPServer(jsonConfigDirectory=config_file_dir,logger=logger);
				print "try block";
			except ECUTestFailureError:
				logger.error("OVS NTP Server check failed");
				exitCode=1;
			else:
				logger.info("OVS NTP Server check passed");        

		#Check if OVS Image Status is as expected
		if (postinstall_validation=="checkOVSImageStatus"):
			try:
				ovsTests.checkOVSImageStatus(ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'));
			except ECUTestFailureError:
				logger.error("Exalogic Image check failed");
				exitCode=1;
			else:
				logger.info("Exalogic Image check passed");        
		
		#########################
		### Physical server related tests
		#########################
		
		physicalServerTests=PhysicalServerTests(config_file_dir,logger);
		
		
		#Check if Firmware Version is as expected
		if (postinstall_validation=="checkFirmVersion"):
			try:
				physicalServerTests.checkFirmVersion(ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'));
			except ECUTestFailureError:
				logger.error("Firmware Version check failed");
				exitCode=1;
			else:
				logger.info("Firmware Version check passed"); 				

		#Check if Interface Name is as expected
		serverTest=ServerTests(config_file_dir,logger);
		if (postinstall_validation=="checkInterfaceName"):
			try:
				serverTest.checkInterfaceName(interfaceName=config.get('TestData','interfaceName'),ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'));
				#serverTest.checkInterfaceName();
			except ECUTestFailureError:
				logger.error("Interface check failed");
				exitCode=1;
			else:
				logger.info("Interface check passed"); 		



		#########################
		### ZFS related tests
		#########################				
		
		#Check if NTP Server is as expected
		if (postinstall_validation=="checkNTPServer"):
			try:
				zfsTests=ZFSTests(config_file_dir,logger);
				zfsTests.checkNTPServer();
			except ECUTestFailureError:
				logger.error("NTP Server check failed");
				exitCode=1;
			else:
				logger.info("NTP Server check passed");
				
		#Check if ZFS Pools are as expected
		if (postinstall_validation=="checkPools"):
				try:
					zfsTests=ZFSTests(config_file_dir,logger);
					zfsTests.checkPools();
				except ECUTestFailureError:
					logger.error("ZFS Pools check failed");
					exitCode=1;
				else:
					logger.info("ZFS Pools check passed");
								
		#Check if ZFS share names are as expected
		if (postinstall_validation == "checkShareName"):
			try:
				zfsTests=ZFSTests(config_file_dir,logger);
				zfsTests.checkShareName() 
			except ECUTestFailureError:
				logger.error("ZFS Share name check failed");
				exitCode=1;
			else:
				logger.info("ZFS Share name check passed");
		
		# Check Projects
		if (postinstall_validation=="checkProjects"):
				try:
					zfsTests=ZFSTests(config_file_dir,logger);
					zfsTests.checkProjects();
				except ECUTestFailureError:
					logger.error("ZFS Projects check failed");
					exitCode=1;
				else:
					logger.info("ZFS Pools check passed");
						
		#Check if DNS Server configuration in ZFS is as expected
		if (postinstall_validation=="checkDNSServers"):

			try:
				zfsTests=ZFSTests(config_file_dir,logger);
				zfsTests.checkDNSServers();
			except ECUTestFailureError:
				logger.error("ZFS DNS Server check failed");
				exitCode=1;
			else:
				logger.info("ZFS DNS Server check passed");				

		#Check if Net Interfaces configuration in ZFS is as expected
		if (postinstall_validation=="checkNetInterfaces"):
			try:
				zfsTests=ZFSTests(config_file_dir,logger);
				zfsTests.checkNetInterfaces();
			except ECUTestFailureError:
				logger.error("ZFS Net Interfaces check failed");
				exitCode=1;
			else:
				logger.info("ZFS Net Interfaces check passed");				
						
		
		#########################
		### ECU Run related tests
		#########################
		
		#Check if ECU has created the bundle containing config & log files 
		if (postinstall_validation=="checkECUArchive"):
				try:
						EcuRunTests.checkECUArchive(jsonConfigDirectory=config_file_dir,ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'),fileloc=config.get('TestData','ecu_archive_loc'),filebundle=config.get('TestData','ecu_archive_bundle'),logger=logger);
				except ECUTestFailureError:
						logger.error("ECU config and log file check failed");
						exitCode=1;
				else:
						logger.info("ECU config and log files check passed");
		
		#Check if ECU bundle has config directory & a log*tgz file 
		if (postinstall_validation=="checkECUArchiveContents"):
				try:
						EcuRunTests.checkECUArchiveContents(jsonConfigDirectory=config_file_dir,ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'),fileloc=config.get('TestData','ecu_archive_loc'),filebundle=config.get('TestData','ecu_archive_bundle'),targetloc=config.get('TestData','ecu_tgt_loc'),logger=logger);
				except ECUTestFailureError:
						logger.error("ECU config and log file check failed");
						exitCode=1;
				else:
						logger.info("ECU config and log file check passed");    
		#Check if ECU run status 
		if (postinstall_validation=="checkEcuRunStatus"):
				try:
						EcuRunTests.checkEcuRunStatus(jsonConfigDirectory=config_file_dir,ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'),fileloc=config.get('TestData','ecu_archive_loc'),filebundle=config.get('TestData','ecu_archive_bundle'),targetloc=config.get('TestData','ecu_tgt_loc'),logfileloc=config.get('TestData','log_file_location'),logger=logger);
				except ECUTestFailureError:
						logger.error("ECU Run status check failed");
						exitCode=1;
				else:
						logger.info("ECU Run  status check passed");    
		#Check if ECU config ,log and ecu.tgz files are deleted
		if (postinstall_validation=="deleteEculogs"):
				try:
						EcuRunTests.deleteEculogs(jsonConfigDirectory=config_file_dir,ovsUser=config.get('TestData','ovs_admin_user'),ovsPassword=config.get('TestData','ovs_admin_password'),fileloc=config.get('TestData','ecu_archive_loc'),filebundle=config.get('TestData','ecu_archive_bundle'),targetloc=config.get('TestData','ecu_tgt_loc'),logfileloc=config.get('TestData','log_file_location'),logger=logger);
				except ECUTestFailureError:
						logger.error("ECU log cleanup check failed");
						exitCode=1;
				else:
						logger.info("ECU log cleanup check passed");
						
		
		### Nimbula tests		
		nimbulaTests=NimbulaTests(config_file_dir,logger);
			
		#Check if Nimbula API is up as expected		
		if (postinstall_validation=="checkNimbulaAPI" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkNimbulaAPI();
			except ECUTestFailureError:
				logger.error("Nimbula API is not up");
				exitCode=1;
			else:
				logger.info("Nimbula API is OK");

				#Check if Nimbula Shapes are available		
		if (postinstall_validation=="checkNimbulaShape" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkNimbulaShape();
			except ECUTestFailureError:
				logger.error("Nimbula shapes are not as expected");
				exitCode=1;
			else:
				logger.info("Nimbula shapes are matching");

		#List object(tenant) using Nimbula API 
		if (postinstall_validation=="checkDefaultTenant" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkDefaultTenant(config.get('TestData','tenant_name'));
			except ECUTestFailureError:
				logger.error("Unable to list Nimbula API object(Tenant)");
				exitCode=1;
			else:
				logger.info("Nimbula API Tenant object successfully listed");
		
		#Check default vEthernet
		if (postinstall_validation=="checkDefaultVethernet" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkDefaultVethernet(config.get('TestData','vethernet_name'));
			except ECUTestFailureError:
				logger.error("Default Vethernet Name Test Failed");
				exitCode=1;
			else:
				logger.info("Default Vethernet Name Test Passed");
		
		#Check default vNet
		if (postinstall_validation == "checkDefaultVnet" or postinstall_validation == "all"):
			try:
				nimbulaTests.checkDefaultVnet(config.get("TestData","vnet_names"))
			except ECUTestFailureError:
				logger.error("Default vNet Name Test Failed");
				exitCode=1;
			else:
				logger.info("Default vNet Name Test Passed");
		
		#Check default vNetreservation
		if (postinstall_validation == "checkDefaultVnetReservation" or postinstall_validation == "all"):
			try:
				nimbulaTests.checkDefaultVnetReservation(config.get("TestData","vnet_reservation_names"))
			except ECUTestFailureError:
				logger.error("Default vNetReservation Name Test Failed");
				exitCode=1;
			else:
				logger.info("Default vNetReservation Name Test Passed");
		
		#Check default orchestration names
		if (postinstall_validation == "checkDefaultOrchestrationName" or postinstall_validation == "all"):
			try:
				nimbulaTests.checkDefaultOrchestrationName(config.get("TestData","orch_names"))
			except ECUTestFailureError:
				logger.error("Default orchestration Name Test Failed");
				exitCode=1;
			else:
				logger.info("Default orchestration Name Test Passed");
		
		#Check if Nimbula nodes have the expected version
		if (postinstall_validation=="checkNimbulaVersion" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkNimbulaVersion(config.get('TestData','nimbula_version'));
			except ECUTestFailureError:
				logger.warn("Nimbula version check failed, please check change in the test properties/data file");
				exitCode=1;				
			else:
				logger.info("Nimbula version check passed");			
		
		#Check if all virtual nodes are part of the Nimbula cluster
		if (postinstall_validation=="checkNimbulaNodes" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkNimbulaNodes();
			except ECUTestFailureError:
				logger.error("Nimbula node/cluster check failed");
				exitCode=1;
			else:
				logger.info("Nimbula node/cluster check passed");      
		
		#Checks for placement of all control Vms on nodes 1 and 2 
		if (postinstall_validation=="checkControlVMPlacement" or postinstall_validation=="all"):
			try:
				expectedinstances = config.get('TestData','instance')
				nimbulaTests.checkControlVMPlacement(expectedinstances);
			except ECUTestFailureError:
				logger.error("ControlVM check failed");
				exitCode=1;
			else:
				logger.info("ControlVM check passed");      
		
		#Check for placement of Management Control Vms Relationships
		if (postinstall_validation=="checkVMRelationship" or postinstall_validation=="all"):
			try:
				nimbulaTests.checkVMRelationship();
			except ECUTestFailureError:
				logger.error("Control VM relationship check failed");
				exitCode=1;
			else:
				logger.info("Control VM relationship check passed");   
		
		#Check for Control VM Node Placement
		if (postinstall_validation=="checkControlVMNodePlacement" or postinstall_validation=="all"):
			try:
				expected = config.get('TestData','instance')
				nimbulaTests.checkControlVMNodePlacement(expected);
			except ECUTestFailureError:
				logger.error("Control VM Node Placement check failed");
				exitCode=1;
			else:
				logger.info("Control VM Node Placement check passed");   
			
		#Check for blacklisted components
		if (postinstall_validation=="checkBlacklistComponent" or postinstall_validation=="all"):
			try:
				expected = config.get('TestData','blacklist')
				nimbulaTests.checkBlacklistComponent(expected);
			except ECUTestFailureError:
				logger.error("Blacklisted component check failed");
				exitCode=1;
			else:
				logger.info("Blacklisted component check passed");   
			
		### IB Tests
		ibswitchTests=IBSwitchTests(config_file_dir,build_number,logger)
		logger.info("build_number is " + str(build_number))
		# Check OOB tenant partition
		if (postinstall_validation=="checkOOBPartitions" or postinstall_validation=="all"):
			try:				
				ibswitchTests.checkOOBPartitionsTest(config.get('TestData','tenant_name'))
			except ECUTestFailureError:
				logger.error("IB OOB partition check failed");
				exitCode=1;
			else:
				logger.info("IB OOB partition check passed");      
		
		# Check OOB infrastructure partition names
		if (postinstall_validation == "checkPartitionName" or postinstall_validation =="all"):
			try:	
				ibswitchTests.checkPartitionNameTest()
			except ECUTestFailureError:
				logger.error("IB infrastructure partition name check failed");
				exitCode=1;
			else:
				logger.info("IB infrastructure partition name check passed");      
	
		# Check OOB infrastructure network types
		if (postinstall_validation == "checkPartitionType" or postinstall_validation =="all"):
			try:
				ibswitchTests.checkPartitionTypeTest()

			except ECUTestFailureError:
				logger.error("IB infrastructure network type check failed");
				exitCode=1;
			else:
				logger.info("IB infrastructure network type check passed");   

		# Check OOB infrastructure partition member access type
		if (postinstall_validation == "checkPartitionMemberAccess" or postinstall_validation == "all"):
			try:
				#Get username and password from test properties file
				#ovs_admin_user=oracleadmin
				#ovs_admin_password=welcome1
				username=config.get('TestData','ovs_admin_user')
				password=config.get('TestData','ovs_admin_password')
				ibswitchTests.checkPartitionMemberAccessTest(username, password)
				### Call this method only in the last test being executed for IBSwitches
				ibswitchTests.deleteSwitchInfoFileTest();
			except :
				logger.error("IB infrastructure partition member access check failed");
				exitCode=1;
				ibswitchTests.deleteSwitchInfoFileTest();
			else:
				logger.info("IB infrastructure partition member access check passed"); 
				ibswitchTests.deleteSwitchInfoFileTest();
				
		### Database Tests
		# Get username and password
		database_linux_username = config.get("TestData","database_linux_username")
		database_linux_password = config.get("TestData","database_linux_password")
		databaseTests=DatabaseTests(database_linux_username,database_linux_password,config_file_dir,logger)

		# Check if the expected databases are running
		if (postinstall_validation == "checkDatabaseRunning" or postinstall_validation == "all"):
			try:
				# Get expected value
				expected = config.get("TestData","expected_database")
				databaseTests.checkDatabaseRunning(expected)
			except :
				logger.error("Database Online test failed");
				exitCode=1;
			else:
				logger.info("Database Online test passed"); 
			
		# Check if the listener is running with service configured for each of these databases 
		if (postinstall_validation == "checkDatabaseListener" or postinstall_validation == "all"):
			try:
				# Get expected value
				expected = config.get("TestData","expected_database")
				oracle_home_dir = config.get("TestData","oracle_home_dir")
				databaseTests.checkDatabaseListener(expected,oracle_home_dir)
			except :
				logger.error("Database Listener test failed");
				exitCode=1;
			else:
				logger.info("Database Listener test passed"); 
		
		# Check if the connections to databases are working.
		if (postinstall_validation == "checkDatabaseConnection" or postinstall_validation == "all"):
			try:
				# Get expected databases and credentials
				expected = config.get("TestData","expected_database")
				database_username = config.get("TestData","database_username")
				database_password = config.get("TestData","database_password")
				listener_port = config.get("TestData","listener_port")
				databaseTests.checkDatabaseConnection(expected,database_username,database_password,listener_port)
			except :
				logger.error("Database Connection test failed");
				exitCode=1;
			else:
				logger.info("Database Connection test passed"); 
		
	return exitCode;

#####
rc=main();
sys.exit(rc);

