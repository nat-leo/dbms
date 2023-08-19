import logging
import ply.lex as lex
import tokens

class Parser:
    def __init__(self) -> None:
        self.lexer = lex.lex(module=tokens) # steal PLY lex() and methods
        self.match_token = lex.LexToken()
        self.query_plan = {}

    def parse(self, string: str):
        self.lexer.input(string) # FROM PLY
        self.query_plan = {} # reset lqp
        while True:
            self.match_token = self.lexer.token() # Also from PLY
            if not self.match_token:
                break
            logging.info(f"Going through production rules for {self.match_token}")
            self.start_symbol()
            logging.info(f"LQP: {self.query_plan}")

    # LexToken() has the following attributes: type, value, lineno, lexpos
    def start_symbol(self):
        if self.match_token.type in ["SELECT"]:
            self.query_plan = {
                "operation": "SELECT",
                "columns": [],
                "table": None,
                "condition": {
                    "column": None,
                    "operator": None,
                    "value": None,
                },
            } # ast
            self.select()
        elif self.match_token.type in ["UPDATE"]:
            self.query_plan = {
                "operation": "UPDATE",
                "columns": ["*"],
                "table": None,
                "set": [
                    #{"column": None,
                    #"value": None}
                ],
                "condition": {
                    "column": None,
                    "operator": None,
                    "value": None,
                },
            } # ast
            self.update()
        elif self.match_token.type in ["INSERT"]:
            self.query_plan = {
                "operation": "INSERT",
                "columns": [],
                "table": None,
                "values": [],
            } # ast
            self.insert()

        elif self.match_token.type in ["DELETE"]:
            self.query_plan = {
                "operation": "DELETE",
                "columns": ["*"],
                "table": None,
                "condition": {
                    "column": None,
                    "operator": None,
                    "value": None,
                },
            } # ast
            self.delete()

    """SELECT column_list FROM table"""
    def select(self):
        self.match_token = self.lexer.token()
        # After SELECT, expect column_list 
        self.column_list()
        # After column_list, expect FROM
        if self.match_token.type in ["FROM"]:
            logging.info(f"select: Matched {self.match_token} to [FROM].")
        else:
            raise SyntaxError(f"select: Error on line {self.match_token.lineno}. Expected [FROM]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        # After FROM, expect table
        self.table()
        # After table, expect optional args
        self.optional_args()
    
    def update(self):
        self.match_token = self.lexer.token()
        # After UPDATE, expect table
        self.table()
        # After table, expect SET
        if self.match_token.type in ["SET"]:
            logging.info(f"update: Matched {self.match_token} to [FROM].")
        else:
            raise SyntaxError(f"update: Error on line {self.match_token.lineno}. Expected [FROM]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        self.set_list()
        self.optional_args()

    # INSERT INTO table schema VALUES values_list
    def insert(self):
        self.match_token = self.lexer.token()
        if self.match_token.type not in ["INTO"]:
            raise SyntaxError(f"insert: Error on line {self.match_token.lineno}. Expected [INTO]: got {self.match_token} instead.")
        logging.info(f"insert: Matched {self.match_token} to [INTO].")
        self.match_token = self.lexer.token()
        self.table()
        self.schema()
        if self.match_token.type not in ["VALUES"]:
            raise SyntaxError(f"insert: Error on line {self.match_token.lineno}. Expected [VALUES]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        self.row_list()

    def delete(self):
        self.match_token = self.lexer.token()
        if self.match_token.type not in ["FROM"]:
            raise SyntaxError(f"delete: Error on line {self.match_token.lineno}. Expected [INTO]: got {self.match_token} instead.")
        logging.info(f"delete: Matched {self.match_token} to [INTO].")
        self.match_token = self.lexer.token()
        # After FROM, expect table
        self.table()
        # After table, expect optional args
        self.optional_args()

    """ 
    set set_list_n
    """  
    def set_list(self):
        self.set()
        self.set_list_n()

    """
    COMMA set set_list_n
    | empty [WHERE, NONE]
    """
    def set_list_n(self):
        # empty rule
        if self.match_token is None or self.match_token.type in ["WHERE"]:
            return
        # there's another column, expect COMMA
        elif self.match_token.type in ["COMMA"]:
            logging.info(f"set_list_n: Matched {self.match_token} to [COMMA].")
            self.match_token = self.lexer.token()
            # After COMMA, expect set set_list_n
            self.set()
            self.set_list_n()
            return
        else: 
            raise SyntaxError(f"set_list_n: Error on line {self.match_token.lineno}. Expected [COMMA, WHERE, NONE]: got {self.match_token} instead.")

    def set(self):
        # parser logic
        if self.match_token.type not in ["ID"]:
            raise SyntaxError(f"set: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")
        logging.info(f"set: Matched {self.match_token} to [ID].")
        col = self.match_token.value
        # After ID, expect =
        self.match_token = self.lexer.token()
        # After =, expect val
        self.match_token = self.lexer.token()
        val = self.value()
        # build query plan
        self.query_plan["set"].append({"column": col, "value": val})

    # ( column_list )
    def schema(self):
        if self.match_token.type not in ["LPAR"]:
            raise SyntaxError(f"schema: Error on line {self.match_token.lineno}. Expected [LPAR]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        self.column_list()
        if self.match_token.type not in ["RPAR"]:
            raise SyntaxError(f"schema: Error on line {self.match_token.lineno}. Expected [RPAR]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()

    """ 
    column column_list_n
    """  
    def column_list(self):
        self.column()
        self.column_list_n()
        return 
        
    """
    COMMA column column_list_n
    | empty [FROM]
    """
    def column_list_n(self):
        # there's another column, expect COMMA
        if self.match_token.type in ["COMMA"]:
            logging.info(f"column_list_n: Matched {self.match_token} to [COMMA].")
            self.match_token = self.lexer.token()
            # After COMMA, expect column column_list_n
            self.column()
            self.column_list_n()
            return
        # empty rule
        elif self.match_token.type in ["FROM", "RPAR"]:
            return
        else: 
            raise SyntaxError(f"column_list_n: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")
    
    """ 
    row row_list_n
    """  
    def row_list(self):
        self.row()
        self.row_list_n()
        return 
        
    """
    COMMA row row_list_n
    | empty [None]
    """
    def row_list_n(self):
        # empty rule
        if self.match_token is None:
            return
        # there's another column, expect COMMA
        elif self.match_token.type in ["COMMA"]:
            logging.info(f"row_list_n: Matched {self.match_token} to [COMMA].")
            self.match_token = self.lexer.token()
            # After COMMA, expect row row_list_n
            self.row()
            self.row_list_n()
            return
        else: 
            raise SyntaxError(f"row_list_n: Error on line {self.match_token.lineno}. Expected [COMMA, None]: got {self.match_token} instead.")
    
    # ( attribute_list )
    def row(self):
        if self.match_token.type not in ["LPAR"]:
            raise SyntaxError(f"row: Error on line {self.match_token.lineno}. Expected [LPAR]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        self.query_plan["values"].append(self.attribute_list()) # row is only used for UPDATE, no need to check if SELECT, INSERT, UDPATE, or DELETE
        if self.match_token.type not in ["RPAR"]:
            raise SyntaxError(f"row: Error on line {self.match_token.lineno}. Expected [RPAR]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
    
    # value attribute_list_n
    def attribute_list(self):
        if self.match_token.type not in ["VALUE", "ID"]:
            raise SyntaxError(f"attribute_list: Error on line {self.match_token.lineno}. Expected [VALUE]: got {self.match_token} instead.")
        return [self.value()] + self.attribute_list_n()

    # COMMA value attribute_list_n | empty [RPAR]
    def attribute_list_n(self):
        if self.match_token.type in ["RPAR"]: # empty case RPAR
            return None
        elif self.match_token.type in ["COMMA"]:
            self.match_token = self.lexer.token()
            val = self.value()
            val_list = self.attribute_list_n()
            if val_list is not None:
                return [val] + val_list
            return [val]
        else:
            raise SyntaxError(f"attribute_list: Error on line {self.match_token.lineno}. Expected [COMMA, RPAR]: got {self.match_token} instead.")
    

    """ WHERE condition
        | empty [None]
    """
    def optional_args(self):
        # empty rule should terminate
        if self.match_token is None:
            return
        elif self.match_token.type in ["WHERE"]:
            logging.info(f"optiolnal_args: Matched {self.match_token} to [WHERE].")
            self.match_token = self.lexer.token()
            self.condition()
            return
        raise SyntaxError(f"optional_args: Error on line {self.match_token.lineno}. Expected [WHERE]: got {self.match_token} instead.")
    
    # column operator value
    def condition(self):
        # error checking
        if self.match_token.type not in ["ID"]:
            raise SyntaxError(f"condition: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")
        # column
        self.conditional_column()
        # operator
        self.operator()
        # value
        self.query_plan["condition"]["value"] = self.value()
    
    # OPERATOR
    def operator(self):
        if self.match_token.type not in ["OPERATOR"]:
            raise SyntaxError(f"operator: Error on line {self.match_token.lineno}. Expected [OPERATOR]: got {self.match_token} instead.")
        self.query_plan["condition"]["operator"] = self.match_token.value
        self.match_token = self.lexer.token()

    # STRING | NUM
    def value(self):
        val = self.match_token.value
        if self.match_token.type not in ["NUM", "STRING", "ID"]:
            raise SyntaxError(f"value: Error on line {self.match_token.lineno}. Expected [NUM, STRING]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        return val
    
    # ID | ALL
    # returns the column Lexeme matched.
    def column(self):
        # build query plan
        if self.query_plan["operation"] in ["SELECT", "DELETE"]:
            self.query_plan["columns"].append(self.match_token.value)
        # parser logic
        if self.match_token.type in ["ID"]:
            logging.info(f"column: Matched {self.match_token} to [ID].")
            self.match_token = self.lexer.token()
        elif self.match_token.type in ["ALL"]:
            logging.info(f"column: Matched {self.match_token} to [ALL].")
            self.match_token = self.lexer.token()
        else: 
            raise SyntaxError(f"column: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")
    
    # ID | ALL
    # returns the column Lexeme matched.
    def conditional_column(self):
        # build query plan
        # error check first
        if self.query_plan["columns"]!=["*"] and self.match_token.value not in self.query_plan["columns"]:
            raise NameError(f"conditonal_column: Error on line {self.match_token.lineno}. {self.match_token} is not a column.")
        if self.query_plan["operation"] in ["SELECT", "UPDATE", "DELETE"]:
            self.query_plan["condition"]["column"] = self.match_token.value
        # parser logic
        if self.match_token.type in ["ID"]:
            logging.info(f"conditional_column: Matched {self.match_token} to [ID].")
            self.match_token = self.lexer.token()
        elif self.match_token.type in ["ALL"]:
            logging.info(f"conditional_column: Matched {self.match_token} to [ALL].")
            self.match_token = self.lexer.token()
        else: 
            raise SyntaxError(f"conditional_column: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")

    # ID
    # returns table matched
    def table(self):
        self.query_plan["table"] = self.match_token.value # table is in every type of ast.
        if self.match_token.type in ["ID"]:
            logging.info(f"table: Matched {self.match_token} to [ID].")
            self.match_token = self.lexer.token()
        else: 
            raise SyntaxError(f"table: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    p = Parser()
    p.parse("SELECT column FROM table")
    p.parse("SELECT column1, column2, column3 FROM table WHERE column1 < 5")
    p.parse("SELECT * FROM table")
    p.parse("INSERT INTO table (column1, column2, column3) VALUES (value1, value2, value3), (value1, value2, value3)")
    p.parse("DELETE FROM table")
    p.parse("DELETE FROM table WHERE column3 = tibby")
    p.parse("UPDATE table SET column1 = 5 WHERE column3 = tibby")
    p.parse("UPDATE table SET column1 = tibs")

