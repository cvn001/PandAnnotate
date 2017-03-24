'''
parser.blast

Parses BLAST output for annotator

created on March 23, 2017
@author: Aaron Kitzmiller <aaron_kitzmiller@harvard.edu>
@copyright: 2016 The Presidents and Fellows of Harvard College. All rights reserved.
@license: GPL v2.0
'''

import pandas as pd


def parse(tablefile, **kwargs):
    '''
    Converts BLAST to a data frame with a queryname index

    Creates dictionary of query=key, hitdata=value
    dictionary. If header is provided, must be a 
    comma separated string
    '''

    # Check requireds
    prefix      = kwargs.get('prefix')
    searchtype  = kwargs.get('searchtype')
    if prefix is None or prefix.strip() == '' or searchtype is None or searchtype.strip() == '':
        raise Exception('Cannot parse BLAST results without prefix and searchtype arguments')

    # Setup column labels
    header = kwargs.get('header', None)
    if header is None:
        column_labels = [
            'queryname',
            'sseqid',
            'pident',
            'length',
            'mismatch',
            'gapopen',
            'qstart',
            'qend',
            'sstart',
            'send',
            'eval',
            'bitscore',
        ]
    else:
        column_labels = header.split(',')

    # Add prefix to the column labels
    column_labels = [prefix + '_' + i if i != 'queryname' else i for i in column_labels]

    blast_dict = dict()
    with open(tablefile, 'r') as fopen:
        for line in fopen:
            linelist = line.strip().split()
            if searchtype in ['blastx', 'blastp']:
                linelist[0] = linelist[0].split('::')[1]

            querydict = dict(zip(column_labels, linelist))
            if querydict['queryname'] in blast_dict:
                if float(querydict[prefix + '_eval']) < float(blast_dict[querydict['queryname']][prefix + '_eval']):
                    blast_dict[querydict['queryname']] = querydict
                elif float(querydict[prefix + '_eval']) == float(blast_dict[querydict['queryname']][prefix + '_eval']) and float(querydict[prefix + '_pident']) > float(blast_dict[querydict['queryname']][prefix + '_pident']):
                    blast_dict[querydict['queryname']] = querydict
            else:
                blast_dict[querydict['queryname']] = querydict
    
    framedata = dict(zip(column_labels, [[] for i in range(len(column_labels))]))
    for query in blast_dict.keys():
        for column_label in column_labels:
            framedata[column_label].append(blast_dict[query][column_label])        
            
    blastframe = pd.DataFrame(framedata, columns=column_labels) 
    blastframe.set_index('queryname', drop=True, inplace=True)
    return blastframe