__author__ = 'Natasha'

import PySide.QtGui as QtGui


class JobOptionsWidget(QtGui.QWidget):

    def __init__(self):

        super(JobOptionsWidget, self).__init__()
        self.setLayout(QtGui.QHBoxLayout())
        optionsBox = QtGui.QGroupBox('Job Options')
        gLayout = QtGui.QGridLayout()
        optionsBox.setLayout(gLayout)
        self.layout().addWidget(optionsBox)

        gLayout.addWidget(QtGui.QLabel('Job Name: '), 0, 0)
        self.jobEdit = QtGui.QLineEdit('shot_submit:<Scene>')
        gLayout.addWidget(self.jobEdit,  0, 1)

        gLayout.addWidget(QtGui.QLabel('Priority: '), 1, 0)
        self.priorityBox = QtGui.QSpinBox()
        self.priorityBox.setMinimum(1)
        self.priorityBox.setMaximum(10)
        self.priorityBox.setValue(5)
        self.priorityBox.setMaximumWidth(50)
        gLayout.addWidget(self.priorityBox, 1, 1)
        self.urgentCheckBox = QtGui.QCheckBox('Urgent Job')
        gLayout.addWidget(self.urgentCheckBox, 1, 2)

        gLayout.addWidget(QtGui.QLabel('Split Mode:'), 2, 0)
        self.splitmodeDrop = QtGui.QComboBox()
        self.setSplitModeDrop()
        self.splitmodeDrop.activated[int].connect(self.splitModeSelected)
        gLayout.addWidget(self.splitmodeDrop, 2, 1)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addItem(QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        hlayout.addWidget(QtGui.QLabel('Count:'))
        gLayout.addLayout(hlayout, 2, 2)
        self.countBox = QtGui.QSpinBox()
        self.countBox.setValue(5)
        gLayout.addWidget(self.countBox, 2, 3)
        self.countLabel = QtGui.QLabel('frames/chunk')
        gLayout.addWidget(self.countLabel, 2, 4)

        gLayout.addWidget(QtGui.QLabel('Client Pool:'), 3, 0)
        self.poolDrop = QtGui.QComboBox()
        self.poolDrop.addItem('All')
        self.poolDrop.addItem('Default pool')
        self.poolDrop.addItem('natasha-test')
        gLayout.addWidget(self.poolDrop, 3, 1)

    def setSplitModeDrop(self):
        self.splitmodeDrop.addItem('No Splitting')
        self.splitmodeDrop.addItem('Split into X total pieces')
        self.splitmodeDrop.addItem('Split into X frames per chunk')
        self.splitmodeDrop.setCurrentIndex(2)

    def splitModeSelected(self, index):
        if index == 0:
            self.countLabel.setText('')
            self.countBox.setValue(0)
            self.countBox.setEnabled(False)
        elif index == 1:
            self.countBox.setEnabled(True)
            self.countBox.setValue(2)
            self.countLabel.setText('total pieces')
        else:
            self.countBox.setEnabled(True)
            self.countBox.setValue(5)
            self.countLabel.setText('frames/chunk')

    def buildNetJob(self, renderer, rset, scene, exporter=False, dependent=False, id=None):
        netJobStr = ''
        netJobStr += ' -nj_renderer "%s"' % renderer
        jobname = str(self.jobEdit.text()).replace('<Scene>',scene.split('/')[-1])
        netJobStr += ' -nj_name "%s"' % jobname
        netJobStr += ' -nj_priority ' + str(self.priorityBox.value())
        if self.urgentCheckBox.checkState()==2:
            netJobStr += ' -nj_urgent'
        if not self.poolDrop.currentIndex() == 0:
            netJobStr += ' -nj_pools ' + str(self.poolDrop.currentText())
        if not exporter:
            splitMode = self.splitmodeDrop.currentIndex()
            if splitMode == 1:
                netJobStr += ' -nj_splitmode ' + str(splitMode) + ',' + str(self.countBox.value())
            elif splitMode == 2:
                netJobStr += ' -nj_splitmode ' + str(splitMode) + ',' + str(self.countBox.value())
        if dependent:
            netJobStr += ' -nj_dependency ' + id
            netJobStr += ' -nj_deptype 0'
        netJobStr += ' -retnjid '
        netJobStr += ' -importset ' + rset
        netJobStr += ' ' + scene
        return netJobStr
