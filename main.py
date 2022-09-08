from cgi import test
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QWidget, QInputDialog
from flashcards_db_operations import FlashcardsDB
from ui_main import Ui_MainWindow
from ui_addCards import Ui_AddCardsWindow

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

    # ADD CARDS WINDOW FUNCTION

    def openAddCardsWindow(self):
        self.addCardsWindow = None

        self.addCardsWindow = QtWidgets.QMainWindow()
        self.ui_addCards = Ui_AddCardsWindow()
        self.ui_addCards.setupUi(self.addCardsWindow)

        global cardsWinWidgets
        cardsWinWidgets = self.ui_addCards

        self.addCardsWindow.show()
        cardsWinWidgets.btnAddCard.clicked.connect(self.addCards)

        self.loadTopicsList()
    
    def loadTopicsList(self):
        with FlashcardsDB() as db:
            qry_select = "SELECT (topic_name) from topics WHERE topic_id != 0"
            topics = db.cursor.execute(qry_select).fetchall()
        print(topics)
        for topic in topics:
            cardsWinWidgets.listTopics.addItem(topic[0])

    @QtCore.Slot()
    def addCards(self):
        #topic = cardsWinWidgets.listWidget.SelectedClicked()
        topic_id = cardsWinWidgets.listTopics.currentRow()
        card_question = cardsWinWidgets.pTextFront.toPlainText()
        card_answer = cardsWinWidgets.pTextVerse.toPlainText()
        qry_insert = "INSERT INTO flashcards VALUES (?,?,?)"
        row = (card_question, card_answer, topic_id)
        print(topic_id)
        with FlashcardsDB() as db:
            print('populating...')
            db.populate(qry_insert, row)
        self.addCardsClearContents()
        self.loadTopicsInTable()

    def addCardsClearContents(self):
        cardsWinWidgets.pTextFront.clear()
        cardsWinWidgets.pTextVerse.clear()

    # OTHER FUNCTIONS

    def loadTopicsInTable(self):
        with FlashcardsDB() as db:
            rowCount = (db.cursor.execute("SELECT COUNT(*) FROM topics").fetchone())
            topics = db.cursor.execute("SELECT * FROM topics WHERE topic_id != 0").fetchall()

        self.rowCount = rowCount[0]
        widgets.tblWidgetTopics.clearContents()
        widgets.tblWidgetTopics.setRowCount(self.rowCount)
        
        tablerow = 0
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
    
    def loadWidgetCell(self, tablerow):
        btnCell = QtWidgets.QPushButton(widgets.tblWidgetTopics)
        with FlashcardsDB() as db:
            try:
                results = db.cursor.execute(f"SELECT * FROM flashcards WHERE (topic_id = {tablerow})")
                rows = [row for row in results]
                print(rows[0])
                btnCell.setText('Start')
            except Exception:
                print('NOT EXISTS')
                btnCell.setText('Add Cards')
                btnCell.clicked.connect(self.openAddCardsWindow)
        widgets.tblWidgetTopics.setCellWidget(tablerow, 2, btnCell)

    @QtCore.Slot()
    def addDeck(self):
        new_topic, input_status = QInputDialog.getText(self, "New Topic", "Enter The Name of Topic:")
        if input_status:
            qry_insert = """INSERT INTO topics (topic_id, topic_name, hits_percentage) VALUES (?,?,?);"""
            row = (self.rowCount, new_topic, 0)
        with FlashcardsDB() as db:
            db.populate(qry_insert, row)
            self.loadTopicsInTable()

    #######################

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())