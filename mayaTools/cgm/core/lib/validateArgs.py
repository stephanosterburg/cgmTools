"""
------------------------------------------
cgm_Meta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the Core of the MetaNode implementation of the systems.
It is uses Mark Jackson (Red 9)'s as a base.
================================================================
"""
import maya.cmds as mc
import maya.mel as mel
import copy
import time
import inspect
import sys

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.lib import search
# Shared Defaults ========================================================

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
    
#>>> Basics ============================================================== 
def stringArg(arg = None,noneValid = True):
    """
    Simple string validation
    """
    log.debug(">>> stringArg >> arg = %s"%arg + "="*75)   
    if type(arg) in [str,unicode]:
	return arg
    elif noneValid:
	return False
    else: raise StandardError, ">>> stringArg >> Arg failed: arg = %s | type: %s"%(arg,type(arg))
    
def boolArg(arg = None, calledFrom = None):
    """
    Bool validation
    """
    log.debug(">>> boolArg >> arg = %s"%arg + "="*75)   
    calledFrom = stringArg(calledFrom,noneValid=True)
    if calledFrom: _str_funcName = "%s.validateObjArg(%s)"%(calledFrom,arg)
    else:_str_funcName = "boolArg(%s)"%arg
    
    if type(arg) is bool:
	return arg
    elif type(arg) is int and arg in [0,1]:
	return bool(arg)
    else: raise StandardError, ">>> %s >> Arg failed"%(_str_funcName)
	
def objString(arg = None, mayaType = None, noneValid = False, calledFrom = None):
    """
    validate an objString. Use cgmMeta version for instances
    
    arg -- obj or instance
    mayaType -- maya type to validate to
    noneValid -- whether none is a valid arg
    """
    log.debug(">>> objString >> arg = %s"%arg + "="*75)
    
    calledFrom = stringArg(calledFrom,noneValid=True)
    if calledFrom: _str_funcName = "%s.objString(%s)"%(calledFrom,arg)
    else:_str_funcName = "objString(%s)"%arg
    
    if len(mc.ls(arg)) > 1:
	raise StandardError,"More than one object named %s"%arg
    try:
	argType = type(arg)
	if argType in [list,tuple]:#make sure it's not a list
	    if len(arg) ==1:
		arg = arg[0]
	    elif arg == []:
		arg = None
	    else:
		raise StandardError,"%s >>> arg cannot be list or tuple"%_str_funcName	
	if not noneValid:
	    if arg in [None,False]:
		raise StandardError,"%s >>> arg cannot be None"%_str_funcName
	else:
	    if arg in [None,False]:
		if arg not in [None,False]:log.warning("%s >>> arg fail"%_str_funcName)
		return False
			
	if not mc.objExists(arg):
	    if noneValid: return False
	    else:
		raise StandardError,"%s>>> Doesn't exist: '%s'"%(_str_funcName,arg)
			
	if mayaType is not None and len(mayaType):
	    if type(mayaType) not in [tuple,list]:l_mayaTypes = [mayaType]
	    else: l_mayaTypes = mayaType	    
	    str_type = search.returnObjectType(arg)
	    if str_type not in l_mayaTypes:
		if noneValid:
		    log.warning("%s >>> '%s' Not correct mayaType: mayaType: '%s' != currentType: '%s'"%(_str_funcName,arg,str_type,l_mayaTypes))
		    return False
		raise StandardError,"%s >>> '%s' Not correct mayaType: mayaType: '%s' != currentType: '%s'"%(_str_funcName,arg,str_type,l_mayaTypes)			    	
	return arg
    
    except StandardError,error:
	log.error("%s >>Failure! arg: %s | mayaType: %s"%(_str_funcName,arg,mayaType))
	raise StandardError,error  
    
def objStringList(l_args = None, mayaType = None, noneValid = False,calledFrom = None):
    log.debug(">>> objStringList >> l_args = %s"%l_args + "="*75) 
    calledFrom = stringArg(calledFrom,noneValid=True)    
    if calledFrom: _str_funcName = "%s.objStringList"%(calledFrom)
    else:_str_funcName = "objStringList"    
    try:
	if type(l_args) not in [list,tuple]:l_args = [l_args]
	returnList = []
	for arg in l_args:
	    buffer = validateObjArg(arg,mayaType,noneValid,calledFrom)
	    if buffer:returnList.append(buffer)
	    else:log.warning("%s >> failed: '%s'"%(_str_funcName,arg))
	return returnList
    except StandardError,error:
	log.error("%s >>Failure! l_args: %s | mayaType: %s"%(_str_funcName,l_args,mayaType))
	raise StandardError,error 
    
#>>> Simple Axis ==========================================================================
l_axisDirectionsByString = ['x+','y+','z+','x-','y-','z-'] #Used for several menus and what not

d_stringToVector = {'x+':[1,0,0],
                      'x-':[-1,0,0],
                      'y+':[0,1,0],
                      'y-':[0,-1,0],
                      'z+':[0,0,1],
                      'z-':[0,0,-1]}

d_vectorToString = {'[1,0,0]':'x+',
                      '[-1,0,0]':'x-',
                      '[0,1,0]':'y+',
                      '[0,-1,0]':'y-',
                      '[0,0,1]':'z+',
                      '[0,0,-1]':'z-'}
d_tupleToString = {'(1, 0, 0)':'x+',
                   '(-1, 0, 0)':'x-',
                   '(0, 1,  0)':'y+',
                   '(0,-1,0)':'y-',
                   '(0, 0, 1)':'z+',
                   '(0, 0, -1)':'z-'}
d_shortAxisToLong = {'x':'x+','y':'y+','z':'z+'}

class simpleAxis():
    """ 
    """
    @cgmGeneral.Timer
    def __init__(self,arg):
	_str_funcName = "simpleAxis"    
	log.debug(">>> %s(arg = %s)"%(_str_funcName,arg) + "="*75)
	
        self.str_axis = None
        self.v_axis = None
        
        if arg in d_shortAxisToLong.keys():
            self.str_axis = d_shortAxisToLong.get(arg) or False
            self.v_axis = d_stringToVector.get(self.str_axis) or False
            
        elif arg in d_stringToVector.keys():
            self.v_axis = d_stringToVector.get(arg) or False
            self.str_axis = arg
        
        elif str(arg) in d_vectorToString.keys():
            self.str_axis = d_vectorToString.get(str(arg)) or False 
            self.v_axis = d_stringToVector.get(self.str_axis) or False
	    
        elif str(arg) in d_tupleToString.keys():
            self.str_axis = d_tupleToString.get(str(arg)) or False 
            self.v_axis = d_stringToVector.get(self.str_axis) or False
            
        elif ' ' in list(str(arg)):
            splitBuffer = str(arg).split(' ')
            newVectorString =  ''.join(splitBuffer)
            self.str_axis = d_vectorToString.get(newVectorString) or False
            self.v_axis = d_stringToVector.get(self.str_axis) or False
	    
	if self.str_axis is False or self.v_axis is False:
	    log.info("v_axis: %s"%self.v_axis)
	    log.info("str_axis: %s"%self.str_axis)	    
            raise StandardError, ">>> %s(arg = %s) Failed to validate as a simple maya axis"%(_str_funcName,arg)
	    
    def asString(self):
	return self.str_axis
    def asVector(self):
	return self.v_axis
    
    p_vector = property(asVector)
    p_string = property(asString)

