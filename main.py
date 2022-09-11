from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QWidget, QInputDialog
from flashcards_db_operations import FlashcardsDB
from ui_main import Ui_MainWindow
from ui_addCards import Ui_AddCardsWindow
from ui_studyCards import Ui_StudyCardsWindow

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        global widgets
        widgets = self.ui

        self.addCardsWindow = None

        with FlashcardsDB() as db:
            db.create_table()
        
        self.loadTopicsInTable()
        widgets.btnAddCards.clicked.connect(self.openAddCardsWindow)
    
    # MainWindow Functions

    def loadTopicsInTable(self):
        with FlashcardsDB() as db:
            rowCount = (db.cursor.execute("SELECT COUNT(*) FROM topics").fetchone())[0]
            topics = db.cursor.execute("SELECT * FROM topics").fetchall()

        self.rowCount = rowCount+1
        widgets.tblWidgetTopics.clearContents()
        widgets.tblWidgetTopics.setRowCount(self.rowCount)
        
        tablerow = 0
        print(topics)
        for topic in topics:
            widgets.tblWidgetTopics.setRowHeight(tablerow, 60)
            widgets.tblWidgetTopics.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(f'{str(topic[2])}%'))
            widgets.tblWidgetTopics.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(topic[1]))
            self.loadWidgetCell(tablerow)
            tablerow+=1
            
        lastrow = self.rowCount-1
        widgets.tblWidgetTopics.setRowHeight(tablerow, 60)
        widgets.tblWidgetTopics.setItem(lastrow, 1, QtWidgets.QTableWidgetItem('Create New Deck!'))
        btnCell = QtWidgets.QPushButton(widgets.tblWidgetTopics)
        btnCell.setText('+')
        widgets.tblWidgetTopics.setCellWidget(lastrow, 0, btnCell)
        widgets.tblWidgetTopics.cellWidget(lastrow, 0).clicked.connect(self.addDeck)

        print("="*50)

    def loadWidgetCell(self, tablerow):
        btnStartStudy, btnAddCards = None, None
        hasRecordsInDB = self.hasRecordsInDB(tablerow)
        with FlashcardsDB() as db:
            if hasRecordsInDB:
                results = db.cursor.execute(f"SELECT * FROM flashcards WHERE (topic_id = {tablerow})")
                rows = [row for row in results]
                print(rows)
                
                btnStartStudy = QtWidgets.QPushButton(widgets.tblWidgetTopics)
                btnStartStudy.setObjectName(f'btnStudyRow{tablerow}')
                btnStartStudy.setText('Start Study')
                widgets.tblWidgetTopics.setCellWidget(tablerow, 2, btnStartStudy)
                btnStartStudy.clicked.connect(lambda: self.openStudyCardsWindow(tablerow))
            else:
                btnAddCards = QtWidgets.QPushButton(widgets.tblWidgetTopics)
                print('NOT EXISTS')
                btnAddCards.setText('Add Cards')
                btnAddCards.setObjectName(f'btnAddCards{tablerow}')
                widgets.tblWidgetTopics.setCellWidget(tablerow, 2, btnAddCards)
                btnAddCards.clicked.connect(self.openAddCardsWindow)

    def hasRecordsInDB(self, tablerow): 
        with FlashcardsDB() as db:
            qry = f"SELECT COUNT(*) FROM flashcards WHERE (topic_id = {tablerow})"
            recordCount = db.cursor.execute(qry).fetchall()[0][0]
            if recordCount > 0:
                return True
            return False

    @QtCore.Slot()
    def addDeck(self):
        new_topic, input_status = QInputDialog.getText(self, "New Topic", "Enter The Name of Topic:")
        if input_status:
            row = (self.rowCount, new_topic, 0)
        with FlashcardsDB() as db:
            qry_insert = "INSERT INTO topics (topic_id, topic_name, hits_percentage) VALUES (?,?,?);"
            db.populate(qry_insert, row)
            self.loadTopicsInTable()

    # AddCardsWindow Functions #####################################

    @QtCore.Slot()
    def openAddCardsWindow(self):
        self.addCardsWindow = QtWidgets.QMainWindow()
        self.ui_addCards = Ui_AddCardsWindow()
        self.ui_addCards.setupUi(self.addCardsWindow)

        global cardsWinWidgets
        cardsWinWidgets = self.ui_addCards
        
        cardsWinWidgets.listTopics.setCurrentRow(0)
        self.addCardsWindow.show()
        cardsWinWidgets.btnAddCard.clicked.connect(self.addCards)

        self.loadTopicsList()
    
    def loadTopicsList(self):
        with FlashcardsDB() as db:
            qry_select = "SELECT (topic_name) from topics"
            topics = db.cursor.execute(qry_select).fetchall()
        print(topics)
        for topic in topics:
            cardsWinWidgets.listTopics.addItem(topic[0])

    @QtCore.Slot()
    def addCards(self):
        card_question = cardsWinWidgets.pTextFront.toPlainText()
        card_answer = cardsWinWidgets.pTextVerse.toPlainText()
        if card_question and card_answer != "":
            topic_id = cardsWinWidgets.listTopics.currentRow()
            card_question = cardsWinWidgets.pTextFront.toPlainText()
            card_answer = cardsWinWidgets.pTextVerse.toPlainText()
            qry_insert = "INSERT INTO flashcards VALUES (?,?,?)"
            row = (card_question, card_answer, topic_id)
            with FlashcardsDB() as db:
                print('populating...')
                db.populate(qry_insert, row)
            self.addCardsClearContents()
            self.loadTopicsInTable()
        else:
            retry_msg = QtWidgets.QMessageBox(self.addCardsWindow)
            retry_msg.setText('Input something in your card (front and verse)!')
            retry_msg.show()

    def addCardsClearContents(self):
        cardsWinWidgets.pTextFront.clear()
        cardsWinWidgets.pTextVerse.clear()

    # StudyCards Functions #################################

    @QtCore.Slot()
    def openStudyCardsWindow(self, rowClicked):
        self.studyCardsWindow = QtWidgets.QMainWindow()
        self.ui_studyCards = Ui_StudyCardsWindow()
        self.ui_studyCards.setupUi(self.studyCardsWindow)

        global studyCardsWidgets
        studyCardsWidgets = self.ui_studyCards

        self.loadWindowInfo(rowClicked)

        self.studyCardsWindow.show()

    def loadWindowInfo(self, rowClicked):
        studyCardsWidgets.lblDeckName.setText(self.getTopicName(rowClicked))
        cardsRecords, cardsCount = self.getFlashcardsInfo(rowClicked)
        studyCardsWidgets.lblCardsQnt.setText(f"1/{str(cardsCount)}")

    def getTopicName(self, topic_id):
        with FlashcardsDB() as db:
            qry = f"SELECT (topic_name) FROM topics WHERE topic_id == {topic_id}"
            topic_name = db.cursor.execute(qry).fetchone()
        return topic_name[0]

    def getFlashcardsInfo(self, topic_id):
        with FlashcardsDB() as db:
            qry = f"SELECT * FROM flashcards WHERE topic_id == {topic_id}"
            cardsRecords = db.cursor.execute(qry).fetchall()

            qry = f"SELECT COUNT(*) FROM flashcards WHERE topic_id == {topic_id}"
            cardsCount = (db.cursor.execute(qry).fetchone())[0]

        return cardsRecords, cardsCount

    #######################

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())