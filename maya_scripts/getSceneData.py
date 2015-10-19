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
renderLayers = []

for layer in cmds.ls(type='renderLayer'):
    if cmds.getAttr('%s.renderable' % layer):
        renderLayers.append(layer)

cmds.setAttr("vraySettings.misc_eachFrameInFile", 0)
cmds.setAttr("vraySettings.vrscene_render_on", 0)
cmds.setAttr("vraySettings.vrscene_on", 1)
cmds.file(save=True, open=False)

maya.standalone.uninitialize()

cameraStr = '#cameras|%s' % (','.join(cameraTransforms))
rndrLayerStr = 'render layers|%s' % (','.join(renderLayers))

sys.stdout.write('%s;%s' % (cameraStr, rndrLayerStr))