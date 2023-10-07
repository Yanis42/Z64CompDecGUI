#!/usr/bin/env python3

from PyQt6 import QtWidgets
from PyQt6.uic import load_ui
from pathlib import Path
from sys import exit, argv
from os import path, name as osName
from subprocess import run, PIPE


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """Main initialisation function"""
        super(MainWindow, self).__init__()

        uiPath = path.dirname(path.abspath(__file__)) + "/MainWindow.ui"
        if not path.isfile(uiPath):
            # temp fix for executables
            uiPath = uiPath.replace("/..", "")
        load_ui.loadUi(uiPath, self)

        self.defaultDir = str(Path.home())
        self.initConnections()

    # connections callbacks

    def openFileIn(self):
        """Returns the splits file path"""
        try:
            fName = QtWidgets.QFileDialog.getOpenFileName(None, "Open ROM", self.defaultDir, "*.z64")[0]
            self.fileInLineEdit.setText(fName)
        except:
            pass

    def openFileOut(self):
        """Returns the splits file path"""
        try:
            fName = QtWidgets.QFileDialog.getSaveFileName(None, "Save ROM as...", self.defaultDir, "*.z64")[0]
            self.fileOutLineEdit.setText(fName)
        except:
            pass

    def openExecutable(self):
        """Returns the splits file path"""
        try:
            fName = QtWidgets.QFileDialog.getOpenFileName(None, "Open Z64Compress Executable", self.defaultDir)[0]
            self.openCompressExeLineEdit.setText(fName)
        except:
            pass

    def compressROM(self):
        fileIn: str = self.fileInLineEdit.text()
        fileOut: str = self.fileOutLineEdit.text()
        executable: str = self.openCompressExeLineEdit.text()
        codec: str = self.codecList.currentText()
        game: str = self.gameList.currentText()
        otherFlags = ""

        if game == "OoT (NTSC 1.0)":
            otherFlags = '--dma "0x7430,1526" --compress "10-14,27-END"'
        elif game == "OoT (Debug)":
            otherFlags = '--dma "0x12F70,1548" --compress "9-14,28-END"'
        elif game == "MM (US)":
            otherFlags = '--dma "0x1A500,1568" --compress "10-14,23,24,31-END" --skip "1127" --repack "15-20,22"'
        else:
            raise ValueError("ERROR: Game not supported!")

        compressArgs = f'--in "{fileIn}" --out "{fileOut}" --codec {codec} --cache cache ' + otherFlags + " --threads 4"
        run(f"{executable} {compressArgs}", shell=True)

    def decompressROM(self):
        pass

    def initConnections(self):
        """Initialises the callbacks"""
        self.openFileInBtn.clicked.connect(self.openFileIn)
        self.openFileOutBtn.clicked.connect(self.openFileOut)
        self.openCompressExeBtn.clicked.connect(self.openExecutable)
        self.fileSizeTargetList.addItems(["32MB", "16MB", "8MB"])
        self.codecList.addItems(["yaz", "DEFLATE", "lzo", "ucl", "aplib"])
        self.gameList.addItems(["OoT (NTSC 1.0)", "OoT (Debug)", "MM (US)"])
        self.compressBtn.clicked.connect(self.compressROM)


# start the app
if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()

    try:
        from qdarktheme import load_stylesheet

        app.setStyleSheet(load_stylesheet())
    except ModuleNotFoundError:
        pass

    mainWindow.show()
    exit(app.exec())
