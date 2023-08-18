import logging
import ply.lex as lex
import tokens

class Parser:
    def __init__(self) -> None:
        self.lexer = lex.lex(module=tokens) # steal PLY lex() and methods
        self.match_token = lex.LexToken()

    def parse(self, string: str):
        self.lexer.input(string) # FROM PLY
        while True:
            self.match_token = self.lexer.token() # Also from PLY
            if not self.match_token:
                break
            logging.info(f"Going through production rules for {self.match_token}")
            self.start_symbol()

    # LexToken() has the following attributes: type, value, lineno, lexpos
    def start_symbol(self):
        if self.match_token.type in ["SELECT"]:
            self.select()
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
        elif self.match_token.type in ["FROM"]:
            return
        else: 
            raise SyntaxError(f"column_list_n: Error on line {self.match_token.lineno}. Expected [ID]: got {self.match_token} instead.")
    
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
    
    def condition(self):
        return

    # ID | ALL
    def column(self):
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
    p.parse("SELECT column1, column2, column3 FROM table")
    p.parse("SELECT * FROM table")
