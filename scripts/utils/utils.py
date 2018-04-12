import logging
import sys, os
from gensim.utils import tokenize

def init_gensim_logger():
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.DEBUG if 'DEBUG' in os.environ else logging.INFO
    mpl_logger = logging.getLogger('matplotlib') # deaktiviere matplotlib-debug-logging
    mpl_logger.setLevel(logging.INFO) 
    return program, logger
    
    
def number_of_tokens(str):
    return sum(1 for token in tokenize(str))