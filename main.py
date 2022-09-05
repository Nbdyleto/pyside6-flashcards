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

        global db
        db = FlashcardsDB()
        db.create_table()
        
        self.loadTopicsInTable()

        widgets.btnAddCards.clicked.connect(self.openAddCardsWindow)

    # ADD CARDS WINDOW FUNCTION

    def openAddCardsWindow(self):
        print('aff')
        self.addCardsWindow = None

        self.addCardsWindow = QtWidgets.QMainWindow()
        self.ui_addCards = Ui_AddCardsWindow()
        self.ui_addCards.setupUi(self.addCardsWindow)

        global cardsWinWidgets
        cardsWinWidgets = self.ui_addCards

        self.addCardsWindow.show()
        cardsWinWidgets.btnAddCard.clicked.connect(self.addCards)

        #cardsWinWidgets.listTopics.itemClicked.connect(self.expandTopicsList)

        self.loadTopicsList()
    
    def loadTopicsList(self):
        qry_select = "SELECT (topic_name) from topics WHERE topic_id != 0"
        topics = db.cursor.execute(qry_select).fetchall()
        print(topics)
        for topic in topics:
            cardsWinWidgets.listTopics.addItem(topic[0])

    @QtCore.Slot()
    def addCards(self):
        #topic = cardsWinWidgets.listWidget.SelectedClicked()
        topic_id = cardsWinWidgets.listTopics.currentRow()+1
        card_question = cardsWinWidgets.pTextFront.toPlainText()
        card_answer = cardsWinWidgets.pTextVerse.toPlainText()
        qry_insert = "INSERT INTO flashcards VALUES (?,?,?)"
        row = (card_question, card_answer, topic_id)
        db.populate(qry_insert, row)
        print(topic_id, card_question, card_answer)
        self.addCardsClearContents()

    def addCardsClearContents(self):
        cardsWinWidgets.pTextFront.clear()
        cardsWinWidgets.pTextVerse.clear()

    # OTHER FUNCTIONS

    def loadTopicsInTable(self):
        widgets.tblWidgetTopics.clearContents()
        self.row_count = (db.cursor.execute("SELECT COUNT(*) FROM topics").fetchone())[0]
        widgets.tblWidgetTopics.setRowCount(self.row_count)
        print(self.row_count)

        topics = db.cursor.execute("SELECT * FROM topics WHERE topic_id != 0")
        
        tablerow = 0
        for topic in topics:
            widgets.tblWidgetTopics.setRowHeight(tablerow, 60)
            widgets.tblWidgetTopics.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(f'{str(topic[2])}%'))
            widgets.tblWidgetTopics.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(topic[1]))
            btnCell = QtWidgets.QPushButton(widgets.tblWidgetTopics)
            btnCell.setText('Start Study')
            widgets.tblWidgetTopics.setCellWidget(tablerow, 2, btnCell)
            tablerow+=1
        
        lastrow = self.row_count-1
        widgets.tblWidgetTopics.setRowHeight(tablerow, 60)
        widgets.tblWidgetTopics.setItem(lastrow, 1, QtWidgets.QTableWidgetItem('Create New Deck!'))
        btnCell = QtWidgets.QPushButton(widgets.tblWidgetTopics)
        btnCell.setText('+')
        widgets.tblWidgetTopics.setCellWidget(lastrow, 0, btnCell)
        widgets.tblWidgetTopics.cellWidget(lastrow, 0).clicked.connect(self.addDeck)
    
    @QtCore.Slot()
    def addDeck(self):
        new_topic, input_status = QInputDialog.getText(self, "New Topic", "Enter The Name of Topic:")
        if input_status:
            qry_insert = """INSERT INTO topics (topic_id, topic_name, hits_percentage) VALUES (?,?,?);"""
            row = (self.row_count, new_topic, 0)
        db.populate(qry_insert, row)
        self.loadTopicsInTable()

    #######################

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())