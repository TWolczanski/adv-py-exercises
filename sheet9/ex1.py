from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine
import sqlite3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QAction, QMenu, QMenuBar, QStatusBar, QFormLayout, QLineEdit, QPushButton, QFrame, QErrorMessage

Base = declarative_base()

class Book(Base):
    __tablename__ = "Books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    year = Column(String)
    person = Column(Integer, ForeignKey("People.id"))

class Person(Base):
    __tablename__ = "People"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    # a one-to-many relationship:
    # one person can borrow multiple books
    books = relationship(Book)

# I assume that books and people are unique
def find_book(session, title):
    books = session.query(Book).filter(Book.title == title).all()
    if len(books) > 0:
        return books[0]
    else:
        return None

def find_book_by_id(session, id):
    books = session.query(Book).filter(Book.id == id).all()
    if len(books) > 0:
        return books[0]
    else:
        return None

def find_person(session, name):
    people = session.query(Person).filter(Person.name == name).all()
    if len(people) > 0:
        return people[0]
    else:
        return None

def find_person_by_id(session, id):
    people = session.query(Person).filter(Person.id == id).all()
    if len(people) > 0:
        return people[0]
    else:
        return None

def add_book(session, title, author, year):
    if find_book(session, title) is None:
        book = Book(title=title, author=author, year=year)
        session.add(book)
        session.commit()
    else:
        raise Exception("This book has already been added to the database")

def add_person(session, name, email):
    if find_person(session, name) is None:
        person = Person(name=name, email=email)
        session.add(person)
        session.commit()
    else:
        raise Exception("This person has already been added to the database")

def borrow_book(session, book_title, person_name):
    book = find_book(session, book_title)
    if book is None:
        raise Exception("There is no such book in the database")
    person = find_person(session, person_name)
    if person is None:
        raise Exception("There is no such person in the database")
    if book.person is not None:
        raise Exception("This book has already been borrowed")
    person.books.append(book)
    session.add(person)
    session.commit()

def return_book(session, book_title, person_name):
    book = find_book(session, book_title)
    if book is None:
        raise Exception("There is no such book in the database")
    person = find_person(session, person_name)
    if person is None:
        raise Exception("There is no such person in the database")
    if book.person != person.id:
        raise Exception("This book has not been borrowed by this person")
    person.books.remove(book)
    session.add(person)
    session.commit()

def update_book(session, id, title, author, year):
    book = find_book_by_id(session, id)
    book.title = title
    book.author = author
    book.year = year
    session.commit()

###########################################
# GUI
###########################################

# the main window consists of a menu, a table and a status bar
# I implemented adding, viewing and editing only for the Books table
# operations such as adding a new book or person, borrowing a book and returning a book are available from the Edit menu
# it is also possible to edit existing records by clicking on a cell and changing its content
class MainWindow(QMainWindow):
    def __init__(self, session):
        self.session = session
        super().__init__()
        
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        
        self.init_table_label()
        self.init_table()
        self.init_menu()
        self.init_statusbar()
        
        self.widget.setLayout(self.vbox)
        self.setCentralWidget(self.widget)
        
        self.resize(800, 600)
        self.setWindowTitle("Library")
    
    def init_table_label(self):
        self.table_name = QLabel()
        self.vbox.addWidget(self.table_name)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.table_name.setFont(font)
        self.table_name.setText("Books")
        
    # the full information about the highlighted record is displayed in the status bar
    def init_statusbar(self):
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        
        self.statusbar_id = QLabel("Id: ")
        self.statusbar_title = QLabel("Title: ")
        self.statusbar_author = QLabel("Author: ")
        self.statusbar_year = QLabel("Year: ")
        self.statusbar_borrower = QLabel("Borrower: ")
        
        self.separator1 = QFrame()
        self.separator1.setFrameShape(self.separator1.VLine)
        self.separator2 = QFrame()
        self.separator2.setFrameShape(self.separator2.VLine)
        self.separator3 = QFrame()
        self.separator3.setFrameShape(self.separator3.VLine)
        self.separator4 = QFrame()
        self.separator4.setFrameShape(self.separator4.VLine)
        
        # add labels and vertical lines to the status bar
        self.statusbar.addPermanentWidget(self.statusbar_id)
        self.statusbar.addPermanentWidget(self.separator1)
        self.statusbar.addPermanentWidget(self.statusbar_title)
        self.statusbar.addPermanentWidget(self.separator2)
        self.statusbar.addPermanentWidget(self.statusbar_author)
        self.statusbar.addPermanentWidget(self.separator3)
        self.statusbar.addPermanentWidget(self.statusbar_year)
        self.statusbar.addPermanentWidget(self.separator4)
        self.statusbar.addPermanentWidget(self.statusbar_borrower)
    
    def init_table(self):
        self.books_table = QTableWidget()
        self.vbox.addWidget(self.books_table)
        # make the table editable
        self.books_table.setEnabled(True)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.books_table.sizePolicy().hasHeightForWidth())
        self.books_table.setSizePolicy(sizePolicy)
        self.books_table.setColumnCount(3)
        self.books_table.setRowCount(0)
        
        item = QTableWidgetItem()
        self.books_table.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.books_table.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.books_table.setHorizontalHeaderItem(2, item)
        
        item = self.books_table.horizontalHeaderItem(0)
        item.setText("Title")
        item = self.books_table.horizontalHeaderItem(1)
        item.setText("Author")
        item = self.books_table.horizontalHeaderItem(2)
        item.setText("Year")
        
        # make the columns resize dynamically
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        
        # when a cell is clicked, the full information about its row is displayed in the status bar
        self.books_table.cellClicked.connect(self.log_record)
        # when a cell is edited, an appropriate record is changed in the database
        self.books_table.cellChanged.connect(self.edit_record)
        self.load_data()
        
    # load data from the sqlite database
    def load_data(self):
        con = sqlite3.connect("library.db")
        cur = con.cursor()
        i = 0
        # temporarily disable listening to changes made to the table
        self.books_table.cellChanged.disconnect()
        self.books_table.setRowCount(0)
        # auxiliary list storing rows of the books_table widget
        self.books_table_rows = []
        for row in cur.execute("SELECT * FROM Books"):
            self.books_table.insertRow(i)
            self.books_table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.books_table.setItem(i, 1, QTableWidgetItem(row[2]))
            self.books_table.setItem(i, 2, QTableWidgetItem(row[3]))
            self.books_table_rows.append(list(row))
            i += 1
        self.books_table.cellChanged.connect(self.edit_record)
    
    def log_record(self, row, col):
        book = find_book(self.session, self.books_table.item(row, 0).text())
        borrower = find_person_by_id(self.session, book.person)
        if borrower is None:
            borrower = ""
        else:
            borrower = borrower.name
        self.statusbar_id.setText(f"Id: {book.id}")
        self.statusbar_title.setText(f"Title: {book.title}")
        self.statusbar_author.setText(f"Author: {book.author}")
        self.statusbar_year.setText(f"Year: {book.year}")
        self.statusbar_borrower.setText(f"Borrower: {borrower}")
    
    def edit_record(self, row, col):
        # if the user is trying to change the title of a book and the entered title is already in the database, an error message is shown
        if col == 0 and find_book(self.session, self.books_table.item(row, 0).text()) is not None:
            self.error_msg = QErrorMessage()
            self.error_msg.showMessage("This book has already been added to the database")
            self.books_table.item(row, 0).setText(self.books_table_rows[row][1])
        else:
            self.books_table_rows[row][col + 1] = self.books_table.item(row, col).text()
            update_book(self.session, self.books_table_rows[row][0], self.books_table_rows[row][1], self.books_table_rows[row][2], self.books_table_rows[row][3])
        
    def init_menu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.setMenuBar(self.menubar)
        
        self.menu_edit = QMenu(self.menubar)
        self.menu_edit.setTitle("Edit")
        
        self.action_add_book = QAction(self)
        self.action_add_book.setText("Add book")
        self.action_add_person = QAction(self)
        self.action_add_person.setText("Add person")
        self.action_borrow = QAction(self)
        self.action_borrow.setText("Borrow")
        self.action_return = QAction(self)
        self.action_return.setText("Return")
        
        self.menu_edit.addAction(self.action_add_book)
        self.menu_edit.addAction(self.action_add_person)
        self.menu_edit.addAction(self.action_borrow)
        self.menu_edit.addAction(self.action_return)
        
        self.menubar.addAction(self.menu_edit.menuAction())
        
        # an appropriate window pops up whenever an action is chosen from the Edit menu
        self.add_book_window = AddBookWindow(self.session, self)
        self.action_add_book.triggered.connect(lambda: self.add_book_window.show())
        self.add_person_window = AddPersonWindow(self.session, self)
        self.action_add_person.triggered.connect(lambda: self.add_person_window.show())
        self.borrow_window = BorrowWindow(self.session, self)
        self.action_borrow.triggered.connect(lambda: self.borrow_window.show())
        self.return_window = ReturnWindow(self.session, self)
        self.action_return.triggered.connect(lambda: self.return_window.show())

class AddBookWindow(QDialog):
    def __init__(self, session, main_window):
        self.session = session
        self.main_window = main_window
        super().__init__()
        self.setWindowTitle("Add book")
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        self.title = QLineEdit(self)
        self.author = QLineEdit(self)
        self.year = QLineEdit(self)
        add_button = QPushButton("Add", clicked=lambda: self.button_clicked())
        form_layout.addRow("Title", self.title)
        form_layout.addRow("Author", self.author)
        form_layout.addRow("Year", self.year)
        form_layout.addRow(add_button)
        
    def button_clicked(self):
        try:
            add_book(session, self.title.text(), self.author.text(), self.year.text())
            # whenever a new book is added, the table in the main window is rebuilt
            self.main_window.load_data()
            self.title.setText("")
            self.author.setText("")
            self.year.setText("")
        except Exception as e:
            # show an error message if the book could not be added to the database
            self.error_msg = QErrorMessage()
            self.error_msg.showMessage(str(e))

class AddPersonWindow(QDialog):
    def __init__(self, session, main_window):
        self.session = session
        self.main_window = main_window
        super().__init__()
        self.setWindowTitle("Add person")
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        self.name = QLineEdit(self)
        self.email = QLineEdit(self)
        add_button = QPushButton("Add", clicked=lambda: self.button_clicked())
        form_layout.addRow("Name", self.name)
        form_layout.addRow("E-mail", self.email)
        form_layout.addRow(add_button)
        
    def button_clicked(self):
        try:
            add_person(session, self.name.text(), self.email.text())
            self.name.setText("")
            self.email.setText("")
        except Exception as e:
            self.error_msg = QErrorMessage()
            self.error_msg.showMessage(str(e))
            
class BorrowWindow(QDialog):
    def __init__(self, session, main_window):
        self.session = session
        self.main_window = main_window
        super().__init__()
        self.setWindowTitle("Borrow")
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        self.book = QLineEdit(self)
        self.person = QLineEdit(self)
        borrow_button = QPushButton("Borrow", clicked=lambda: self.button_clicked())
        form_layout.addRow("Book", self.book)
        form_layout.addRow("Person", self.person)
        form_layout.addRow(borrow_button)
        
    def button_clicked(self):
        try:
            borrow_book(session, self.book.text(), self.person.text())
            self.book.setText("")
            self.person.setText("")
        except Exception as e:
            self.error_msg = QErrorMessage()
            self.error_msg.showMessage(str(e))
            
class ReturnWindow(QDialog):
    def __init__(self, session, main_window):
        self.session = session
        self.main_window = main_window
        super().__init__()
        self.setWindowTitle("Return")
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        self.book = QLineEdit(self)
        self.person = QLineEdit(self)
        return_button = QPushButton("Return", clicked=lambda: self.button_clicked())
        form_layout.addRow("Book", self.book)
        form_layout.addRow("Person", self.person)
        form_layout.addRow(return_button)
        
    def button_clicked(self):
        try:
            return_book(session, self.book.text(), self.person.text())
            self.book.setText("")
            self.person.setText("")
        except Exception as e:
            self.error_msg = QErrorMessage()
            self.error_msg.showMessage(str(e))

engine = create_engine("sqlite:///library.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

app = QApplication(sys.argv)
win = MainWindow(session)
win.show()
sys.exit(app.exec_())