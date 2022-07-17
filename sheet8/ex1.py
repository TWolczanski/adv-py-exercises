from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine
import argparse

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
def add_book(session, title, author, year):
    books = session.query(Book).filter(Book.title == title).all()
    if len(books) == 0:
        book = Book(title=title, author=author, year=year)
        session.add(book)
    else:
        print("This book has already been added to the database")

def add_person(session, name, email):
    people = session.query(Person).filter(Person.name == name).all()
    if len(people) == 0:
        person = Person(name=name, email=email)
        session.add(person)
    else:
        print("This person has already been added to the database")

def borrow_book(session, book_title, person_name):
    try:
        book = session.query(Book).filter(Book.title == book_title).all()[0]
        person = session.query(Person).filter(Person.name == person_name).all()[0]
        person.books.append(book)
        session.add(person)
    except:
        print("Invalid book title or person name")

def return_book(session, book_title, person_name):
    try:
        book = session.query(Book).filter(Book.title == book_title).all()[0]
        person = session.query(Person).filter(Person.name == person_name).all()[0]
        person.books.remove(book)
        session.add(person)
    except:
        print("Invalid book title or person name")

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

# python3 ex1.py add-book --title <title> --author <author> --year <year>
parser_add_book = subparsers.add_parser("add-book")
# python3 ex1.py add-person --name <name> --email <email>
parser_add_person = subparsers.add_parser("add-person")
# python3 ex1.py borrow --book <book_title> --person <person_name>
parser_borrow = subparsers.add_parser("borrow")
# python3 ex1.py return --book <book_title> --person <person_name>
parser_return = subparsers.add_parser("return")

# nargs="+" makes it possible to have whitespaces in the title, author name, etc.
# if the argument contains whitespaces, it will be split into a list which I have to join later on

parser_add_book.add_argument("--title", nargs="+", required=True)
parser_add_book.add_argument("--author", nargs="+", required=True)
parser_add_book.add_argument("--year", nargs=1, required=True, type=int)

parser_add_person.add_argument("--name", nargs="+", required=True)
parser_add_person.add_argument("--email", nargs="+", required=True)

parser_borrow.add_argument("--book", nargs="+", required=True)
parser_borrow.add_argument("--person", nargs="+", required=True)

parser_return.add_argument("--book", nargs="+", required=True)
parser_return.add_argument("--person", nargs="+", required=True)

engine = create_engine("sqlite:///library.db", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
parsed = parser.parse_args()

if parsed.command == "add-book":
    title = " ".join(parsed.title)
    author = " ".join(parsed.author)
    year = parsed.year[0]
    add_book(session, title, author, year)
elif parsed.command == "add-person":
    name = " ".join(parsed.name)
    email = " ".join(parsed.email)
    add_person(session, name, email)
elif parsed.command == "borrow":
    book = " ".join(parsed.book)
    person = " ".join(parsed.person)
    borrow_book(session, book, person)
elif parsed.command == "return":
    book = " ".join(parsed.book)
    person = " ".join(parsed.person)
    return_book(session, book, person)

session.commit()
session.close()