#!/bin/bash

# script to run fetch on a set of VIVO journal URIs

# generate a list of journal URIs via SPARQL 
# specify patch to input file below
INPUT=
OLDIFS=$IFS
IFS=
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
source .env
while read journal
do
    python fetch_ids.py $journal
    sleep 1
done < $INPUT
IFS=$OLDIFS
