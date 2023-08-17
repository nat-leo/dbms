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
            #print(self.match_token)
            self.start_symbol()

    def start_symbol(self):
        pass

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
    )
    p = Parser()
    p.parse("SELECT * FROM table")
