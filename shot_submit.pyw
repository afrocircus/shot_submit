__author__ = 'Natasha'

import sys
import os
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from widgets import JobOptionsWidget
from widgets import VRayWidget
from utils import submissionUtils

class ShotSubmit(QtGui.QWidget):
    '''
    Main Application Class
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Loco VFX - Shot Submit')

        #set stylesheet
        from style import pyqt_style_rc
        f = QtCore.QFile('style/style.qss')
        f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        ts = QtCore.QTextStream(f)
        self.styleSheet = ts.readAll()
        self.setStyleSheet(self.styleSheet)
        self.setLayout(QtGui.QGridLayout())

        self.renderPalExec = '"C:\\Program Files (x86)\\RenderPal V2\\CmdRC\\RpRcCmd.exe"'
        self.rsetdir = os.path.join(os.environ['TEMP'], 'shot_submit')
        if not os.path.exists(self.rsetdir):
            os.makedirs(self.rsetdir)

        self.uiSetup()

    def uiSetup(self):
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel('Renderer: '))
        self.rendererDrop = QtGui.QComboBox()
        self.rendererDrop.setMinimumWidth(200)
        self.populateRenderDrop()
        self.displayRendererWidget(0)
        self.rendererDrop.activated[int].connect(self.displayRendererWidget)
        layout.addWidget(self.rendererDrop)
        layout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        layout.setContentsMargins(10, 0, 0, 0)
        self.layout().addLayout(layout, 0, 0)
        self.jobOpWidget = JobOptionsWidget.JobOptionsWidget()
        self.layout().addWidget(self.jobOpWidget, 2, 0)

        layout = QtGui.QHBoxLayout()
        self.submitButton = QtGui.QPushButton('Submit')
        self.submitButton.setMinimumWidth(100)
        self.submitButton.clicked.connect(self.submitRender)
        closeButton = QtGui.QPushButton('Close')
        closeButton.clicked.connect(self.close)
        closeButton.setMinimumWidth(100)
        layout.addWidget(self.submitButton)
        layout.addWidget(closeButton)
        layout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.layout().addLayout(layout, 3, 0)

    def populateRenderDrop(self):
        self.rendererDrop.addItem('VRay 2016 Export and Render')

    def displayRendererWidget(self, index):
        if index == 0:
            self.vrayWidget = VRayWidget.VRayWidget(self.rsetdir)
            self.layout().addWidget(self.vrayWidget, 1, 0)

    def submitRender(self):
        validate = self.vrayWidget.validateInputFields()
        if validate == 'Valid':
            if str(self.rendererDrop.currentText()) == 'VRay 2016 Export and Render':
                self.submitVRay(self.renderPalExec, self.rsetdir)
        else:
            QtGui.QMessageBox.warning(self, "Warning!", validate)

    def submitVRay(self, renderPalExec, outdir):
        jobidList = []
        exportSettings, exporter, scene = self.vrayWidget.createExportDict(str(self.rendererDrop.currentText()), outdir)
        netjobExporter = self.jobOpWidget.buildNetJob(exporter, exportSettings, scene, exporter=True)
        cmd = renderPalExec + netjobExporter
        output = submissionUtils.submitCmd(cmd)
        exjobid = submissionUtils.getJobID(output)
        jobidList.append(exjobid)

        rndrSettingsList, renderer = self.vrayWidget.createRenderDict(str(self.rendererDrop.currentText()), outdir)
        for rndrSettings, sceneFile in rndrSettingsList:
            netjobExporter = self.jobOpWidget.buildNetJob(renderer, rndrSettings, sceneFile, dependent=True, id=exjobid)
            cmd = renderPalExec + netjobExporter
            output = submissionUtils.submitCmd(cmd)
            jobid = submissionUtils.getJobID(output)
            jobidList.append(jobid)
        QtGui.QMessageBox.about(self, 'Shot_Submit', 'Shot submitted successfully! \nThe following job ids were created: %s' % ','.join(jobidList))


def main():
    app = QtGui.QApplication(sys.argv)
    gui = ShotSubmit()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()