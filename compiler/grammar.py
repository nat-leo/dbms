import ply.yacc as yacc
import logging
from tokens import tokens


def p_select(p):
    """select : SELECT select_expr FROM ID
              | SELECT DISTINCT select_expr FROM ID
              | SELECT select_expr FROM ID ORDER BY ID sort_order
    """
    logging.debug("Parsed SELECT statement")
    raise SyntaxError
    pass

def p_select_expr(p):
    """select_expr : wildcard_expr
                   | column_list
    """
    pass

def p_sort_order(p):
    """sort_order : ASC
                  | DESC
    """
    pass

def p_wildcard_expr(p):
    """wildcard_expr : ALL
    """
    pass

def p_column_list(p):
    """column_list : column
                  | column COMMA column_list
    """
    pass

def p_column(p):
    """ column : ID
    """
    pass

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    pass
    #raise Exception(f"at {p}")