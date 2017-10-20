from dbconvert import Parser
app = Parser()
app.execute("tasks.xml")

with open("result.xml", "w") as output_file:
    app.createXML().writexml(output_file, addindent="  ", newl="\n", encoding="utf-8")
    output_file.close()


#==============================================================================
#     Test
#==============================================================================
with open("result.xml", "r") as result, open("tasks.xml", "r", encoding="utf-8") as origin:
    i = 0
    errors = []
    for r, o in zip(result, origin):
        i += 1
        if r != o:
            errors.append((i, r, o))
    result.close()
    origin.close()
    print(errors)

# Ошибка в первой строке из-за того,
# что оригинальный файл начинается с \ufeff