import json
import sqlite3

#https://codereview.stackexchange.com/questions/182700/python-class-to-manage-a-table-in-sqlite
#https://blog.rtwilson.com/a-python-sqlite3-context-manager-gotcha/

class FlashcardsDB:
    __DB_LOCATION = 'flashcards_db_operations.db'

    def __init__(self):
        self.conn = sqlite3.connect(FlashcardsDB.__DB_LOCATION)
        self.cursor = self.conn.cursor()

    #"""
    #Uselless? 
    # Context Manager Capabilities

    def __enter__(self):
        return self
    
    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
    #"""
    
    # DB Functions 

    def create_table(self):
        # Child Table
        self.cursor.execute("DROP TABLE IF EXISTS flashcards")
        qry_flashcards = """ CREATE TABLE flashcards (
            card_question VARCHAR(255) NOT NULL,
            card_answer VARCHAR(255) NOT NULL,
            topic_id INTEGUER NOT NULL,
            FOREIGN KEY (topic_id)
                REFERENCES topics (topic_id)
            );"""
        self.cursor.execute(qry_flashcards)
        print('table flashcards is ready!')

        # Parent Table
        self.cursor.execute("DROP TABLE IF EXISTS topics")
        qry_topics = """ CREATE TABLE topics (
            topic_id INTEGUER PRIMARY KEY,
            topic_name VARCHAR(255) NOT NULL,
            hits_percentage INTEGUER NOT NULL
        );"""
        self.cursor.execute(qry_topics)
        print('table topics is ready!')

        poptbl = """INSERT INTO topics (topic_id, topic_name, hits_percentage) VALUES (?,?,?);"""
        self.populate(poptbl, (0, "", 0))
        self.populate(poptbl, (1, "Math", 0))
        self.populate(poptbl, (2, "Geography", 0))
        self.populate(poptbl, (3, "Chemistry", 0))
        self.populate(poptbl, (4, "Physics", 0))
    
    def populate(self, qry, row):
        self.cursor.execute(qry, row)
        self.conn.commit()

    
        #self.topics = self.cursor.execute("SELECT * FROM topics").fetchall()
    