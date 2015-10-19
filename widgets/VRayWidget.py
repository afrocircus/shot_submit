__author__ = 'Natasha'

import os
import threading
import subprocess
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from utils import xmlUtils


class VRayWidget(QtGui.QWidget):

    def __init__(self, rsetdir):
        super(VRayWidget, self).__init__()
        self.setLayout(QtGui.QHBoxLayout())
        optionsBox = QtGui.QGroupBox('VRay Options')
        hLayout = QtGui.QHBoxLayout()
        optionsBox.setLayout(hLayout)
        optionsBox.setMaximumHeight(250)
        self.layout().addWidget(optionsBox)

        gLayout = QtGui.QGridLayout()
        hLayout.addLayout(gLayout)
        gLayout.addWidget(QtGui.QLabel('Scene File:'), 0, 0)
        self.sceneEdit = QtGui.QLineEdit()
        self.sceneEdit.setMinimumWidth(200)
        gLayout.addWidget(self.sceneEdit, 0, 1)
        self.sceneEdit.textChanged.connect(self.populateDependentFields)
        self.sceneBrowseButton = QtGui.QToolButton()
        self.sceneBrowseButton.setText('...')
        self.sceneBrowseButton.clicked.connect(lambda: self.browseFiles(self.sceneEdit))
        gLayout.addWidget(self.sceneBrowseButton, 0 , 2)

        gLayout.addWidget(QtGui.QLabel('Proj Dir:'), 1, 0)
        self.projEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.projEdit, 1, 1)
        self.projBrowseButton = QtGui.QToolButton()
        self.projBrowseButton.setText('...')
        self.projBrowseButton.clicked.connect(lambda: self.browseDirs(self.projEdit))
        gLayout.addWidget(self.projBrowseButton, 1 , 2)

        gLayout.addWidget(QtGui.QLabel('Export File:'), 2, 0)
        self.exportEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.exportEdit, 2, 1)
        self.exportBrowseButton = QtGui.QToolButton()
        self.exportBrowseButton.setText('...')
        self.exportBrowseButton.clicked.connect(lambda: self.browseSaveFile(self.exportEdit))
        gLayout.addWidget(self.exportBrowseButton, 2 , 2)

        gLayout.addWidget(QtGui.QLabel('Frames:'), 3, 0)
        self.frameEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.frameEdit, 3, 1)

        gLayout.addWidget(QtGui.QLabel('Output Dir:'), 4, 0)
        self.outDirEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.outDirEdit, 4, 1)
        self.outDirBrowseButton = QtGui.QToolButton()
        self.outDirBrowseButton.setText('...')
        self.outDirBrowseButton.clicked.connect(lambda: self.browseDirs(self.outDirEdit, outdir=True))
        gLayout.addWidget(self.outDirBrowseButton, 4 , 2)

        gLayout.addWidget(QtGui.QLabel('Output File:'), 5, 0)
        self.outFileEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.outFileEdit, 5, 1)

        self.compressedCheck = QtGui.QCheckBox('Compressed')
        gLayout.addWidget(self.compressedCheck, 6, 0)
        self.seperateCheck = QtGui.QCheckBox('Seperate Files')
        gLayout.addWidget(self.seperateCheck, 6, 1)

        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(QtGui.QLabel('Camera'))
        self.cameraList = QtGui.QListWidget()
        self.cameraList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        vLayout.addWidget(self.cameraList)
        vLayout.addWidget(QtGui.QLabel('Render Layer'))
        self.rlList = QtGui.QListWidget()
        self.rlList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        vLayout.addWidget(self.rlList)
        vLayout.addItem(QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

        hLayout.addLayout(vLayout)
        exportSettings = os.path.join(rsetdir, 'v-ray_exporter.rset')
        if os.path.exists(exportSettings):
            self.populateWidget(exportSettings)

    def populateWidget(self, exportSettings):
        valuedict = xmlUtils.readXMLfile(exportSettings)
        #if valuedict.has_key('scene'):
        #    self.sceneEdit.setText(valuedict['scene'])
        if valuedict.has_key('filename'):
            filename = valuedict['filename'].replace('&lt;', '<')
            filename = filename.replace('&gt;','>')
            self.exportEdit.setText(filename)
        if valuedict.has_key('projdir'):
            self.projEdit.setText(valuedict['projdir'])
        if valuedict.has_key('outdir'):
            dirname = valuedict['outdir'].replace('&lt;', '<')
            dirname = dirname.replace('&gt;','>')
            self.outDirEdit.setText(dirname)
        if valuedict.has_key('frames'):
            self.frameEdit.setText(valuedict['frames'])
        if valuedict.has_key('outfile'):
            self.outFileEdit.setText(valuedict['outfile'])
        if valuedict.has_key('compressed'):
            self.compressedCheck.setCheckState(QtCore.Qt.CheckState.Checked)
        if valuedict.has_key('separate'):
            self.seperateCheck.setCheckState(QtCore.Qt.CheckState.Checked)

    def browseFiles(self, lineEdit):
        dialog = QtGui.QFileDialog()
        filename, fileType = dialog.getOpenFileName(self, "Select File",
                                                    os.path.dirname(self.sceneEdit.text()),
                                                    options= QtGui.QFileDialog.DontUseNativeDialog)
        lineEdit.setText(str(filename))

    def browseSaveFile(self, lineEdit):
        dialog = QtGui.QFileDialog()
        filename, fileType = dialog.getSaveFileName(self, "Select File",
                                                    os.path.dirname(self.sceneEdit.text()),
                                                    options= QtGui.QFileDialog.DontUseNativeDialog)
        base, ext = os.path.splitext(str(filename))
        if not ext:
            ext = '.vrscene'
        filename = base + '_<Camera>_<Layer>' + ext
        lineEdit.setText(str(filename))

    def browseDirs(self, lineEdit, outdir=False):
        dialog = QtGui.QFileDialog()
        dirname = dialog.getExistingDirectory(self, "Select Directory",
                                              os.path.dirname(self.sceneEdit.text()),
                                              options= QtGui.QFileDialog.DontUseNativeDialog)
        if outdir:
            dirname = dirname + '/<Camera>/<Layer>'
        lineEdit.setText(str(dirname))

    def populateDependentFields(self):
        scene = str(self.sceneEdit.text())
        parentDir = os.path.dirname(scene)
        self.projEdit.setText(parentDir)
        if not scene == '':
            threading.Thread( None, self.getSceneData, args=[scene]).start()
            self.cameraList.clear()
            self.cameraList.addItem('Loading ...')
            self.rlList.clear()
            self.rlList.addItem('Loading ...')

    def getSceneData(self, sceneFile):
        mayapyLocation = 'C:\\Program Files\\Autodesk\\Maya2016\\bin\\mayapy.exe'
        mayaCameraScript = 'P:\\dev\\shot_submit\\maya_scripts\\getSceneData.py'
        cmd = '"%s" %s %s' % (mayapyLocation, mayaCameraScript, sceneFile)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        outputStr = process.stdout.read()
        self.populateCameraAndRl(outputStr)

    def populateCameraAndRl(self, outputStr):
        output = outputStr.split('#')[-1]
        cameraList = []
        renderList = []
        for outstr in output.split(';'):
            if 'cameras' in outstr:
                cameraList = outstr.split('|')[-1].split(',')
            else:
                renderList = outstr.split('|')[-1].split(',')
        self.cameraList.clear()
        self.rlList.clear()
        self.cameraList.addItems(cameraList)
        self.rlList.addItems(renderList)

    def createExportDict(self, renderer, outdir):
        exportDict = {}
        if '2016' in renderer:
            exportDict['Renderer'] = 'V-Ray for Maya 2016 Exporter/Default version'
        exValuesDict = {}
        exValuesDict['frames'] = str(self.frameEdit.text())
        exValuesDict['scene'] = str(self.sceneEdit.text())
        exValuesDict['outfile'] = str(self.outFileEdit.text())
        exValuesDict['projdir'] = str(self.projEdit.text())
        exValuesDict['camera'] = [str(item.text()) for item in self.cameraList.selectedItems()]
        exValuesDict['rl'] = [str(item.text()) for item in self.rlList.selectedItems()]
        exValuesDict['filename'] = str(self.exportEdit.text()).replace('<','&lt;')
        exValuesDict['filename'] = exValuesDict['filename'].replace('>','&gt;')
        exValuesDict['outdir'] = str(self.outDirEdit.text()).replace('<','&lt;')
        exValuesDict['outdir'] = exValuesDict['outdir'].replace('>','&gt;')
        exValuesDict['norender'] = 'true'
        if self.compressedCheck.checkState() == 2:
            exValuesDict['compressed'] = 'true'
        if self.seperateCheck.checkState() == 2:
            exValuesDict['separate'] = 'true'
        exportDict['Values'] = exValuesDict
        exportSettings = os.path.join(outdir, 'v-ray_exporter.rset')
        xmlUtils.createXMLfile(exportDict, exportSettings)
        return exportSettings, exportDict['Renderer'], exValuesDict['scene']

    def createRenderDict(self, renderer, rsetdir):
        renderDict = {}
        if '2016' in renderer:
            renderDict['Renderer'] = 'V-Ray Standalone 2016/Default version'
        rndrValuesDict = {}
        rndrValuesDict['frames'] = str(self.frameEdit.text())
        #rndrValuesDict['outfile'] = str(self.outFileEdit.text())
        camList = [str(item.text()) for item in self.cameraList.selectedItems()]
        rlList = [str(item.text()) for item in self.rlList.selectedItems()]
        scene = str(self.exportEdit.text())
        outdir = str(self.outDirEdit.text()) + '/'
        outfile = str(self.outFileEdit.text())
        rndrSettingsList = []
        for cam in camList:
            newscene = scene.replace('<Camera>', cam)
            newoutdir = outdir.replace('<Camera>', cam)
            newoutfile = outfile.replace('<Camera>', cam)
            for rl in rlList:
                if rl == 'defaultRenderLayer':
                    rl = 'masterLayer'
                rndrValuesDict['scene'] = newscene.replace('<Layer>', rl)
                rndrValuesDict['outdir'] = newoutdir.replace('<Layer>', rl)
                rndrValuesDict['outfile'] = newoutfile.replace('<Layer>', rl)
                renderDict['Values'] = rndrValuesDict
                rndrSettings = os.path.join(rsetdir, 'v-ray_renderer_%s_%s.rset' % (cam, rl))
                # Hack. Since outfile and outdir are not being read from the V-Ray renderer rset file.
                rndrSettingsFull = rndrSettings + ' -outdir "%s" -outfile "%s"' % (rndrValuesDict['outdir'], rndrValuesDict['outfile'])
                xmlUtils.createXMLfile(renderDict, rndrSettings)
                rndrSettingsList.append((rndrSettingsFull, rndrValuesDict['scene']))
        return rndrSettingsList, renderDict['Renderer']

    def validateInputFields(self):
        if self.sceneEdit.text()=='':
            return 'Please enter a scene file!'
        elif not self.cameraList.selectedItems():
            return 'Please select a camera'
        elif not self.rlList.selectedItems():
            return 'Please select a render layer'
        elif self.outDirEdit.text() == '' or self.outFileEdit.text()=='':
            return 'Please enter a valid output location'
        else:
            return 'Valid'
