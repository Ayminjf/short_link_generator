import sys
import json
import pyperclip
import requests
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from urllib.parse import urlencode

import csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ShortLinkGenerator import Ui_MainWindow_ShortLinkGenerator

class Ui_ShortLinkGenerator(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui_shortlinkgenerator = Ui_MainWindow_ShortLinkGenerator()
        self.ui_shortlinkgenerator.setupUi(self)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ui_shortlinkgenerator.help_btn.clicked.connect(self.help)
        self.show()
        self.pushbutton()

    def mousePressEvent(self, evt):
        self.oldpos = evt.globalPos()

    def mouseMoveEvent(self, evt) :
        delta = QPoint(evt.globalPos() - self.oldpos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldpos = evt.globalPos()

    def pushbutton(self):
        self.ui_shortlinkgenerator.Pastelongurl.clicked.connect(self.pasteurl)
        self.ui_shortlinkgenerator.generateshortlink.clicked.connect(self.generate_link)
        self.ui_shortlinkgenerator.copyshorturl.clicked.connect(self.copyhash)
        self.ui_shortlinkgenerator.loadlinks.clicked.connect(self.loadalllinks)
        self.ui_shortlinkgenerator.dellink.clicked.connect(self.deletelink)

    def help(self):

            message_box = QtWidgets.QMessageBox()

            message_box.setWindowTitle("Developer information")
            message_box.setWindowIcon(QtGui.QIcon('royal_lionn.ico'))
            message_box.setIcon(QMessageBox.Information)

            message_box.setText("Developer : Amin Jafari\n"
                                "---------------------------------\n"
                                "Gmail : Aminjjjeffrey@gmail.com\n")
            message_box.exec_()

    def pasteurl(self):
        self.ui_shortlinkgenerator.longurl.setPlainText(pyperclip.paste())

    def copyhash(self):
        if ((self.ui_shortlinkgenerator.shortlinktxt.text()) != ""):
            try:
                pyperclip.copy(self.ui_shortlinkgenerator.shortlinktxt.text())
                QMessageBox.information(self, "Copy Short-Link", "Short-Link Copied")
            except:
                pass
        else:
            QMessageBox.information(self, "Copy Short-Link", "Please wait until Short-Link is generated")


    def deletelink(self):
        LinkID = self.ui_shortlinkgenerator.deltxt.text()
        url = f"https://api.rebrandly.com/v1/links/{LinkID}"

        headers = {
            "Accept": "application/json",
            "apikey": "YOUR_API_KEY"
        }
        if (LinkID != ""):
            try:
                QMessageBox.information(self, "ID Deleting", "ID Deleted")
                requests.request("DELETE", url, headers=headers)
            except:
                pass
        else:
            QMessageBox.information(self, "ID Deleting", "Please Enter The Link ID")


    def loadalllinks(self):
        # CONFIGURATION
        exportFileName = "exported.csv"
        apiKey = "YOUR_API_KEY"
        workspace = None
        fieldnames = ['id', 'createdAt', 'shortUrl', 'destination']

        # CONSTRAINTS
        MAX_PAGE_SIZE = 10000

        def downloadLinksAfter(lastLink):
            last = lastLink["id"] if lastLink else ""
            requestHeaders = {
                "Content-type": "application/json",
                "apikey": apiKey,
                "workspace": workspace
            }
            querystring = urlencode({
                "limit": MAX_PAGE_SIZE,
                "last": lastLink["id"] if lastLink else "",
                "orderBy": "createdAt",
                "orderDir": "desc"
            })
            endpoint = f"https://api.rebrandly.com/v1/links?{querystring}"
            r = requests.get(endpoint, headers=requestHeaders)
            if (r.status_code != requests.codes.ok):
                raise Exception(f"Could not retrieve links, response code was {r.status_code}")
            links = r.json()
            return links

        def export():
            downloadedAll = False
            downloaded = None

            def lastOne():
                return downloaded[-1] if downloaded else None

            def initFile(exportCSV):
                outputFile = csv.DictWriter(exportCSV, fieldnames=fieldnames)
                outputFile.writeheader()

            def saveLinksToFile(links, exportCSV):
                outputFile = csv.DictWriter(exportCSV, fieldnames=fieldnames)

                def map(link):
                    output = {}
                    for field in fieldnames:
                        output[field] = link[field]
                    return output

                outputFile.writerows([map(link) for link in links])

            with open(exportFileName, "w", encoding='UTF8') as exportCSV:
                initFile(exportCSV)
                while (not downloadedAll):
                    downloaded = downloadLinksAfter(lastOne())
                    if not any(downloaded):
                        downloadedAll = True
                    else:
                        saveLinksToFile(downloaded, exportCSV)

        export()
        self.ui_shortlinkgenerator.plainTextEdit.setPlainText("")
        a = []
        file = open('exported.csv')
        csvreader = csv.reader(file)
        shortlink = None
        shortlinkid = None

        for i in csvreader:
            if i != [] and i != ['id', 'createdAt', 'shortUrl', 'destination']:
                shortlink = i[0]
                date = i[1]
                shortlinkid = i[2]
                a.append(f"🔗 {shortlinkid}")
                a.append(f"🆔 {shortlink}")
                a.append(f"📅 {date}")
                a.append("")

        for i in a:
            self.ui_shortlinkgenerator.plainTextEdit.appendPlainText(i)
        file.close()

    def generate_link(self):
        LongURL = self.ui_shortlinkgenerator.longurl.toPlainText()
        TitleURL = self.ui_shortlinkgenerator.titleurl.text()
        CustomURL = self.ui_shortlinkgenerator.customurl.text()

        if (LongURL != ""):
            try:


                if TitleURL or CustomURL != "":
                    self.linkRequest = {
                        "destination": f"{LongURL}"
                        , "domain": {"fullName": "rebrand.ly"}
                        , "slashtag": f"{CustomURL}"
                        , "title": f"{TitleURL}"
                    }
                elif TitleURL or CustomURL == "":
                    self.linkRequest = {
                        "destination": f"{LongURL}"
                        , "domain": {"fullName": "rebrand.ly"}
                    }
                requestHeaders = {
                    "Content-type": "application/json",
                    "apikey": "YOUR_API_KEY",
                    "workspace": ""
                }

                r = requests.post("https://api.rebrandly.com/v1/links",
                                  data=json.dumps(self.linkRequest),
                                  headers=requestHeaders)

                if (r.status_code == requests.codes.ok):
                    link = r.json()
                    self.ui_shortlinkgenerator.shortlinktxt.setText(link["shortUrl"])
                    QMessageBox.information(self, "Short-Link Generatore", "Short-Link Generated")
            except:
                pass
        else:
            QMessageBox.information(self, "Short-Link Generatore", "Please Enter The Long-Link ")

if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    root = Ui_ShortLinkGenerator()
    sys.exit(qApp.exec_())