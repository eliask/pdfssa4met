===============================================================================
PDF Structure and Syntactic Analysis for Metadata Extraction and Tagging
===============================================================================

PDFSSA4MET attempts to provide metadata extraction and tagging based on
structural and syntactic analysis of content in XML.

PDFSSA4MET depends on pdf2xml which is available in binary form at
https://github.com/eliask/pdf2xml/tags. The master branch of the
repository also contains the source.

PDFSSA4MET is written in Python.

The following scripts can be used directly to output results to STDOUT:
pdf2xml.py
headings.py
references.py
socialtags.py

Help, options and arguments for each are available using -h or --help option
e.g.
python references.py --help
