#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG
if [ ! -z ${DEBUG+x} ]; then
    export DEBUG=$DEBUG
fi

CONTRIB_PREFIX=output/contribs/$PREFIX
GRAPH_PREFIX=output/graph/$PREFIX
COMM_PREFIX=output/communities/$PREFIX

CONTRIB_VALUES=($CONTRIB_VALUES)
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"
COAUTH_MODES=($COAUTH_MODES)
echo "COAUTH_MODES ${COAUTH_MODES[@]}"
COMM_METHODS=($COMM_METHODS)
echo "COMM_METHODS ${COMM_METHODS[@]}"

# Plots zu #Autoren je Dokument, #Dokumente je Autor
CONTRIBS_STATS_DIR=output/stats/community_contribs
mkdir -p $CONTRIBS_STATS_DIR
CONTRIBS_STATS_PREFIX=$CONTRIBS_STATS_DIR/$PREFIX
QUANTILE=0.95
echo "plotting number of different docs per author, different authors per doc distributions"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ACC_CONTRIBS=$CONTRIB_PREFIX-$CONTRIB_VALUE-acc-contribs.mm.bz2
    IMG_PREFIX=$CONTRIBS_STATS_PREFIX-$CONTRIB_VALUE-contribs
    python3 -m scripts.stats.community.plot_contribs_dists --acc-contribs=$ACC_CONTRIBS --img-prefix=$IMG_PREFIX --quantile-order=$QUANTILE
done

# Statistiken zu Zusammenhangskomponenten der Graphen
COMPONENTS_STATS_DIR=output/stats/community_components
mkdir -p $COMPONENTS_STATS_DIR
COMPONENTS_STATS_PREFIX=$COMPONENTS_STATS_DIR/$PREFIX
QUANTILE=0.99
echo "plotting document network connected component statistics"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    COAUTH_MODE=mul # beschränkung hier auf "mul", da Struktur der Graphen gleich, nur Gewichte verschieden
    GRAPH_FILE=$GRAPH_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-coauth.graph.gz
    IMG_FILE=$COMPONENTS_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-components.pdf
    LOG_FILE=$COMPONENTS_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-components.log
    python3 -m scripts.stats.community.plot_components_sizes_dist --graph=$GRAPH_FILE --img=$IMG_FILE --quantile-order=$QUANTILE |& tee $LOG_FILE
done

# betrachte (pruned) bipartiten Graphen: bestimme Mapping: Dokumenttitel -> Liste der Namen adjazenter Autoren
DOC_AUTHORS_STATS_DIR=output/stats/community_document_authors
mkdir -p $DOC_AUTHORS_STATS_DIR
DOC_AUTHORS_STATS_PREFIX=$DOC_AUTHORS_STATS_DIR/$PREFIX
echo "determining authors of each document"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    BIPART_GRAPH=$GRAPH_PREFIX-$CONTRIB_VALUE-doc-auth-bipartite.graph.bz2
    ID2AUTHOR=$CONTRIB_PREFIX-$CONTRIB_VALUE-id2author.txt.bz2
    TITLES=$CONTRIB_PREFIX-$CONTRIB_VALUE-titles.json.bz2
    TITLE2AUTHORNAMES=$DOC_AUTHORS_STATS_PREFIX-$CONTRIB_VALUE-title2authornames.json
    python3 -m scripts.stats.community.get_authors_of_titles_pruned --bipart-graph=$BIPART_GRAPH --id2author=$ID2AUTHOR --titles=$TITLES --title2authornames=$TITLE2AUTHORNAMES
done

# plotte absteigend sortierte Größen der Communities
COMMUNITY_SIZES_STATS_DIR=output/stats/community_sizes
mkdir -p $COMMUNITY_SIZES_STATS_DIR
COMMUNITY_SIZES_STATS_PREFIX=$COMMUNITY_SIZES_STATS_DIR/$PREFIX
echo "plotting community size distributions"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do
        for COMM_METHOD in "${COMM_METHODS[@]}"; do
            COMM_FILE=$COMM_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-communities.json.bz2
            IMG_FILE=$COMMUNITY_SIZES_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-community-sizes.pdf
            python3 -m scripts.stats.community.plot_communities_sizes_dist --communities=$COMM_FILE --img=$IMG_FILE
        done
    done
done


