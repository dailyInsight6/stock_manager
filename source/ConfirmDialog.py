# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'Confirm.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class ConfirmDialog(object):
    def setupUi(self, ConfirmDialog):
        ConfirmDialog.setObjectName("confirmDialog")
        ConfirmDialog.resize(240, 87)
        ConfirmDialog.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfirmDialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 46, 164, 32))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(ConfirmDialog)
        self.label.setGeometry(QtCore.QRect(20, 6, 201, 41))
        self.label.setObjectName("label")

        self.retranslateUi(ConfirmDialog)
        QtCore.QMetaObject.connectSlotsByName(ConfirmDialog)

    def retranslateUi(self, confirmDialog):
        _translate = QtCore.QCoreApplication.translate
        confirmDialog.setWindowTitle(_translate("ConfirmDialog", "Confirm"))
        self.label.setText(_translate("confirmDialog", "Do you want to remove the row?"))
