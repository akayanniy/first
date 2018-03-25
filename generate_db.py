
simple_types = dict(
    INTEGER = "int",
    BLOB = "bytea",
    BOOLEAN = "boolean",
    BUTE = "byte",
    LARGEINT = "bigint",
    SMALLINT = "smallint",
    WORD = "smallint",
    DATE = "date",
    TIME = "time",
    MEMO = "text",
    BYTE = "int"
)

precision_and_sscale_types = dict(
    FLOAT = "numeric"
)

length_types = dict(
    STRING = "varchar",
    CODE="varchar"
)
#преобразование из XML в словарь PG
def createType(domain):
    if domain.type in simple_types:
        return simple_types[domain.type]
    if domain.type in length_types:
        length = domain.length if domain.length is not None else domain.char_length
        return length_types[domain.type] + "(" + str(length) + ")"
    if domain.type in precision_and_sscale_types and domain.precision is not None:
        scale = ", " + domain.scale if domain.scale is not None else ""
        return precision_and_sscale_types[domain.type] + "(" + domain.precision + scale + ")"


def createDB(connection, schema):
    cursor = connection.cursor()
    cursor.execute('CREATE SCHEMA "{}"'.format(schema.name))
    for domain in schema.domains:
        cursor.execute('CREATE DOMAIN "{}"."{}" AS {}'.format(schema.name, domain.name, createType(domain)))

    connection.commit()
    for table in schema.tables:
        s = 'CREATE TABLE "{}"."{}"'.format(schema.name, table.name)
        declare_fields = []
        for field in table.fields:
            declare_fields.append('"{}" "{}"."{}"'.format(field.name, schema.name, field.domain))

        s += "( "+ ",".join(declare_fields)+");"
        cursor.execute(s)

        for constraint in filter(lambda c: c.kind == "PRIMARY", table.constraints):
            cursor.execute ('ALTER TABLE "{}"."{}" ADD {} PRIMARY KEY ("{}")'.format(
                schema.name,
                table.name,
                'CONSTRAINT "' + constraint.name + '"' if constraint.name is not None else "",
                constraint.items))

        for constraint in filter(lambda c: c.kind == "UNIQE", table.constraints):
            cursor.execute ('ALTER TABLE "{}"."{}" ADD {} UNIQE ("{}")'.format(
                schema.name,
                table.name,
                'CONSTRAINT "' + constraint.name + '"' if constraint.name is not None else "",
                constraint.items))

        for constraint in filter(lambda c: c.kind == "CHECK", table.constraints):
            cursor.execute ('ALTER TABLE "{}"."{}" ADD {} CHECK "{}"'.format(
                schema.name,
                table.name,
                'CONSTRAINT "' + constraint.name + '"' if constraint.name is not None else "",
                constraint.expression))

        for index in table.indexes:
            cursor.execute('CREATE INDEX ON "{}"."{}" ({})'.format(
                schema.name,
                table.name, ", ".join(map(lambda item: '"' + item + '"', index.fields))))
    connection.commit()

    for table in schema.tables:
        for constraint in filter(lambda c: c.kind == "FOREIGN", table.constraints):
            cursor.execute ('ALTER TABLE "{}"."{}" ADD {} FOREIGN KEY ("{}") REFERENCES "{}"."{}"'.format(
                schema.name,
                table.name,
                'CONSTRAINT "' + constraint.name + '"' if constraint.name is not None else "",
                constraint.items,
                schema.name,
                constraint.reference
                ))
    connection.commit()
    cursor.close()
