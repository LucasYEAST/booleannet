"""
Grammar file for a boolean parser based on PLY
"""
import random, time, sys
import tokenizer, util, state
from ply import yacc
from itertools import *

# a list of all valid modes
PLDE, SYNC, ASYNC, RANK, TIME = 'plde sync async rank time'.split()

# valid modes of operation
VALID_MODES = [ PLDE, SYNC, ASYNC, RANK, TIME ] 

# the labels will be set to 1 for these
NOLABEL_MODE = [ PLDE, SYNC, ASYNC] 

# will contain the last parsed line,  used to improve error reporting
LAST_LINE = ''

tokens = tokenizer.Lexer.tokens

precedence = (
    ('left',  'OR'),
    ('left',  'AND'),
    ('right', 'NOT'),
)

# YACC style grammar rules below

def p_stmt_init(p):
    'stmt : ID EQUAL stmt '    

    # this will only be executed during initialization
    p.parser.RULE_SETVALUE( p.parser.old, p[1], p[3], p)
    p.parser.RULE_SETVALUE( p.parser.new , p[1], p[3], p)       
    p[0] = p[3]

def p_stmt_assign(p):
    'stmt : ID ASSIGN EQUAL stmt '
    p.parser.RULE_SETVALUE( p.parser.new, p[1], p[4], p)    
    p[0] = p[4]

def p_stmt_expression(p):
    'stmt : expression'    
    p[0] = p[1]
 
def p_expression_id(p):
    "expression : ID"

    # this is the only distinction bewtween synchronous and asynchronous updating
    if p.parser.sync:
        p[0] = p.parser.RULE_GETVALUE( p.parser.old, p[1], p)
    else:                        
        p[0] = p.parser.RULE_GETVALUE( p.parser.new, p[1], p)

def p_expression_state(p):
    "expression : STATE"

    if p[1] == 'Random':
        value = random.choice( (True, False) ) 
    else:
        value = ( p[1] == 'True' )

    # plde mode will transforms the boolean values to triplets
    if p.parser.mode ==  PLDE:
        value = util.bool_to_tuple( value )

    p[0] = value

def p_expression_tuple(p):
    "expression : LPAREN NUMBER COMMA NUMBER COMMA NUMBER RPAREN"
    if p.parser.mode == PLDE:
        p[0] = (p[2], p[4], p[6])
    else:
        p[0] = p[2] > p[6] / p[4]

def p_expression_paren(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_binop(p):
    """expression : expression AND expression
                  | expression OR expression 
    """
    if p[2] == 'and'  : 
        p[0] = p.parser.RULE_AND( p[1], p[3], p )
    elif p[2] == 'or': 
        p[0] = p.parser.RULE_OR( p[1], p[3], p )
    else:
        error( "unknown operator '%s'" % p[2] )   
   
def p_expression_not(p):
    "expression : NOT expression "
    p[0] = p.parser.RULE_NOT( p[2], p )

def p_label_init(p):
    'stmt : LABEL '    

    # this is for silencing unused token warnings, 
    # labels are not used in the grammar
    util.error('invalid construct')

def p_error(p):
    if hasattr(p, 'value'):
        util.warn( 'at %s' % p.value )
    msg = "Syntax error in -> '%s'" % LAST_LINE
    util.error( msg )

class Parser(object):
    "Represents a boolean parser"
    def __init__(self, mode, text ):
        """
        Main parser baseclass for all models
        """

        # check the validity of modes
        if mode not in VALID_MODES:
            util.error( 'mode parameter must be one of %s' % VALID_MODES)

        # initialize the parsers
        self.parser = yacc.yacc( write_tables=0, debug=0 )
        
        # set the mode
        self.parser.mode  = mode

        # optimization: this check is used very often 
        self.parser.sync =  self.parser.mode == SYNC

        # define default functions
        def get_value(state, name, p):
            return  getattr( state, name )

        def set_value(state, name, value, p):
            setattr( state, name, value )
            return value

        #
        # setting the default rules
        #
        self.parser.RULE_AND = lambda a, b, p: a and b
        self.parser.RULE_OR  = lambda a, b, p: a or b
        self.parser.RULE_NOT = lambda a, p: not a
        self.parser.RULE_SETVALUE = set_value
        self.parser.RULE_GETVALUE = get_value
        self.parser.RULE_START_ITERATION = lambda index, model: index

        #
        # internally we'll maintain a full list of tokens 
        #
        self.tokens = tokenizer.tokenize( text )
        self.init_tokens   = tokenizer.init_tokens( self.tokens )
        self.update_tokens = tokenizer.update_tokens( self.tokens )
        self.label_tokens  = tokenizer.label_tokens( self.update_tokens ) 
        self.async_tokens  = tokenizer.async_tokens( self.update_tokens ) 
      
        # finding the initial and update nodes
        self.init_nodes   = tokenizer.get_nodes( self.init_tokens )
        self.update_nodes = tokenizer.get_nodes( self.update_tokens )

        # find uninizitalized nodes        
        self.uninit_nodes = self.update_nodes - self.init_nodes

        # populate the initializer lines
        self.init_lines = map( tokenizer.tok2line, self.init_tokens )

        # populate the body by the ranks            
        labelmap = {} 
        for tokens in self.async_tokens:
            labelmap.setdefault( 1, []).append( tokens )            

        # overwrite the label token's value in nolabel modes
        if self.parser.mode in NOLABEL_MODE:
            for token in self.label_tokens:
                token[0].value = 1
        
        # for all PLDE, SYNC and ASYNC modes all ranks will be set to 1
        for tokens in self.label_tokens:
            rank  = tokens[0].value
            short = tokens[1:]
            labelmap.setdefault( rank, []).append( short )            
        
        # will iterate over the ranks in order
        self.ranks = list(sorted(labelmap.keys()))

        # build another parseable text, as lines stored for rank keys
        # by shuffling, sorting or reorganizing this body we can
        # implement various updating rule selection strategies
        self.update_lines = {}
        for key, values in labelmap.items():
            self.update_lines.setdefault(key, []).extend( map(tokenizer.tok2line, values))

class Model(Parser):
    """
    Maintains the functionality for all models
    """

    def initialize(self, missing=None, defaults={} ):
        """
        Initializes the model, needs to be called to reset the simulation 
        """

        # create a new lexer                
        self.lexer = tokenizer.Lexer().lexer
        
        if self.parser.mode == SYNC:
            # these two states are only needed for SYNC mode
            self.parser.old = state.State()
            self.parser.new = state.State()
        else:
            # in all other modes the states reflect the change immediately
            self.parser.old = self.parser.new  = state.State()

        # references must be attached to the parser class 
        # to be visible during parsing
        self.states = self.parser.states = [ self.parser.old ]

        # parser the initial data
        map( self.local_parse, self.init_lines )

        # deal with uninitialized nodes
        if self.uninit_nodes:
            if missing:
                for node in self.uninit_nodes:
                    value = missing( node )
                    self.parser.RULE_SETVALUE( self.parser.old, node, value, None)
                    self.parser.RULE_SETVALUE( self.parser.new, node, value, None)
            else:
                util.error( 'uninitialized nodes: %s' % list(self.uninit_nodes))

    @property
    def first(self):
        return self.states[0]

    @property
    def last(self):
        return self.states[-1]

    def __update(self):       
        """Internal update function"""
        p = self.parser       
        p.old = p.new
        p.new = p.new.copy()                     
        p.states.append( p.old )

    def local_parse( self, line ):
        "Used like such only to keep track of the last parsed line"
        global LAST_LINE
        LAST_LINE = line
        return self.parser.parse( line )

    def iterate( self, steps, shuffler=util.default_shuffler, **kwds ):
        """
        Iterates over the lines 'steps' times. Allows other parameters for compatibility with the plde mode
        """
        for index in xrange(steps):
            self.parser.RULE_START_ITERATION( index, self )
            self.__update()
            for rank in self.ranks:
                lines = self.update_lines[rank]
                lines = shuffler( lines )
                map( self.local_parse, lines ) 

if __name__ == '__main__':
    

    text = """
    A = True
    B = C = False

    1: B* = A or C
    2: C* = A and not D
    3: D* = B and C
    """

    model = Model( mode='sync', text=text )

    model.initialize( missing=util.true )
    
    print model.first
    model.iterate( steps=10 )
    
    for state in model.states:
        print state

    '''
    model.initialize( )

    shuffler = lambda x: []
    model.iterate( steps=10, shuffler=shuffler)
    
    for state in model.states[:10]:
        print state
    
    model.report_cycles()
    print model.fp()
    '''          