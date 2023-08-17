import ply.yacc as yacc
import ply.lex as lex
#import pytest

import grammar
import tokens

# select
select_commands = [
   "SELECT * FROM airbnb_listings",
   "SELECT city FROM airbnb_listings",
   "SELECT city, year_listed FROM airbnb_listings",
   "SELECT price FROM apts WHERE price <= 1500",
   "SELECT * FROM apts WHERE zipcode in [95060, 95062, 95066]",
   "SELECT city, year_listed FROM airbnb_listings ORDER BY number_of_rooms ASC",
]

# insert
insert_commands = [

]

# update 
update_commands = [
    
]

# delete
delete_commands = [
  
]

#@pytest.fixture
def p():
    parser = yacc.yacc(module=grammar)
    lexer = lex.lex(module=tokens)
    return parser

def test_select(p):
    for cmd in select_commands:
        result = p.parse(select_commands[0])
        assert result == None
    
for command_list in [select_commands, insert_commands, update_commands, delete_commands]:
    for command in command_list:
        # Build the parser
        parser = yacc.yacc(module=grammar)
        lexer = lex.lex(module=tokens)
        result = parser.parse(command)
        print(result)