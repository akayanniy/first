import sqlite3

from dbconvert import Parser
from ram2sqlite import ram2sqlite

app = Parser()
app.execute("tasks.xml")

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
