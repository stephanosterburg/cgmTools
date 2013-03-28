"""
------------------------------------------
nameTools: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class Factory for 
================================================================
"""
# From Python =============================================================
import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.lib import (lists,
                     search,
                     dictionary,
                     settings,
                     attributes)

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()
        
#>>>Utilities
#==================================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnSceneObjectsNameDictMap(**a):   
    sceneTransformObjects =  mc.ls(shortNames = True,**a)

    SceneObjectNameDict = {}

    for obj in sceneTransformObjects:
        dictBuffer = returnObjectGeneratedNameDict(obj)
        if dictBuffer:
            SceneObjectNameDict[obj] = dictBuffer

    if not SceneObjectNameDict:
        return False
    return SceneObjectNameDict
      
#@r9General.Timer   
def returnCGMOrder():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the order for names in a list format

    ARGUMENTS:
    Nothin

    RETURNS:
    order(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    orderBuffer = dict.get('nameOrder')
    return (orderBuffer.split(','))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnCGMDivider():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the divider string

    ARGUMENTS:
    Nothin

    RETURNS:
    divider(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    return dict.get('nameDivider')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnCGMSetting(setting):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the divider string

    ARGUMENTS:
    Nothin

    RETURNS:
    divider(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    return (dict.get(setting))


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnRawGeneratedName(obj,ignore=[False]):
    """  
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name

    ARGUMENTS:
    obj(string) - object
    ignore(list) -  only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    divider = returnCGMDivider()
    order = returnCGMOrder()

    nameBuilder=[]
    #>>> Dictionary driven order
    for item in order:
        buffer = rawNamesDict.get(item)
        if buffer > 0 and item not in ignore:
            nameBuilder.append(buffer)
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnCombinedNameFromDict(nameDict):
    """  
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name

    ARGUMENTS:
    obj(string) - object
    ignore(string) - default is 'none', only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    divider = returnCGMDivider()
    order = returnCGMOrder()

    nameBuilder=[]
    #>>> Dictionary driven order
    for item in order:
        buffer = nameDict.get(item)
        buffer = search.returnTagInfoShortName(buffer,item)
        if buffer > 0 and buffer != 'ignore':
            if '|' or '[' or ']' in buffer:
                bufferList = list(buffer)
                for i in buffer:
                    if i == '[' or i == ']' or i == '|':
                        bufferList.remove(i) 
                    elif i == '.':
                        cnt = buffer.index(i)
                        bufferList.pop(cnt)
                        bufferList.insert(cnt,'_')
                    elif i == ':':
                        cnt = bufferList.index(i)
                        bufferList.pop(cnt)
                        bufferList.insert(cnt,'to')
                buffer = ''.join(bufferList)
                
            nameBuilder.append(buffer)
    
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectGeneratedNameDict(obj,ignore=[False]):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated dictionary of name info

    ARGUMENTS:
    obj(string) - object
    ignore(string) - default is 'none', only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    namesDict(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if type(ignore) is not list:ignore = [ignore]    
    typesDictionary = dictionary.initializeDictionary(typesDictionaryFile)
    namesDictionary = dictionary.initializeDictionary(namesDictionaryFile)
    settingsDictionary = dictionary.initializeDictionary(settingsDictionaryFile)
    namesDict={}
    divider = returnCGMDivider()
    order = returnCGMOrder()
    nameBuilder = []
    #>>> Get our cgmVar_iables
    userAttrs = attributes.returnUserAttributes(obj)
    cgmAttrs = lists.returnMatchList(userAttrs,order)
    #>>> Tag ignoring
    if ignore:
        for i in ignore:
            if i in order:
                order.remove(i)

    #>>> Geting our data
    for tag in order:
        tagInfo = search.findRawTagInfo(obj,tag)
        if tagInfo is not False:
            #if mc.objExists(tagInfo):
                #tagInfo = mc.ls(tagInfo,sn=True)[0]
                #log.info("shortening")
            namesDict[tag] = (tagInfo)
    """ remove tags up stream that we don't want if they don't exist on the actual object"""
    if mc.objExists(obj+'.cgmTypeModifier') != True:
        if namesDict.get('cgmTypeModifier') != None:
            namesDict.pop('cgmTypeModifier')   

    #>>> checks if the names exist as objects or it's a shape node
    ChildNameObj = False
    nameObj = search.returnTagInfo(obj,'cgmName')
    typeTag = search.returnTagInfo(obj,'cgmType')
    isType = search.returnObjectType(obj)
    childrenObjects = search.returnChildrenObjects(obj)
    """first see if it's a group """
    if isType == 'group' and typeTag == False:
        """ if it's a transform group """
        groupNamesDict = {}
        if not nameObj:
            groupNamesDict['cgmName'] = childrenObjects[0]
        else:
            groupNamesDict['cgmName'] = nameObj
        groupNamesDict['cgmType'] = typesDictionary.get('transform')
        if namesDict.get('cgmPosition') != None:
            groupNamesDict['cgmPosition'] = namesDict.get('cgmPosition')        
        if namesDict.get('cgmDirection') != None:
            groupNamesDict['cgmDirection'] = namesDict.get('cgmDirection')
        if namesDict.get('cgmDirectionModifier') != None:
            groupNamesDict['cgmDirectionModifier'] = namesDict.get('cgmDirectionModifier')
        if namesDict.get('cgmTypeModifier') != None:
            groupNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
        return groupNamesDict
        """ see if there's a name tag"""
    elif nameObj != None or isType == 'shape':
        """if there is, does it exist """
        if mc.objExists(nameObj) == True:
            """basic child object with cgmName tag """
            childNamesDict = {}
            childNamesDict['cgmName'] = namesDict.get('cgmName')
            childNamesDict['cgmType'] = namesDict.get('cgmType')
            if namesDict.get('cgmPosition') != None:
                childNamesDict['cgmPosition'] = namesDict.get('cgmPosition')            
            if namesDict.get('cgmDirection') != None:
                childNamesDict['cgmDirection'] = namesDict.get('cgmDirection')
            if namesDict.get('cgmNameModifier') != None:
                childNamesDict['cgmNameModifier'] = namesDict.get('cgmNameModifier')
            if namesDict.get('cgmDirectionModifier') != None:
                childNamesDict['cgmDirectionModifier'] = namesDict.get('cgmDirectionModifier')
            if namesDict.get('cgmTypeModifier') != None:
                childNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
            return childNamesDict
        elif isType == 'shape' or 'Constraint' in isType:
            """if so, it's a child name object"""
            childNamesDict = {}
            childNamesDict['cgmName'] = search.returnParentObject(obj,False)
            childNamesDict['cgmType'] = namesDict.get('cgmType')
            return childNamesDict
        elif typeTag == 'infoNull':
            """if so, it's a special case"""
            moduleObj = search.returnMatchedTagObjectUp(obj,'cgmType','module')
            masterObj = search.returnMatchedTagObjectUp(obj,'cgmType','master')
            if moduleObj != False:
                moduleName = returnUniqueGeneratedName(moduleObj,ignore='cgmType')
                childNamesDict = {}
                childNamesDict['cgmName'] = (moduleName+'_'+nameObj)
                childNamesDict['cgmType'] = namesDict.get('cgmType')
                return childNamesDict   
            elif masterObj != False:
                masterName = returnUniqueGeneratedName(masterObj,ignore='cgmType')
                childNamesDict = {}
                childNamesDict['cgmName'] = (masterName+'_'+nameObj)
                childNamesDict['cgmType'] = namesDict.get('cgmType')
                return childNamesDict   
            else:
                return namesDict
        else:
            return namesDict
    else:
        return namesDict
