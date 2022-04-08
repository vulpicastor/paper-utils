#!/usr/bin/env perl
# Copied from arXiv FAQs at https://arxiv.org/help/faq/whytex .
while(<STDIN>){ s/^\%.*$/\%/; s/([^\\])\%.*$/\1\%/g; print; }
exit(0);
