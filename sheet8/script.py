from subprocess import run
import sqlite3

run("python3 ex1.py add-book --title Quo vadis --author Henryk Sienkiewicz --year 1900", shell=True)
run("python3 ex1.py add-book --title Lalka --author Bolesław Prus --year 1800", shell=True)
run("python3 ex1.py add-book --title Dziady cz. III --author Adam Mickiewicz --year 1700", shell=True)
run("python3 ex1.py add-person --name John Doe --email example@gmail.com", shell=True)
run("python3 ex1.py add-person --name Marshall Mathers --email mm@gmail.com", shell=True)
run("python3 ex1.py borrow --book Lalka --person Marshall Mathers", shell=True)
run("python3 ex1.py borrow --book Quo vadis --person John Doe", shell=True)
run("python3 ex1.py borrow --book Dziady cz. III --person John Doe", shell=True)
run("python3 ex1.py return --book Quo vadis --person John Doe", shell=True)
run("python3 ex1.py borrow --book Quo vadis --person Marshall Mathers", shell=True)
run("python3 ex1.py return --book Lalka --person Marshall Mathers", shell=True)
run("python3 ex1.py return --book Dziady cz. III --person John Doe", shell=True)

db = sqlite3.connect("library.db")
cur = db.cursor()

print()
for row in cur.execute("SELECT * FROM Books"):
    print(row)

print()
for row in cur.execute("SELECT * FROM People"):
    print(row)