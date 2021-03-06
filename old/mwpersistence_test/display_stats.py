import argparse
import sys
import json
from mwcli import files
from tabulate import tabulate


def display_stats(input_stat_paths):
    for input_stat_path in input_stat_paths:
        print()
        print('file: "{}"'.format(input_stat_path))
        ifile = files.functions.reader(input_stat_path)
        stats = [] 
        for line in ifile:
            rev = json.loads(line)
            rev_pers = rev['persistence']
            stats.append((rev['page']['id'],rev['id'],rev_pers['revisions_processed'],rev_pers["non_self_processed"],rev_pers['persistent_tokens'],rev_pers['non_self_persistent_tokens'],rev_pers['sum_log_persisted'],rev_pers['sum_log_non_self_persisted']))
        headers = ['DocID','RevID','RevProcessed','NonSelfProcessed','PersistentTokens','NonSelfPersistentTokens','SumLogPersisted','SumLogNonSelfPersisted']
        print(tabulate(stats, headers=headers, tablefmt='orgtbl'))
    

def main():
    parser = argparse.ArgumentParser(description='displays stats of MediaWiki revision dump analysis, needs JSON files of stats (such as generated by "persistence2stats" tool'.format(sys.argv[0]))
    parser.add_argument("istatfile", nargs='+', type=argparse.FileType('r'), help='path to input JSON stat file')
    args = parser.parse_args()
    input_stat_paths = [path.name for path in args.istatfile]
    display_stats(input_stat_paths)
    
if __name__ == '__main__':
    main()