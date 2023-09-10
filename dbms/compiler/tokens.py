reserved = {
    'NOT': 'NOT',
    'OR': 'OR',
    'EXISTS': 'EXISTS',
    'INTERSECTS': 'INTERSECTS',
    'SELECT': 'SELECT',
    'DISTINCT': 'DISTINCT',
    'FROM': 'FROM',
    'WHERE': 'WHERE',
    'GROUP': 'GROUP',
    'WINDOW': 'WINDOW',
    'QUALIFY': 'QUALIFY',
    'UNION': 'UNION',
    'EXCEPT': 'EXCEPT',
    'INTERSECT': 'INTERSECT',
    'ORDER': 'ORDER',
    'BY': 'BY',
    'OFFSET': 'OFFSET',
    'ROW': 'ROW',
    'ROWS': 'ROWS',
    'FETCH': 'FETCH',
    'FIRST': 'FIRST',
    'NEXT': 'NEXT',
    'PERCENT': 'PERCENT',
    'ONLY': 'ONLY',
    'WITH': 'WITH',
    'TIES': 'TIES',
    'FOR': 'FOR',
    'UPDATE': 'UPDATE',
    'NOWAIT': 'NOWAIT',
    'WAIT': 'WAIT',
    'SKIP': 'SKIP',
    'LOCKED': 'LOCKED',
    'INSERT': 'INSERT',
    'INTO': 'INTO',
    'DEFAULT': 'DEFAULT',
    'VALUES': 'VALUES',
    'DIRECT': 'DIRECT',
    'UPDATE': 'UPDATE',
    'AS': 'AS',
    'DELETE': 'DELETE',
    'FROM': 'FROM',
    'ASC': 'ASC',
    'DESC': 'DESC',
    'SET': 'SET',
    'CREATE': 'CREATE',
    'TABLE': 'TABLE',

    # types
    'varchar': 'varchar',
}

tokens = ["ID", "STRING", "OPERATOR", "ALL", "COMMA", "LPAR", "RPAR", "NUM",] + list(reserved.values())

t_NUM = r'\d+|[\d+|''].\d+'
t_ALL = r'\*'
t_COMMA = r','
t_OPERATOR = r'<|>|<=|>=|='
t_LPAR = r'\('
t_RPAR = r'\)'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, "ID")    # Check for reserved words
    return t

def t_STRING(t):
    r'[a-zA-Z]+'
    t.type = reserved.get(t.value, "ID")    # Check for reserved words
    return t

# ingore these characters and patterns:
t_ignore = r' \n'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)