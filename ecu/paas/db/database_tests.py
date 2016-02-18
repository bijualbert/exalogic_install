#! /usr/bin/python

from re import *;

# Installed Python modules
import cx_Oracle;

#Exalogic internal modules
from pylib.linux.networkutils import *;
from pylib.db.sql.oracle.oracle import *;
from pylib.servers.server import *;
from pylib.exalogic.config.exalogic_configuration import *;
from tests.exalogic.ecu.ecutest_exceptions import *;

__author__ = "Chen"
__date__ = "$Aug 18, 2015 1:32:16 PM$"

class DatabaseTests(object):
	"""
	Tests related to Database
	"""

	def __init__ (self,username,password,configurationDirectory,logger=None):
		"""
		Constructor for Database tests
		"""
		
		self.logger=logger;
		
		self.rack_config=ExalogicConfiguration(configurationDirectory);                                    
		
		self.vminfo = self.rack_config.getDatabaseNameAddress()
		self.vmhostnames = self.vminfo.keys()
		self.vms = []
		username = "root"
		for hostname in self.vmhostnames:
			server = OracleDBServer(hostname,None,username,password,prompt=".*~]\$",logger=self.logger,timeout=60)
			#newly added for root user
			server = OracleDBServer(hostname,None,username,password,prompt=".*~]#",logger=self.logger,timeout=60)
			self.vms.append(server)
	
	#Test:ECU_73
	def checkDatabaseRunning(self,expectedDatabases):
		"""
		Check if the expected databases is online or not
		"""
		try:
			error = False
			# Process expected databases
			expected_databases = expectedDatabases.split(',')
			
			for vm in self.vms:
				self.logger.info("Checking " + vm.name)
				for database in expected_databases:
					self.logger.info("Checking " + database)
					# Check if the process is running on the vm
					if not vm.isDatabaseRunning(database,"oracle"):
						error = True
						self.logger.error(database + " is not running in " + vm.name)
			if error:
					raise ECUTestFailureError("Databases are not running as expected")
		except:
			self.logger.error(traceback.format_exc());
			raise ECUTestFailureError("Database test Fail")
			
	def checkDatabaseListener(self,expectedDatabases,oracle_home_dir):
		"""
		Check if the listener is running with service configured for each of these databases 
		"""
		
		try:
			error = False
			# Process expected databases
			expected_databases = expectedDatabases.split(',')
			
			for vm in self.vms:
				self.logger.info("Checking " + vm.name)
				# Get actual response
				response = vm.getListenerResponse(oracle_home_dir)
				for db in expected_databases:
					self.logger.info("Checking " + db)
					expected_response = re.compile('.*Instance "'+ db+ '".*status READY.*has.*[1-9]*.*handler')
					# Find expected response in response
					result = re.findall(expected_response,response)
					if len(result) == 0:
						error = True
						self.logger.error(db + " handler is not in " + vm.name)
					
			if error:
					raise ECUTestFailureError("Databases are not as expected")
		except:
			self.logger.error(traceback.format_exc());
			raise ECUTestFailureError("Database test Fail")
	
	def checkDatabaseConnection(self,expectedDatabases,database_username,database_password,listener_port):
		"""
		Check if the connection to databases are working.
		"""
		try:
			error = False
			# Process expected databases
			expected_databases = expectedDatabases.split(',')
			
			for vmname in self.vminfo.keys():
				self.logger.info("Checking " + vmname)
				host = self.vminfo[vmname]
				port = int(listener_port)
				for database in expected_databases:
					self.logger.info("Checking " + database + " connection")
					connectstring = cx_Oracle.makedsn(host, port, service_name=database.upper())
					try:
						# try connect to the database
						connection_obj = cx_Oracle.connect(database_username,database_password,connectstring)
					except:
						error = True
						self.logger.error("Vm "+vmname+" Cannot connect to database"+database)
			if error:
					raise ECUTestFailureError("Database connection test failed")
		except:
			self.logger.error(traceback.format_exc());
			raise ECUTestFailureError("Database test Fail")
		
		
