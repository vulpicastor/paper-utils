#!/usr/bin/env python3

import logging
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

    def add_author_entry(self, name, affiliations, notes=None):
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

    @staticmethod
    def texify_author_name(name):
        word_list = name.split()
        return '~'.join(word_list)

    @staticmethod
    def texify_affiliation_entry(notemark, affiliation):
        return f'\\textsuperscript{{notemark}}{affiliation} \\\\'

    def format_author_list(self):
        lines = []
        for author, indices in self.author_dict.items():
            latex_author = self.texify_author_name(author)
            latex_affils = ','.join(map(str, indices))
            lines.append(f'{latex_author}\\textsuperscript{{latex_affils}}')
        return lines

    def format_affiliation_list(self):
        return [self.texify_affiliation_entry(str(i), affil)
                for affil, i in self.affil_dict.items()]

    def output_latex(self):
        author_lines = self.format_author_list()
        affil_lines = self.format_affiliation_list()
        latex_macro = "{} \\\\\n{}".format(
            ',\n'.join(author_lines),
            '\\\\\n'.join(affil_lines),
        )
        return latex_macro



def read_csv(fn, skip_rows=0):
    pass
