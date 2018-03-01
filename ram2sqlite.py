from itertools import count

from dbconvert.sqlite_ddl import SQL_DBD_Init
from dbconvert.rammodel import Domain


def ram2sqlite(schema, connect):
    # ==============================================================================
    #  Queries
    # ==============================================================================

    # ==== Schema ==================================================================

    insertSchema = """
    INSERT INTO dbd$schemas(name) VALUES (?);
    """

    # ==== Domains =================================================================

    insertDomains = """
    INSERT INTO dbd$domains VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    createDomainType = """
    CREATE TABLE dbd$DomainType(
    domain_name VARCHAR NOT NULL,
    datatype_name VARCHAR NOT NULL);
    """

    insertDomainType = """
    INSERT INTO dbd$DomainType VALUES(?, ?);
    """

    updateDomainsFromDomainType = """
    UPDATE dbd$domains
    SET data_type_id = (
    SELECT dbd$data_types.id
    FROM dbd$domains as dom
    JOIN dbd$DomainType
    ON dbd$domains.name = dbd$DomainType.domain_name
    JOIN dbd$data_types
    ON dbd$DomainType.datatype_name = dbd$data_types.type_id
    WHERE dom.name = name);
    """

    dropDomainType = """
    DROP TABLE dbd$DomainType;
    """

    # ==== Tables ==================================================================

    insertTables = """
    INSERT INTO dbd$tables VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    createSchemaTable = """
    CREATE TABLE dbd$SchemaTable(
    schema_name VARCHAR NOT NULL,
    table_name VARCHAR NOT NULL);
    """

    insertSchemaTable = """
    INSERT INTO dbd$SchemaTable VALUES(?, ?);
    """

    updateTablesFromSchemaTable = """
    UPDATE dbd$tables
    SET schema_id = (
    SELECT dbd$schemas.id
    FROM dbd$tables as tb
    JOIN dbd$SchemaTable ON tb.name = dbd$SchemaTable.table_name
    JOIN dbd$schemas ON dbd$schemas.name = dbd$SchemaTable.schema_name
    WHERE tb.name = dbd$tables.name);
    """

    dropSchemaTable = """
    DROP TABLE dbd$SchemaTable;
    """

    # ===== Fields =================================================================

    insertFields = """
    INSERT INTO dbd$fields VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    createTableField = """
    CREATE TABLE dbd$TableField(
    table_name VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    field_position INTEGER NOT NULL);
    """

    insertTableField = """
    INSERT INTO dbd$TableField VALUES(?, ?, ?);
    """

    updateFieldsFromTableField = """
    UPDATE dbd$fields
    SET table_id = (
    SELECT dbd$tables.id
    FROM dbd$fields as fd
    JOIN dbd$TableField ON fd.name = dbd$TableField.field_name
    JOIN dbd$tables ON dbd$tables.name = dbd$TableField.table_name
    WHERE fd.name = dbd$fields.name),
    position = (
    SELECT dbd$TableField.field_position
    FROM dbd$fields as fd
    JOIN dbd$TableField ON fd.name = dbd$TableField.field_name
    WHERE fd.name = dbd$fields.name)
    WHERE table_id = -1;
    """

    dropTableField = """
    DROP TABLE dbd$TableField;
    """

    createFieldDomain = """
    CREATE TABLE dbd$FieldDomain(
    field_name VARCHAR NOT NULL,
    domain_name VARCHAR NOT NULL);
    """

    insertFieldDomain = """
    INSERT INTO dbd$FieldDomain VALUES (?, ?);
    """

    updateFieldsFromFieldDomain = """
    UPDATE dbd$fields
    SET domain_id = (
    SELECT dbd$domains.id
    FROM dbd$fields as fd
    JOIN dbd$FieldDomain ON fd.name = dbd$FieldDomain.field_name
    JOIN dbd$domains ON dbd$domains.name = dbd$FieldDomain.domain_name)
    WHERE domain_id = -1;
    """

    dropFieldDomain = """
    DROP TABLE dbd$FieldDomain;
    """

    deleteDomainsFakeName = """
    UPDATE dbd$domains
    SET name = null
    WHERE name LIKE 'dbd$FAKE%'
    """

    # ==== Constraints =============================================================

    insertConstraint = """
    INSERT INTO dbd$constraints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    createTableConstraint = """
    CREATE TABLE dbd$TableConstraint(
    table_name VARCHAR NOT NULL,
    constraint_name VARCHAR NOT NULL);
    """

    insertTableConstraint = """
    INSERT INTO dbd$TableConstraint VALUES (?, ?);
    """

    updateConstraintsFromTableConstraint = """
    UPDATE dbd$constraints
    SET table_id = (
    SELECT dbd$tables.id
    FROM dbd$constraints as cs
    JOIN dbd$TableConstraint ON cs.name = dbd$TableConstraint.constraint_name
    JOIN dbd$tables ON dbd$tables.name = dbd$TableConstraint.table_name
    WHERE cs.name = dbd$constraints.name)
    WHERE table_id = -1;
    """

    dropTableConstraint = """
    DROP TABLE dbd$TableConstraint;
    """

    createConstraintDetailFieldTable = """
    CREATE TABLE dbd$ConstraintDetailField(
    constraint_name VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    detail_position INTEGER NOT NULL,
    table_name VARCHAR NOT NULL);
    """

    insertConstraintDetailField = """
    INSERT INTO dbd$ConstraintDetailField VALUES (?, ?, ?, ?);
    """

    insertConstraintDetailsFromConstraintDetailField = """
    INSERT INTO dbd$constraint_details (constraint_id, position, field_id)
    SELECT dbd$constraints.id, cdf.detail_position, dbd$fields.id
    FROM dbd$ConstraintDetailField AS cdf
    JOIN dbd$constraints ON dbd$constraints.name = cdf.constraint_name
    JOIN dbd$fields ON dbd$fields.name = cdf.field_name
    JOIN dbd$tables ON dbd$tables.name = cdf.table_name
    WHERE dbd$tables.id = dbd$fields.table_id
      AND dbd$tables.id = dbd$constraints.table_id;
    """

    dropConstraintDetailField = """
    DROP TABLE dbd$ConstraintDetailField;
    """

    createConstraintReference = """
    CREATE TABLE dbd$ConstraintReference (
    constraint_name VARCHAR,
    reference_table_name VARCHAR NOT NULL);
    """

    insertConstraintReference = """
    INSERT INTO dbd$ConstraintReference VALUES (?, ?);
    """

    updateConstraintFromConstraintReference = """
    UPDATE dbd$constraints
    SET reference = (
    SELECT dbd$tables.id
    FROM dbd$constraints as cs
    JOIN dbd$ConstraintReference
      ON cs.name = dbd$ConstraintReference.constraint_name
    JOIN dbd$tables
      ON dbd$tables.name = dbd$ConstraintReference.reference_table_name
    WHERE cs.name = dbd$constraints.name)
    WHERE reference = -1;
    """

    dropConstraintReference = """
    DROP TABLE dbd$ConstraintReference;
    """

    deleteConstraintsFakeName = """
    UPDATE dbd$constraints
    SET name = null
    WHERE name LIKE 'dbd$FAKE%'
    """

    # ==== Indices =================================================================

    insertindices = """
    INSERT INTO dbd$indices VALUES (?, ?, ?, ?, ?, ?);
    """

    createTableIndex = """
    CREATE TABLE dbd$TableIndex(
    table_name VARCHAR NOT NULL,
    index_name VARCHAR NOT NULL);
    """

    insertTableIndex = """
    INSERT INTO dbd$TableIndex VALUES (?, ?);
    """

    updateindicesFromTableIndex = """
    UPDATE dbd$indices
    SET table_id = (
    SELECT dbd$tables.id
    FROM dbd$indices as ind
    JOIN dbd$TableIndex
      ON ind.name = dbd$TableIndex.index_name
    JOIN dbd$tables
      ON dbd$tables.name = dbd$TableIndex.table_name
    WHERE ind.name = dbd$indices.name)
    WHERE table_id = -1;
    """

    dropTableIndex = """
    DROP TABLE dbd$TableIndex;
    """

    createIndexDetailFieldTable = """
    CREATE TABLE dbd$IndexDetailFieldTable(
    index_name VARCHAR NOT NULL,
    table_name VARCHAR NOT NULL,
    detail_position INT NOT NULL,
    field_name VARCHAR NOT NULL,
    detail_expression VARCHAR,
    detail_descend BOOL);
    """

    insertIndexDetailFieldTable = """
    INSERT INTO dbd$IndexDetailFieldTable VALUES (?, ?, ?, ?, ?, ?);
    """

    insertIndexDetailsFromIndexDetailFieldTable = """
    INSERT INTO dbd$index_details
    SELECT null 
          ,dbd$indices.id
          ,idft.detail_position
          ,dbd$fields.id
          ,idft.detail_expression
          ,idft.detail_descend
    FROM dbd$IndexDetailFieldTable as idft
    JOIN dbd$tables
      ON dbd$tables.name = idft.table_name
    JOIN dbd$fields
      ON dbd$fields.name = idft.field_name
    JOIN dbd$indices
      ON dbd$indices.name = idft.index_name
    WHERE dbd$tables.id = dbd$fields.table_id 
      AND dbd$tables.id = dbd$indices.table_id
    """

    dropIndexDetailFieldTable = """
    DROP TABLE dbd$IndexDetailFieldTable;
    """

    deleteIndicesFakeName = """
    UPDATE dbd$indices
    SET name = null
    WHERE name LIKE 'dbd$FAKE%'
    """

    cursor = connect.cursor()
    cursor.executescript(SQL_DBD_Init)
    # Schema
    cursor.execute(insertSchema, (schema.name,))
    # Domains
    nonameDomains = []
    for table in schema.tables:
        for field in filter(lambda field: isinstance(field.domain, Domain), table.fields):
            tmpDomain = field.domain
            domainName = "__".join(["dbd$FAKE", schema.name, table.name, field.name]) + "__" + str(id(field.domain))
            tmpDomain.name = domainName
            field.domain = domainName
            nonameDomains.append(tmpDomain)
    domains = schema.domains + nonameDomains

    cursor.executemany(insertDomains, map(domainMapper, domains))
    cursor.execute(createDomainType)
    cursor.executemany(insertDomainType, ((domain.name, domain.type) for domain in domains))
    cursor.execute(updateDomainsFromDomainType)
    cursor.execute(dropDomainType)
    cursor.execute(deleteDomainsFakeName)

    # Tables
    cursor.executemany(insertTables, map(tableMapper, schema.tables))
    cursor.execute(createSchemaTable)
    cursor.executemany(insertSchemaTable, ((schema.name, table.name) for table in schema.tables))
    cursor.execute(updateTablesFromSchemaTable)
    cursor.execute(dropSchemaTable)

    # Fields
    for table in schema.tables:
        cursor.executemany(insertFields, map(fieldMapper, table.fields))

        cursor.execute(createTableField)
        cursor.executemany(insertTableField, ((table.name, field.name, i) for i, field in enumerate(table.fields)))
        cursor.execute(updateFieldsFromTableField)
        cursor.execute(dropTableField)

        cursor.execute(createFieldDomain)
        cursor.executemany(insertFieldDomain, ((field.name, field.domain) for field in table.fields))
        cursor.execute(updateFieldsFromFieldDomain)
        cursor.execute(dropFieldDomain)

    # Constraints
    for table in schema.tables:

        for constraint in table.constraints:
            if constraint.name == None:
                constraint.name = "__".join(["dbd$FAKE", schema.name, table.name, constraint.kind, *constraint.items])

        cursor.executemany(insertConstraint, map(constraintMapper, table.constraints))
        # Constraints <--> Tables
        cursor.execute(createTableConstraint)
        cursor.executemany(insertTableConstraint, ((table.name, constraint.name) for constraint in table.constraints))
        cursor.execute(updateConstraintsFromTableConstraint)
        cursor.execute(dropTableConstraint)

        # Constraints <--> ConstraintDetailss
        cursor.execute(createConstraintDetailFieldTable)
        for constraint in table.constraints:
            dataForInsert = ((constraint.name, item, i, table.name) for i, item in enumerate(constraint.items))
            cursor.executemany(insertConstraintDetailField, dataForInsert)
            connect.commit()
        cursor.execute(insertConstraintDetailsFromConstraintDetailField)
        # connect.commit()
        # return True
        cursor.execute(dropConstraintDetailField)

        # Constraints <--> ReferencesTables
        cursor.execute(createConstraintReference)
        cursor.executemany(insertConstraintReference,
                           ((constraint.name, constraint.reference) for constraint in table.constraints if
                            constraint.reference is not None))
        cursor.execute(updateConstraintFromConstraintReference)
        cursor.execute(dropConstraintReference)

        cursor.execute(deleteConstraintsFakeName)

    constraint_id = count(1)

    for table in schema.tables:
        pos = 1
        for constraint in table.constraints:
            cursor.execute("""
                insert into dbd$constraint_details (
                constraint_id,
                position,
                field_id)
                values (?, ?, ?)""", (
                next(constraint_id),
                pos,
                cursor.execute("""
                    select id from dbd$fields
                    where dbd$fields.name = ?""", (constraint.items,)).fetchone()[0]))

    # Indices
    for table in schema.tables:
        for index in table.indexes:
            if index.name is None:
                # index.name = "__".join(["dbd$FAKE", schema.name, table.name, *[item.name for item in index.fields]])
                index.name = "__".join([schema.name, table.name, *[item for item in index.fields]])
        cursor.executemany(insertindices, map(indexMapper, table.indexes))
        cursor.execute(createTableIndex)
        cursor.executemany(insertTableIndex, ((table.name, index.name) for index in table.indexes))
        cursor.execute(updateindicesFromTableIndex)
        cursor.execute(dropTableIndex)

        cursor.execute(createIndexDetailFieldTable)
        for index in table.indexes:
            cursor.executemany(
                insertIndexDetailFieldTable,
                ((index.name, table.name, i, *indexItemMapper(item)) for i, item in enumerate(index.fields))
            )

        cursor.execute(insertIndexDetailsFromIndexDetailFieldTable)
        cursor.execute(dropIndexDetailFieldTable)

        cursor.execute(deleteIndicesFakeName)


def domainMapper(domain):
    return (
        None,  # id
        domain.name,
        domain.descr,
        -1,  # data_type_id
        domain.length,
        domain.char_length,
        domain.precision,
        domain.scale,
        domain.width,
        domain.align,
        domain.show_null,
        domain.show_lead_nulls,
        domain.thousands_separator,
        domain.summable,
        domain.case_sensitive,
        id(domain)  # uuid
    )


def tableMapper(table):
    return (
        None,  # id
        None,  # schema_id
        table.name,
        table.descr,
        table.add,
        table.edit,
        table.delete,
        None,  # temporal_mode
        None,  # means
        id(table)  # uuid
    )


def fieldMapper(field):
    return (
        None,  # id
        -1,  # table_id
        -1,  # position
        field.name,
        field.rname,
        field.descr,
        -1,  # domain_id
        field.input,
        field.edit,
        field.show_in_grid,
        None,  # show_in_details
        field.is_mean,
        field.autocalculated,
        field.required,
        id(field)  # uuid
    )


def constraintMapper(constraint):
    return (
        None,  # id
        -1,  # table_id
        constraint.name,
        constraint.kind,
        -1,  # reference,
        -1,  # unique_id_key
        constraint.has_value_edit,
        constraint.cascading_delete,
        constraint.expression,
        id(constraint)  # uuid
    )


def indexMapper(index):
    return (
        None,  # id
        -1,  # table_id
        index.name,
        None,  # local
        "clustered" if index.is_clustered else "not_clustered",  # kind
        id(index)  # uuid
    )


def indexItemMapper(indexItem):
    return (
        indexItem,
        None,
        None
        # indexItem.expression,
        # indexItem.desc
    )

