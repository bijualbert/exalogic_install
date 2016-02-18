
#Exalogic internal modules
from pylib.exalogic.config.exalogic_configuration import *;
from pylib.servers.server import *;
from pylib.linux.osutils import *;
from pylib.exalogic.ecu.ecu_install import *;
from tests.exalogic.ecu.ecutest_exceptions import *;

__author__ = "Arvind"
__date__ = "$Jun 2, 2015 10:57:16 AM$"

class EcuRunTests(object):
	"""
	Tests related to ECU run
	"""

	@staticmethod
	def checkECUArchive(jsonConfigDirectory,ovsUser,ovsPassword,fileloc,filebundle,logger=None):
		"""
		Check from ECU run status files/logs if ecu logs/config archive is created (/opt/exalogic/tools/data/ecu/ecu.tgz)
		"""

		returnCode=cmdOutput=None;
			
		rack_config=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory); 
		logger.info("Checking config and log files in compute node");
		vnodes=rack_config.GetVirtualCnodesInfo();
		
		server=Server(name=vnodes[1]['host'],ip= vnodes[1]['eth-admin']['ip'],user=ovsUser,password=ovsPassword,prompt=".*?~]\$",logger=logger);

		#Make this file name a test property
		(returnCode,cmdOutput)=server.execCmd("ls "+fileloc+filebundle);			 

		#logger.debug(cmdOutput);

		if "No such file or directory" in cmdOutput:                    
			logger.error("Step result:Fail");
			raise ECUTestFailureError("config and log files not available");
		else:
			logger.info("Step result:Pass");
		

	@staticmethod
	def checkECUArchiveContents(jsonConfigDirectory,ovsUser,ovsPassword,fileloc,filebundle,targetloc,logger=None):
		"""
		Check from ECU run status files/logs if config directory & logs bundle is present in /opt/exalogic/tools/data/ecu/ecu.tgz
		"""
		rack_config=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory); 
		logger.info("Checking config and log files in compute node");
		vnodes=rack_config.GetVirtualCnodesInfo();

		localHost=Server(logger=logger);
		
		returnCode1=cmdOutput1=returnCode2=cmdOutput2=None;

		(returnCode1,cmdOutput1)=osutils.sFtp(vnodes[1]['host'],ovsUser,ovsPassword,"get",fileloc+filebundle,targetloc,logger=logger);
		
		logger.info(cmdOutput1);
		cmdList=["tar","-xvzf",targetloc+filebundle,"-C",targetloc];		

		(returnCode2,cmdOutput2)=localHost.execCmd(command=cmdList);
		
		log = re.search(r'logs_[0-9]+',cmdOutput2,re.S);
		config = re.search(r'config/',cmdOutput2,re.S);

		output=(log.group(0) ,config.group(0));

		if len(output) != 2:                   
			logger.error("Step result:Fail");
			raise ECUTestFailureError("config directory & a log*tgz file not available");
		else:
			logger.info("Step result:Pass");

	@staticmethod
	def checkEcuRunStatus(jsonConfigDirectory,ovsUser,ovsPassword,fileloc,filebundle,targetloc,logfileloc,logger=None):
		"""
		Check from ECU run status of the logs 
		"""

		returnCode=cmdOutput=returnCode1=cmdOutput1=returnCode2=cmdOutput2=returnCode3=cmdOutput3=returnCode4=cmdOutput4=None;

		rack_config=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory); 
		logger.info("Checking ECU Run status");
		vnodes=rack_config.GetVirtualCnodesInfo();

		localHost=Server(logger=logger);

		returnCode1=cmdOutput1=returnCode2=cmdOutput2=None;
		cmdList=["ls",targetloc];		

		(returnCode2,cmdOutput2)=localHost.execCmd(command=cmdList);		
		
		log = re.search(r'logs_[0-9]+.tgz',cmdOutput2,re.S);

		logger.debug("log file name:"+log.group(0));
		logfilename=log.group(0);

		(returnCode3,cmdOutput3)=localHost.execCmd(["tar","-xvzf",targetloc+logfilename,"-C",targetloc]);
		logger.info("Checking ecu_run_progress.out file");
		(returnCode4,cmdOutput4)=localHost.execCmd(["cat",targetloc+logfileloc]);
		match = re.search(r'.*?100 %\s.*?Status: Step 40 executing.*?',cmdOutput4,re.S);
		
		if match:                   
			logger.info("Step result:Pass");
		else:
			 
			logger.error("Step result:Fail");
			raise ECUTestFailureError("ECU Run Fail");     
            
	@staticmethod
	def deleteEculogs(jsonConfigDirectory,ovsUser,ovsPassword,filebundle,targetloc,logfileloc,logger=None):
		"""
		delete the ECU logs ,ecu.tgz and config logs
		"""
		
		returnCode1=cmdOutput1=returnCode2=cmdOutput2=returnCode3=cmdOutput3=returnCode4=cmdOutput5=returnCode5=cmdOutput4=returnCode6=cmdOutput6=returnCode7=cmdOutput7=returnCode8=cmdOutput8=None;
		
		rack_config=ExalogicConfiguration(configurationDirectory=jsonConfigDirectory); 
		logger.info("Deleting the ECU logs ,ecu.tgz and config logs");
		vnodes=rack_config.GetVirtualCnodesInfo();

		localHost=Server(logger=logger);
		cmdList=["ls",targetloc];		
		(returnCode2,cmdOutput2)=localHost.execCmd(command=cmdList);		
		log = re.search(r'logs_[0-9]+.tgz',cmdOutput2,re.S);
		logger.debug("log file name:"+log.group(0));
		logfilename=log.group(0);
		(returnCode3,cmdOutput3)=localHost.execCmd(["rm","-rf",targetloc+logfilename]);
		(returnCode4,cmdOutput4)=localHost.execCmd(["rm","-rf",targetloc+filebundle]); 
		(returnCode5,cmdOutput5)=localHost.execCmd(["rm","-rf",targetloc+"config"]);        
		logger.info("Checking if files are deleted or not");

		(returnCode6,cmdOutput6)=localHost.execCmd("ls "+targetloc+filebundle);
		(returnCode7,cmdOutput7)=localHost.execCmd("ls "+targetloc+logfilename);
		(returnCode8,cmdOutput8)=localHost.execCmd("ls "+targetloc+"config");

		if (returnCode6 == 1 and returnCode7 == 1 and returnCode8 == 1):
			logger.error("ECU Archive logs clean up on local test system done");
			
		else:
			logger.info("ECU Archive logs clean up on local test system failed, please check");            
			raise ECUTestFailureError("config ,ecu and log files were not deleted");

	@staticmethod
	def ecuBasicRunTest(configDirectory,installConfigProperties,artifactsUrl,seedNodeImagePath,physicalImagePath,installMode,seedNode,startNode,endNode,listOfNodes,configureNetworkOnly,mockInstall,logger):
	
		install=EcuInstall(configDirectory,"ecu_install_properties.py",artifactsUrl,seedNodeImagePath,physicalImagePath,seedNode,logger);
		install.prepNodes(installMode,None,startNode,endNode,configureNetworkOnly,mockInstall);
		install.prepEcu();
		install.checkECUPreRequisites();
		install.ecuCleanup();
		install.verifyCleanup();

	@staticmethod
	def prepNodes(configDirectory,installConfigProperties,artifactsUrl,seedNodeImagePath,physicalImagePath,installMode,seedNode,startNode,endNode,listOfNodes,configureNetworkOnly,mockInstall,logger):
                                                                          			
		install=EcuInstall(configDirectory,"ecu_install_properties.py",artifactsUrl,seedNodeImagePath,physicalImagePath,seedNode,logger);
		install.prepNodes(installMode,startNode,endNode,listOfNodes,configureNetworkOnly,mockInstall);

	@staticmethod
	def ecuPrep(configDirectory,installConfigProperties,artifactsUrl,seedNodeImagePath,physicalImagePath,installMode,seedNode,logger):
	
		install=EcuInstall(configDirectory,"ecu_install_properties.py",artifactsUrl,seedNodeImagePath,physicalImagePath,seedNode,logger);
		install.checkECUPreRequisites();
		install.prepEcu();
		install.ecuCleanup();
		install.verifyCleanup();

	@staticmethod
	def ecuInstall(configDirectory,installConfigProperties,artifactsUrl,seedNodeImagePath,physicalImagePath,installMode,seedNode,logger):
	
		install=EcuInstall(configDirectory,"ecu_install_properties.py",artifactsUrl,seedNodeImagePath,physicalImagePath,seedNode,logger);
		install.ecuInstall();
		
