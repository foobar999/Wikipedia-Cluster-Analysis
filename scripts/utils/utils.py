import logging
import sys, os

def init_gensim_logger():
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.DEBUG if 'DEBUG' in os.environ else logging.INFO
    return program, logger