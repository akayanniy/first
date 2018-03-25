import sqlite3
import sys

from dbconvert import Parser
from ram2sqlite import ram2sqlite
from generate_db import createDB
import psycopg2
connect = psycopg2.connect(database='metadata', user='postgres', host='localhost', password='1488')


app = Parser()
app.execute("tasks.xml")


createDB(connect, app.schema)
sys.exit(0)

with open("./result/result.xml", "w+", encoding="utf-8") as output_file:
    app.createXML().writexml(output_file, addindent="  ", newl="\n", encoding="utf-8")
    output_file.close()

with open("./result/result.xml", "r", encoding="utf-8") as result, open("tasks.xml", "r", encoding="utf-8") as origin:
    i = 0
    errors = []
    for r, o in zip(result, origin):
        i += 1
        if r != o:
            errors.append((i, r, o))
    result.close()
    origin.close()
    print(errors)

connection = sqlite3.connect("./result/tasks.db")
ram2sqlite(app.schema, connection)
connection.commit()
connection.close()
print(app.schema.tables[0].name)


