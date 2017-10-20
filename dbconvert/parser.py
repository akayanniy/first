import xml.dom.minidom as md
try:
    from .rammodel import Domain, Table, Field, Index, Constraint, Schema
except ModuleNotFoundError:
    from rammodel import Domain, Table, Field, Index, Constraint, Schema



#==============================================================================
#   app
#==============================================================================
class Parser():
    """
    Aplication class

    Properties:
        schema : object Schema or None

    Methods:
        execute: XML -> RAM model
        createXML: RAM model -> XML
    """
    def __init__(self):
        self.schema = None

    def execute(self, xmlFile):
        """
        Create object Schema from xml.dom.minidom.Document
        XML -> RAM model

        Args:
            xml : string. Name of XML file.
        """
        xml = md.parse(xmlFile)
        schema = Schema()
        for attrName, attrValue in xml.documentElement.attributes.items():
            if attrName.lower() == "fulltext_engine":
                schema.fulltext_engine = attrValue
            elif attrName.lower() == "version":
                schema.version = attrValue
            elif attrName.lower() == "name":
                schema.name = attrValue
            elif attrName.lower() == "description":
                schema.descr = attrValue
            else:
                raise ValueError("Incorrect attribute name \"{}\"".format(attrName))
        schema.domains = self._parseDomains(xml)
        schema.tables = self._parseTables(xml)

        self.schema = schema


    def _parseDomains(self, xml):
        """
        Create list of objects Domain

        Args:
            xml : xml.dom.minidom.Document

        Return: list<Domain>

        """
        domainList = []
        for domain in xml.getElementsByTagName("domain"):
            tmp = Domain()
            for attrName, attrValue in domain.attributes.items():
                if attrName.lower() == "name":
                    tmp.name = attrValue
                elif attrName.lower() == "description":
                    tmp.descr = attrValue
                elif attrName.lower() == "type":
                    tmp.type = attrValue
                elif attrName.lower() == "align":
                    tmp.align = attrValue
                elif attrName.lower() == "width":
                    tmp.width = attrValue
                elif attrName.lower() == "precision":
                    tmp.precision = attrValue
                elif attrName.lower() == "props":
                    tmp.props = attrValue
                elif attrName.lower() == "char_length":
                    tmp.char_length = attrValue
                elif attrName.lower() == "length":
                    tmp.length = attrValue
                elif attrName.lower() == "scale":
                    tmp.scale = attrValue
                else:
                    raise ValueError("In tag \"{}\" incorrect attribute name \"{}\"".format(domain, attrName))

            domainList.append(tmp)

        return domainList

    def _parseTables(self, xml):
        """
        Create list of object Table

        Args:
            xml : xml.dom.minidom.Document

        Return: list<Table>

        """
        tableList = []
        for table in xml.getElementsByTagName("table"):
            tmp = Table()

            for attrName, attrValue in table.attributes.items():
                if attrName.lower() == "name":
                    tmp.name = attrValue
                elif attrName.lower() == "description":
                    tmp.descr = attrValue
                elif attrName.lower() == "props":
                    tmp.props = attrValue
                elif attrName.lower() == "ht_table_flags":
                    tmp.ht_table_flags = attrValue
                elif attrName.lower() == "access_level":
                    tmp.access_level = attrValue
                else:
                    raise ValueError("In tag {} incorrect attribute name \"{}\"".format(table.nodeName, attrName))

            tmp.fields = self._parseFields(table)
            tmp.indexes = self._parseIndexes(table)
            tmp.constraints = self._parseConstraints(table)

            tableList.append(tmp)

        return tableList

    def _parseFields(self, xml):
        """
        Create list of object Field

        Args:
            xml : DOM Element table

        Return: list<Field>

        """
        if xml.nodeName != "table":
            raise ValueError("Element is not table")

        fieldList = []
        for field in xml.getElementsByTagName("field"):
            tmp = Field()
            for attrName, attrValue in field.attributes.items():
                if attrName.lower() == "name":
                    tmp.name = attrValue
                elif attrName.lower() == "rname":
                    tmp.rname = attrValue
                elif attrName.lower() == "domain":
                    tmp.domain = attrValue
                elif attrName.lower() == "props":
                    tmp.props = attrValue
                elif attrName.lower() == "description":
                    tmp.descr = attrValue
                else:
                    raise ValueError("In tag \"{}\" incorrect attribute name \"{}\"".format(field.nodeName, attrName))

            fieldList.append(tmp)

        return fieldList


    def _parseConstraints(self, xml):
        """
        Create list of object Constraint

        Args:
            xml : DOM Element table

        Return: list<Constraint>

        """
        if xml.nodeName != "table":
            raise ValueError("Element is not table")

        constraintList = []
        for constraint in xml.getElementsByTagName("constraint"):
            tmp = Constraint()
            for attrName, attrValue in constraint.attributes.items():
                if attrName.lower() == "name":
                    tmp.name = attrValue
                elif attrName.lower() == "kind":
                    tmp.kind = attrValue
                elif attrName.lower() == "items":
                    tmp.items = attrValue
                elif attrName.lower() == "props":
                    tmp.props = attrValue
                elif attrName.lower() == "reference_type":
                    tmp.reference_type = attrValue
                elif attrName.lower() == "reference":
                    tmp.reference = attrValue
                else:
                    raise ValueError("In tag \"{}\" incorrect attribute name \"{}\"".format(constraint.nodeName, attrName))
            constraintList.append(tmp)
        return constraintList

    def _parseIndexes(self, xml):
        """
        Create list of object Index

        Args:
            xml : DOM Element table

        Return: list<Index>

        """
        if xml.nodeName != "table":
            raise ValueError("Element is not table")

        indexList = []
        for index in xml.getElementsByTagName("index"):
            tmp = Index()
            if index.hasChildNodes():
                for item in index.getElementsByTagName("item"):
                    pass
                    # ветка для случая, когда в индекс входит больше одного поля
                    # хз что тут делать
                    # в предложенных xml файлах такого не было
            else:
                tmp.fields.append(index.getAttribute("field"))
            for attrName, attrValue in index.attributes.items():
                if attrName.lower() == "field":
                    pass
                elif attrName.lower() == "props":
                    tmp.props = attrValue
                else:
                    raise ValueError("In tag \"{}\" incorrect attribute name \"{}\"".format(index.nodeName, attrName))
            indexList.append(tmp)
        return indexList

    def createXML(self) -> md.Document:
        """
        Create xml.dom.minidom.Document from app.schema
        RAM model -> XML

        Return:
            xml.dom.minidom.Document

        """
        if self.schema is None:
            raise ValueError("Schema is missing")

        xml = md.Document()

        node = xml.createElement("dbd_schema")
        if self.schema.fulltext_engine is not None:
            node.setAttribute("fulltext_engine", self.schema.fulltext_engine)
        if self.schema.version is not None:
            node.setAttribute("version", self.schema.version)
        if self.schema.name is not None:
            node.setAttribute("name", self.schema.name)
        if self.schema.descr is not None:
            node.setAttribute("description", self.schema.descr)
        node.appendChild(xml.createElement("custom"))
        domains = xml.createElement("domains")

        for domain in self._domainGenerator(xml):
            domains.appendChild(domain)
        node.appendChild(domains)

        tables = xml.createElement("tables")
        for table in self._tableGenerator(xml):
            tables.appendChild(table)
        node.appendChild(tables)

        xml.appendChild(node)
        return xml

    def _domainGenerator(self, xml):
        """
        Generator of DOM element domain

        Args:
            xml : xml.dom.minidom.Document

        Yield: DOM element domain
        """
        for domain in self.schema.domains:
            node = xml.createElement("domain")
            if domain.name is not None:
                node.setAttribute("name", domain.name)
            if domain.descr is not None:
                node.setAttribute("description", domain.descr)
            if domain.type is not None:
                node.setAttribute("type", domain.type)
            if domain.align is not None:
                node.setAttribute("align", domain.align)
            if domain.width is not None:
                node.setAttribute("width", domain.width)
            if domain.length is not None:
                node.setAttribute("length", domain.length)
            if domain.precision is not None:
                node.setAttribute("precision", domain.precision)
            if domain.props is not None:
                node.setAttribute("props", domain.props)
            if domain.char_length is not None:
                node.setAttribute("char_length", domain.char_length)
#            if domain.length is not None:
#                node.setAttribute("length", domain.length)
            if domain.scale is not None:
                node.setAttribute("scale", domain.scale)
            yield node

    def _tableGenerator(self, xml):
        """
        Generator of DOM element table

        Args:
            xml : xml.dom.minidom.Document

        Yield: DOM element table
        """
        for table in self.schema.tables:
            node = xml.createElement("table")
            if table.name is not None:
                node.setAttribute("name", table.name)
            if  table.descr is not None:
                node.setAttribute("description", table.descr)
            if table.props is not None:
                node.setAttribute("props", table.props)
            if table.ht_table_flags is not None:
                node.setAttribute("ht_table_flags", table.ht_table_flags)
            if table.access_level is not None:
                node.setAttribute("access_level", table.access_level)

            if table.fields != []:
                for field in self._fieldGenerator(xml, table):
                    node.appendChild(field)

            if table.constraints != []:
                for constrint in self._constraintGenerator(xml, table):
                    node.appendChild(constrint)

            if table.indexes != []:
                for index in self._indexGenerator(xml, table):
                    node.appendChild(index)

            yield node

    def _fieldGenerator(self, xml, table):
        """
        Generator of DOM element field

        Args:
            xml   : xml.dom.minidom.Document
            table : object Table

        Yield: DOM element field
        """
        for field in table.fields:
            node = xml.createElement("field")
            if field.name is not None:
                node.setAttribute("name", field.name)
            if field.rname is not None:
                node.setAttribute("rname", field.rname)
            if field.domain is not None:
                node.setAttribute("domain", field.domain)
            if field.descr is not None:
                node.setAttribute("description", field.descr)
            if field.props is not None:
                node.setAttribute("props", field.props)

            yield node

    def _constraintGenerator(self, xml, table):
        """
        Generator of DOM element constraint

        Args:
            xml   : xml.dom.minidom.Document
            table : object Table

        Yield: DOM element constraint
        """
        for constraint in table.constraints:
            node = xml.createElement("constraint")
            if constraint.name is not None:
                node.setAttribute("name", constraint.name)
            if constraint.kind is not None:
                node.setAttribute("kind", constraint.kind)
            if constraint.items is not None:
                node.setAttribute("items", constraint.items)
#            if constraint.props is not None:
#                node.setAttribute("props", constraint.props)
            if constraint.reference_type is not None:
                node.setAttribute("reference_type", constraint.reference_type)
            if constraint.reference is not None:
                node.setAttribute("reference", constraint.reference)
            if constraint.props is not None:
                node.setAttribute("props", constraint.props)
            yield node

    def _indexGenerator(self, xml, table):
        """
        Generator of DOM element index

        Args:
            xml   : xml.dom.minidom.Document
            table : object Table

        Yield: DOM element index
        """
        for index in table.indexes:
            if index.fields != []:
                node = xml.createElement("index")
                if len(index.fields) == 1:
                    node.setAttribute("field", index.fields[0])
                else:
                    # ветка для случая, когда в индекс входит больше одного поля
                    pass
                if index.name is not None:
                    node.setAttribute("name", index.name)
                if index.props is not None:
                    node.setAttribute("props", index.props)
                yield node
            else:
                raise ValueError("Error! Index does not contain fields")