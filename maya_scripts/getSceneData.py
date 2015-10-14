__author__ = 'Natasha'

import sys
args = sys.argv

this_script = args[0]  #this will be the name of this file
target_file = args[1]  #this would be the first argument you passed in

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

cmds.file(target_file, open = True, force = True)
cameraShapes = cmds.ls(type='camera')
cameraTransforms = cmds.listRelatives(cameraShapes, parent=1)
renderLayers = cmds.ls(type='renderLayer')

cameraStr = '#cameras:%s' % (','.join(cameraTransforms))
rndrLayerStr = 'render layers:%s' % (','.join(renderLayers))

sys.stdout.write('%s|%s' % (cameraStr, rndrLayerStr))