import bz2
import json
from ipaddress import ip_address 
from gensim.corpora.wikicorpus import filter_wiki, tokenize
from scripts.utils.utils import init_logger, load_npz

logger = init_logger()
        
        
# liefert die Tokens des Inhalts text einer Wikipediaseite, deren Länge innerhalb des Bereichs [token_min_len,token_max_len] ist
def get_tokens(text, token_min_len=1, token_max_len=100):
    text = filter_wiki(text)
    return tokenize(text, token_min_len, token_max_len, True)        
            
# liefert True, falls page im Mainspace liegt (also ein Artikel ist), sonst False
# falls page das "namespace"-Attribut besitzt (ergibt sich aus dem <ns>-XML-Tag; ist nur in neueren Dumps enthalten), liegt page im Mainspace, falls dieses Attribut 0 ist
# ansonsten liegt page im Mainspace, falls der Titel mit einem Namespacepräfix aus der Liste namespace_prefixes beginnt
def is_mainspace_page(page, namespace_prefixes):
    if page.namespace:
        return page.namespace == 0
    else:
        return not any(page.title.startswith(prefix) for prefix in namespace_prefixes)
        
# liefert True, falls der Autorenname usertext einem registrierten, eingeloggten Autoren entspricht
# dazu darf usertext nicht None und keine IP-Adresse sein
def is_registered_user(usertext):
    if usertext is None:
        return False 
    try:
        ip_address(usertext.strip())
        return False
    except ValueError:
        return True
    
# liefert True, falls der Autorenname usertext einem registrierten, eingeloggten Nicht-Bot-Autoren entspricht
# der Name muss einem registrierten Autoren entsprechen und darf nicht "bot" enthalten (case-insensitiv)
# diese Prüfung kann false-positives liefern, da auch Nicht-Bot-Autoren einen Namen, der "bot" enthält, besitzen können
# da bei Autorenangaben der Revisionen aber eine explizite Bot-Angabe fehlt, ist diese Prüfung notwendig
def is_not_bot_user(usertext):
    return is_registered_user(usertext) and 'bot' not in usertext.lower()
    
# lädt die als .npz vorliegende dichte Dokument-Topic-Matrix
def load_document_topics(document_topics_path):        
    logger.info('loading dense document-topics from {}'.format(document_topics_path))
    document_topics = load_npz(document_topics_path)
    logger.info('loaded document-topics-matrix of shape {}'.format(document_topics.shape))
    logger.debug('document-topics-matrix \n{}'.format(document_topics))
    return document_topics

    
    
    
    
    
    
    
    
    