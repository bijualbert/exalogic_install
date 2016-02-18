
__author__="Biju"
__date__ ="$Apr 18, 2015 3:10:35 AM$"

class ECUTestFailureError(Exception):
    """Exception raised for ECU test validation errors

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

class InvalidInputsError(Exception):
    """Exception raised for invalid inputs provided to automation

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

		
