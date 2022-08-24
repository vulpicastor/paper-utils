#!/usr/bin/env python3

import argparse
import csv
import itertools
import logging
import sys
import unicodedata

logger = logging.getLogger()


class AuthorList:

    def __init__(self):
        self.author_dict = {}
        self.affil_dict = {}
        self.notes_dict = {}
        # By convention, affiliations are 1-indexed.
        self.affil_index = 1

    @staticmethod
    def _normalize(s):
        return unicodedata.normalize('NFKC', s.strip())

    def add_author_entry(self, name, affiliations, notes=None, orcid=None):
        normalized_name = self._normalize(name)
        if normalized_name in self.author_dict:
            raise ValueError(f'Duplicate author name "{normalized_name}"')
        affil_indices = []
        if not affiliations:
            logger.warning('Empty affiliation list for author "%s"', normalized_name)
        for affil in affiliations:
            normalized_affil = self._normalize(affil)
            if normalized_affil in self.affil_dict:
                affil_indices.append(self.affil_dict[normalized_affil])
            else:
                self.affil_dict[normalized_affil] = self.affil_index
                affil_indices.append(self.affil_index)
                self.affil_index += 1
        self.author_dict[normalized_name] = affil_indices
        if notes:
            self.notes_dict[normalized_name] = notes

    @staticmethod
    def texify_author_name(name):
        word_list = name.split()
        return '~'.join(word_list)

    @staticmethod
    def texify_affiliation_entry(notemark, affiliation):
        return f'$^{{{notemark}}}${affiliation} \\\\'

    def format_author_list(self):
        lines = []
        last_author = len(self.author_dict) - 1
        for i, (author, indices) in enumerate(self.author_dict.items()):
            latex_author = self.texify_author_name(author)
            latex_affils = '\\textsuperscript{{{}}}'.format(','.join(map(str, indices)))
            if author in self.notes_dict:
                author_notes = '\n'.join(
                    '\\thanks{{{}}}'.format(n) for n in self.notes_dict[author])
                latex_affils = '{}%\n{}'.format(latex_affils, author_notes)
            if i < last_author - 1:
                lines.append(f'{latex_author},{latex_affils}')
            else:
                lines.append(f'{latex_author}\\thinspace{latex_affils}')
                if i < last_author:
                    lines.append('and')
        lines.append(r'\\')
        return lines

    def format_affiliation_list(self):
        return [self.texify_affiliation_entry(str(i), affil)
                for affil, i in self.affil_dict.items()]

    def output_latex(self):
        author_lines = self.format_author_list()
        affil_lines = self.format_affiliation_list()
        latex_macro = '\n'.join(itertools.chain(author_lines, affil_lines))
        return latex_macro



def read_csv(f, args):
    header = f.readline()
    columns = {c.lower(): i for i, c in enumerate(header.strip().split(','))}
    reader = csv.reader(sys.stdin)
    author_entries = []
    for row in reader:
        author_entry = {}
        if author_name := row[columns['name']].strip():
            author_entry['name'] = author_name
        else:
            continue
        affil_list = []
        for i in range(args.max_affil):
            affil_col = 'affiliation {}'.format(i + 1)
            if affil := row[columns[affil_col]].strip():
                affil_list.append(affil)
        author_entry['affiliations'] = affil_list
        note_list = []
        for i in range(args.max_note):
            note_col = 'note {}'.format(i + 1)
            if note := row[columns[note_col]].strip():
                note_list.append(note)
        if note_list:
            author_entry['notes'] = note_list
        author_entries.append(author_entry)
    return author_entries



def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate MNRAS-style author list from CSV.',
        prog='mkauthor_mnras.py')
    parser.add_argument(
        '--max-affil', type=int, default=4,
        help='Maximum number of columns for affiliations in the CSV file.')
    parser.add_argument(
        '--max-note', type=int, default=1,
        help='Maximum number of columns for author notes in the CSV file.')
    return parser.parse_args()



def main():
    args = parse_args()
    author_entries = read_csv(sys.stdin, args)
    author_list = AuthorList()
    for entry in author_entries:
        author_list.add_author_entry(**entry)
    print(author_list.output_latex())



if __name__ == '__main__':
    main()
