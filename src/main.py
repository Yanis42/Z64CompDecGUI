#!/usr/bin/env python3

import shutil

from PyQt6 import QtWidgets
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import QProcess
from PyQt6.uic import load_ui
from sys import exit, argv
from os import path


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """Main initialisation function"""
        super(MainWindow, self).__init__()

        uiPath = path.dirname(path.abspath(__file__)) + "/../res/MainWindow.ui"
        if not path.isfile(uiPath):
            # temp fix for executables
            uiPath = uiPath.replace("/..", "")
        load_ui.loadUi(uiPath, self)

        self.defaultDir = "./"
        self.sizeTargets = ["32MB", "16MB", "8MB"]
        self.codecs = ["yaz", "DEFLATE", "lzo", "ucl", "aplib"]
        self.games = ["OoT (NTSC 1.0)", "OoT (Debug)", "MM (US)"]
        self.compressProc = QProcess(self)
        self.decompressProc = QProcess(self)
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
        game: str = self.gameList.currentText()
        args = [
            f"--in",
            f"{self.fileInLineEdit.text()}",
            "--out",
            f"{self.fileOutLineEdit.text()}",
            "--codec",
            f"{self.codecList.currentText()}",
            "--cache",
            "cache",
            "--threads",
            "4",
        ]

        if game == "OoT (NTSC 1.0)":
            args.extend(["--dma", "0x7430,1526", "--compress", "10-14,27-END"])
        elif game == "OoT (Debug)":
            args.extend(["--dma", "0x12F70,1548", "--compress", "9-14,28-END"])
        elif game == "MM (US)":
            args.extend(
                [
                    "--dma",
                    "0x1A500,1568",
                    "--compress",
                    "10-14,23,24,31-END",
                    "--skip",
                    "1127",
                    "--repack",
                    "15-20,22",
                ]
            )
        else:
            raise ValueError("ERROR: Game not supported!")

        self.compressProc.setProgram(self.openCompressExeLineEdit.text())
        self.compressProc.setArguments(args)
        self.compressProc.start()

    def removeCacheFolder(self):
        shutil.rmtree("./cache")

    def updateCompressConsoleOutput(self):
        stderrOutput = self.compressProc.readAllStandardError().data().decode("UTF-8")
        self.outputPlainTextEdit.appendPlainText(stderrOutput)
        self.outputPlainTextEdit.moveCursor(QTextCursor.MoveOperation.End)

        for line in stderrOutput.split("\n"):
            val = self.compressProgressBar.value()

            if "success!" in line:
                val = 100
            elif "updating '" in line or "injecting file" in line:
                frac = line.split(" ")[2][:-1]
                fracSplit = frac.split("/")
                divisor = int(fracSplit[1])
                if divisor > 0:
                    val = round((int(fracSplit[0]) / divisor) * 100)

            self.compressProgressBar.setValue(val)

    def updateDecompressConsoleOutput(self):
        stderrOutput = self.decompressProc.readAllStandardError().data().decode("UTF-8")
        stdoutOutput = self.decompressProc.readAllStandardOutput().data().decode("UTF-8")
        self.outputPlainTextEdit.appendPlainText(stderrOutput)
        self.outputPlainTextEdit.appendPlainText(stdoutOutput)
        self.outputPlainTextEdit.moveCursor(QTextCursor.MoveOperation.End)

    def decompressROM(self):
        args = [
            f"{self.fileInLineEdit.text()}",
            f"{self.fileOutLineEdit.text()}",
            "--codec",
            f"{self.codecList.currentText()}",
        ]

        if self.zzrtlCheckBox.isChecked():
            args.append("--dmaext")

        self.decompressProc.setProgram(self.openCompressExeLineEdit.text())
        self.decompressProc.setArguments(args)
        self.decompressProc.start()

    def initConnections(self):
        """Initialises the callbacks"""
        self.openFileInBtn.clicked.connect(self.openFileIn)
        self.openFileOutBtn.clicked.connect(self.openFileOut)
        self.openCompressExeBtn.clicked.connect(self.openExecutable)

        self.fileSizeTargetList.addItems(self.sizeTargets)
        self.codecList.addItems(self.codecs)
        self.gameList.addItems(self.games)
        self.compressBtn.clicked.connect(self.compressROM)
        self.delCacheBtn.clicked.connect(self.removeCacheFolder)
        self.compressProc.readyReadStandardError.connect(self.updateCompressConsoleOutput)

        self.codecs.remove("DEFLATE")
        self.decompressProc.readyReadStandardError.connect(self.updateDecompressConsoleOutput)
        self.decompressBtn.clicked.connect(self.decompressROM)
        self.codecList_2.addItems(self.codecs)


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
