import ply.yacc as yacc
import ply.lex as lex
import grammar
import tokens

# select
select_commands = [
   "SELECT * FROM airbnb_listings",
   "SELECT city FROM airbnb_listings",
   "SELECT city, year_listed FROM airbnb_listings",
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

for command_list in [select_commands, insert_commands, update_commands, delete_commands]:
    for command in command_list:
        # Build the parser
        parser = yacc.yacc(module=grammar)
        lexer = lex.lex(module=tokens)
        result = parser.parse(command)
        print(result)