import argparse
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.matutils import MmWriter
from gensim.corpora import Dictionary
from scripts.utils.utils import init_logger, read_lines
from scripts.utils.documents import is_mainspace_page, is_registered_user, is_not_bot_user, get_tokens

logger = init_logger()


# liefert Autornamen von contributor in id2author oder None, falls nicht vorhanden
def get_author_id(contributor, id2author):
    username = contributor.user_text
    return id2author.token2id.get(username)

    
# berechnet für jede Version eines Autoren, der in id2author vorkommt als Beitragswert: 1
def contrib_value_one(revisions, id2author):
    for rev in revisions:
        authorid = get_author_id(rev.contributor, id2author)
        if authorid is not None:
            yield authorid, 1        
        
        
# berechnet für jede Version eines Autoren, der in id2author vorkommt als Beitragswert: max(0, #Tokens - #Tokens des Vorgängers)
def contrib_value_diff_numterms(revisions, id2author):
    # da Berechnung der Anzahl Tokens aufwändig: berechne nur Anzahl Tokens, falls für Version eines gültigen Autoren nötig
    # speichere Anzahl Tokens einer Version zwischen, da Nachfolge-Version diese ggf. auch braucht
    token_nums = {-1: 0}
    def get_num_tokens(i): 
        if i not in token_nums:
            token_nums[i] = len(get_tokens(revisions[i].text))
        return token_nums[i]
        
    for i, rev in enumerate(revisions):
        authorid = get_author_id(rev.contributor, id2author)
        if authorid is not None:
            num_tokens = get_num_tokens(i)
            prev_num_tokens = get_num_tokens(i-1)
            rev_value = num_tokens-prev_num_tokens
            if rev_value > 0:
                yield authorid, rev_value
    

# Beitragsfunktionen: liefern zu einer Liste von Versionen und einem Autor-ID-Mapping eine Liste von Versionswerte
CONTRIBUTION_VALUE_FUNCTIONS = {
    'one': contrib_value_one,
    'diff_numterms': contrib_value_diff_numterms,
}

# liefert einen Generator ((Revisionen, Seitentitel) für alle Seiten im Mainspace (Artikel))
def get_revisions_of_pages(history_dump, namespace_prefixes):
    num_pages_total = 0
    num_pages_ms = 0
    num_revisions_ms = 0
    num_revisions_ms_registered_users = 0
    num_revisions_ms_nonbots = 0
    for page in history_dump:
        num_pages_total += 1
        logger.debug('page {}'.format(page.title))
        if is_mainspace_page(page, namespace_prefixes):
            num_pages_ms += 1
            logger.debug('page {} considered mainspace'.format(page.title))
            
            # lade Revisionen des Artikels
            revisions = tuple(revision for revision in page)
            num_revisions_ms += len(revisions)
            logger.debug('page {} having {} revisions'.format(page.title, len(revisions)))
            #authors_ms.update(rev.contributor.user_text for rev in revisions if rev.contributor.user_text is not None)
                
            # nur für Statistik: zähle Revisionen registrierter Autoren
            revisions_ms_registered_users = tuple(revision for revision in revisions if is_registered_user(revision.contributor.user_text))
            num_revisions_ms_registered_users += len(revisions_ms_registered_users)
            logger.debug('page {} having {} revisions of registered users'.format(page.title, len(revisions_ms_registered_users)))
                
            # nur für Statistik: zähle Revisionen registrierter Nicht-Bot-Autoren
            revisions_ms_nonbots = tuple(revision for revision in revisions_ms_registered_users if is_not_bot_user(revision.contributor.user_text))
            num_revisions_ms_nonbots += len(revisions_ms_nonbots)
            logger.debug('page {} having {} revisions of non-bot users'.format(page.title, len(revisions_ms_nonbots)))
                
            yield revisions, page.title
                
    logger.info('{} pages total'.format(num_pages_total))
    logger.info('{} pages considered mainspace'.format(num_pages_ms))
    logger.info('{} revisions in mainspace pages'.format(num_revisions_ms))
    logger.info('{} revisions of registered users in mainspace'.format(num_revisions_ms_registered_users))
    logger.info('{} revisions of non-bot users in mainspace'.format(num_revisions_ms_nonbots))
    

    
# liefert einen Generator ((Autorname für alle registrierten nicht-Bot-Autoren des Artikels) für alle Artikel)
def get_revision_authors_of_pages(history_dump, namespace_prefixes):
   #for revisions, pagetitle in filter_revisions(get_revisions_of_pages(history_dump, namespace_prefixes)):
    for revisions, pagetitle in get_revisions_of_pages(history_dump, namespace_prefixes):
        yield (revision.contributor.user_text for revision in revisions if revision.contributor.user_text is not None)    
    
# liefert Generator (((Autor-ID, Versionswert) für alle Versionen), Titel für alle Artikel in page_revisions_titles ) 
# Berechnung der Versionswerte basiert auf revision_value_fun
def get_revision_values(page_revisions_titles, id2author, revision_value_fun):    
    num_considered_revision_values = 0
    num_articles_with_revision_values = 0
    authorids_with_revisions = set()
    for revisions, pagetitle in page_revisions_titles:
        logger.debug('page {} having {} revisions'.format(pagetitle, len(revisions)))
        authorids_revisionvalues = tuple(revision_value_fun(revisions, id2author))
        logger.debug('page {} having {} contribution values of valid authors'.format(pagetitle, len(authorids_revisionvalues)))
        num_considered_revision_values += len(authorids_revisionvalues)
        authorids_with_revisions.update(authorid for authorid,rev_value in authorids_revisionvalues)
                
        if len(authorids_revisionvalues) > 0:
            num_articles_with_revision_values += 1
            yield authorids_revisionvalues, pagetitle
        
    logger.info('{} revisions having postive revision values'.format(num_considered_revision_values))
    logger.info('{} articles having at least 1 contribution value greater zero'.format(num_articles_with_revision_values))
    logger.info('{} different authorids with at least 1 contribution'.format(len(authorids_with_revisions)))
    
    
# entfernt alle Autoren aus id2author, für die keep_predicate False liefert
def remove_from_dictionary(id2author, keep_predicate):
    bad_token_ids = [id for author,id in id2author.token2id.items() if keep_predicate(author) == False]
    id2author.filter_tokens(bad_ids=bad_token_ids, good_ids=None)
    

# einfache Klasse, die einen Generator wrappt und self.metadata = True setzt, damit gensim die Artikeltitel speichert
class MetadataCorpus(object):
    def __init__(self, generator):
        self.generator = generator
        self.metadata = True
    def __iter__(self):
        yield from self.generator
    
    
def main():
    parser = argparse.ArgumentParser(description='creates an id2author mapping gensim dictionary a document->authorid contributions MatrixMarket file and a binary article title file from a given WikiMedia *-pages-meta-history dump (considering only articles in mainspace!)')
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('w'), help='path to output text id2author dictionary (.txt/.txt.bz2)', required=True)
    parser.add_argument('--contribs', type=argparse.FileType('w'), help='path to output MatrixMarket contributions .mm file; also creates a binary article title file CONTRIBS.metadata.cpickle', required=True)
    parser.add_argument('--contribution-value', choices=CONTRIBUTION_VALUE_FUNCTIONS, help='calculated per-contribution value; choices: {}'.format(CONTRIBUTION_VALUE_FUNCTIONS.keys()), required=True)
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore')    
        
    args = parser.parse_args()
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_id2author_path = args.id2author.name
    output_contribs_path = args.contribs.name
    contribution_value = args.contribution_value
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
        
    logger.info('running with:\n{}'.format(pformat({'input_history_dump_path':input_history_dump_path, 'output_id2author_path':output_id2author_path, 'output_contribs_path':output_contribs_path, 'contribution_value':contribution_value, 'namespace_prefixes':namespace_prefixes})))        
            
    # konstruiere id2author-Dictionary: mappt Autornamen von registrierten, Nicht-Bot-Autoren auf IDs und umgekehrt
    with smart_open(input_history_dump_path) as history_dump_file:    
        logger.info('generating author->id mappings')
        history_dump = xml_dump.Iterator.from_file(history_dump_file)
        # benutze id2word-Dictionary von gensim als id2author-Dictionary: Autoren entsprechen Termen
        id2author = Dictionary(get_revision_authors_of_pages(history_dump, namespace_prefixes))
        logger.info('found {} different authors'.format(len(id2author)))
        logger.info('removing non-registered authors')
        remove_from_dictionary(id2author, is_registered_user)
        logger.info('reduced to {} registered authors'.format(len(id2author)))
        logger.info('removing bots')
        remove_from_dictionary(id2author, is_not_bot_user)
        logger.info('reduced to {} registered non-bot authors'.format(len(id2author)))
        id2author.compactify()
        id2author.save_as_text(output_id2author_path)
        
    # berechne & speichere Einträge (Autor-ID, Versionswert) Versionen gültiger Autoren für alle Artikel 
    with smart_open(input_history_dump_path) as history_dump_file: 
        logger.info('generating MatrixMarket representation per revision: (docid, authorid, value of revision)')
        history_dump = xml_dump.Iterator.from_file(history_dump_file)
        revision_value_fun = CONTRIBUTION_VALUE_FUNCTIONS[contribution_value]
        doc_auth_contribs = MetadataCorpus(get_revision_values(get_revisions_of_pages(history_dump, namespace_prefixes), id2author, revision_value_fun))
        MmWriter.write_corpus(output_contribs_path, corpus=doc_auth_contribs, num_terms=len(id2author), index=False, progress_cnt=10000, metadata=True)   
    
    
        
if __name__ == '__main__':
    main()
    
    
    
    
    
    