#copyright@2008 Jefri Haryono. 
#email : r4inm4ker@gmail.com.


import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as mcmds
import maya.mel as mmel
import math

def statusError(message):
    fullMsg = "Status failed: %s\n" % message
    sys.stderr.write(fullMsg)
    OpenMaya.MGlobal.displayError(fullMsg)
    raise	# called from exception handlers only, reraise exception


kPluginCmdName = "rainUVPrescale"

# command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
    def doIt(self,argList):
       
        st = mcmds.timerX()
        
        allObjs = mcmds.ls(sl=1,fl=1)
       
        if(allObjs == [] or allObjs == None):
            return
       
        uvShellList = []
        
        for eachObj in allObjs:
            allSelected = []
            
            currSelection = eachObj+".map[0]"
            remainingUVs = mcmds.ls(eachObj+".map[*]",fl=1)
            
            while(1):
                mcmds.select(clear=1)
                mcmds.select(currSelection,replace=1)
                mmel.eval("polySelectBorderShell 0")
                
                
                selectedUVs =[]
                selectedUVs = mcmds.ls(sl=1,fl=1)
                allSelected.extend(selectedUVs)
                uvShellList.append(selectedUVs)
                
                
                for eachUVs in selectedUVs:
                    remainingUVs.remove(eachUVs)
               
                
                if(remainingUVs==[] or remainingUVs==None):
                    break
               
                currSelection = remainingUVs[0]
          
        if(len(uvShellList) < 2):
            return
                        
        uvAreaList = []
        polyAreaList =[]
       
        for index, shell in enumerate(uvShellList):
            
            totalUVArea = 0.0
            totalPolyArea = 0.0
            
            mcmds.select(shell,replace=1)
            mmel.eval("textureWindowSelectConvert 1")
            
            selList = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(selList)
            selListIter = OpenMaya.MItSelectionList(selList)
            
            dagPath1=OpenMaya.MDagPath()
            
            component1 = OpenMaya.MObject()
            
            mesh1 = []
            
            i=0
           
            while(not selListIter.isDone()):
                selListIter.getDagPath(dagPath1, component1)
               
                polyIter1 = OpenMaya.MItMeshPolygon(dagPath1,component1)
               
                while(not polyIter1.isDone()):
                    ptrUtil = OpenMaya.MScriptUtil()
                    currAreaPtr = ptrUtil.asDoublePtr()
                    
                    polyIter1.getArea(currAreaPtr,OpenMaya.MSpace.kWorld)
                    
                    currArea = ptrUtil.getDouble(currAreaPtr)
                    
                    ptrUtil = OpenMaya.MScriptUtil()
                    currUVAreaPtr = ptrUtil.asDoublePtr()
                    polyIter1.getUVArea(currUVAreaPtr)
                    
                    currUVArea = ptrUtil.getDouble(currUVAreaPtr)
                    totalPolyArea += currArea
                    totalUVArea += currUVArea
                    
                    polyIter1.next()
                selListIter.next()
            
            uvAreaList.append(totalUVArea)
            polyAreaList.append(totalPolyArea)
    
       
        for index, shell in enumerate(uvShellList):
            if(index==0):
                continue
            
            mcmds.select(shell)
          
            scale = (uvAreaList[0] / polyAreaList[0]) / (uvAreaList[index]/polyAreaList[index])
           
            scale = math.sqrt(scale)
  
            mcmds.polyEditUV(su = scale, sv = scale)
       
        
        totalTime = mcmds.timerX(startTime=st)
        print "total time: " + str(totalTime)

            
        mcmds.select(allObjs,replace=1)
        
        return
        
    
# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( scriptedCommand() )
	
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )
        raise
