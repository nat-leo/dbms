import logging
import ply.lex as lex
import tokens

''' Given a set of instructions as a list, execute each
    operation from the first element to the last element.

    Elements all have one "operation" and one "child" operation:
    {
        "operation": ,
        "columns": [],
        "source": {
            "operation": "SCAN",
            "table": ,
        }
        "condition": {
            "column": ,
            "operator": ,
            "value": ,
        }
    }
'''
class LogicalQueryPlan:
    def __init__(self) -> None:
        self.plan = {}
        self.operation = None
        self.columns = []
        self.source = None
        self.c_col = None
        self.c_operator = None
        self.c_val = None
        self.condition = {
            "column": self.c_col,
            "operator": self.c_operator,
            "value": self.c_val
        }

    def set_operation(self, op: str):
        self.operation = op

    def set_columns(self, columns: list):
        self.columns = columns
    
    def add_column(self, column: str):
        self.columns.append(column)
    
    def set_source(self, table: str):
        self.source = table
    
    def set_condition(self, condition: dict):
        self.condition = condition

    def set_c_col(self, column):
        self.c_col = column
        self.condition["column"] = column
        
    def set_c_operator(self, op):
        self.c_operator = op
        self.condition["operator"] = op
    
    def set_c_val(self, val):
        self.c_val = val
        self.condition["value"] = val

    def to_json(self):
        return {"operation": self.operation,
                "columns": self.columns,
                "source": self.source,
                "condition": self.condition}
    


class Parser:
    def __init__(self) -> None:
        self.lexer = lex.lex(module=tokens) # steal PLY lex() and methods
        self.match_token = lex.LexToken()
        self.lqp = LogicalQueryPlan()

    def parse(self, string: str):
        self.lexer.input(string) # FROM PLY
        self.lqp = LogicalQueryPlan()
        while True:
            self.match_token = self.lexer.token() # Also from PLY
            if not self.match_token:
                break
            logging.info(f"Going through production rules for {self.match_token}")
            self.start_symbol()
            logging.info(f"LQP: {p.lqp.to_json()}")

    # LexToken() has the following attributes: type, value, lineno, lexpos
    def start_symbol(self):
        if self.match_token.type in ["SELECT"]:
            self.lqp.set_operation("SELECT") # ast
            self.select()
        elif self.match_token.type in ["INSERT"]:
            self.lqp.set_operation("INSERT") # ast
            self.insert()
        else:
            raise SyntaxError()

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

    # INSERT INTO table schema VALUES values_list
    def insert(self):
        self.match_token = self.lexer.token()
        if self.match_token.type not in ["INTO"]:
            raise SyntaxError(f"select: Error on line {self.match_token.lineno}. Expected [INTO]: got {self.match_token} instead.")
        logging.info(f"select: Matched {self.match_token} to [INTO].")
        self.match_token = self.lexer.token()
        self.table()
        self.schema()
        if self.match_token.type not in ["VALUES"]:
            raise SyntaxError(f"select: Error on line {self.match_token.lineno}. Expected [VALUES]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
        self.row_list()

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
        self.attribute_list()
        if self.match_token.type not in ["RPAR"]:
            raise SyntaxError(f"row: Error on line {self.match_token.lineno}. Expected [RPAR]: got {self.match_token} instead.")
        self.match_token = self.lexer.token()
    
    # value attribute_list_n
    def attribute_list(self):
        if self.match_token.type not in ["VALUE", "ID"]:
            raise SyntaxError(f"attribute_list: Error on line {self.match_token.lineno}. Expected [VALUE]: got {self.match_token} instead.")
        self.value()
        self.attribute_list_n()

    # COMMA value attribute_list_n | empty [RPAR]
    def attribute_list_n(self):
        if self.match_token.type in ["RPAR"]: # empty case RPAR
            return
        elif self.match_token.type in ["COMMA"]:
            self.match_token = self.lexer.token()
            self.value()
            self.attribute_list_n()
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
        if self.match_token.value in self.lqp.columns:
            self.lqp.condition["column"] = self.match_token.value
            self.match_token = self.lexer.token()
        else:
            raise NameError(f"conditon: Error on line {self.match_token.lineno}. {self.match_token} is not a column.")
        # operator
        self.operator()
        # value
        self.value()
    
    # OPERATOR
    def operator(self):
        if self.match_token.type not in ["OPERATOR"]:
            raise SyntaxError(f"operator: Error on line {self.match_token.lineno}. Expected [OPERATOR]: got {self.match_token} instead.")
        self.lqp.condition["operator"] = self.match_token.value
        self.match_token = self.lexer.token()

    # STRING | NUM
    def value(self):
        if self.match_token.type not in ["NUM", "STRING", "ID"]:
            raise SyntaxError(f"value: Error on line {self.match_token.lineno}. Expected [NUM, STRING]: got {self.match_token} instead.")
        self.lqp.condition["value"] = self.match_token.value
        self.match_token = self.lexer.token()

    # ID | ALL
    def column(self):
        self.lqp.add_column(self.match_token.value) # ast
        if self.match_token.type in ["ID"]:
            logging.info(f"column: Matched {self.match_token} to [ID].")
            self.match_token = self.lexer.token()
            return
        elif self.match_token.type in ["ALL"]:
            logging.info(f"column: Matched {self.match_token} to [ALL].")
            self.match_token = self.lexer.token()
            return
        else: 
            raise SyntaxError(f"column: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")

    # ID
    def table(self):
        self.lqp.set_source(self.match_token.value) # ast
        if self.match_token.type in ["ID"]:
            logging.info(f"table: Matched {self.match_token} to [ID].")
            self.match_token = self.lexer.token()
            return
        else: 
            raise SyntaxError(f"table: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    p = Parser()
    p.parse("SELECT column FROM table")
    p.parse("SELECT column1, column2, column3 FROM table WHERE column1 < 5")
    p.parse("SELECT * FROM table")
    p.parse("INSERT INTO table (column1, column2, column3) VALUES (value1, value2, value3)")
    
