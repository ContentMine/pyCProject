#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Converts a single-column CSV into ami-dictionary XML-format.
"""

import argparse
import os
import csv
from lxml import etree

parser = argparse.ArgumentParser(description='Converts a single-column CSV into ami-dictionary XML-format.')
parser.add_argument('--input', dest='inputfile', help='relative or absolute path of the input CSV')
parser.add_argument('--output', dest='outputfile', help='relative or absolute path of the output XML')
parser.add_argument('--title', dest='title', help='title of the dictionary')
parser.add_argument('--action', dest='action', help='what to do, either list2dict or wordfreq2dict')
args = parser.parse_args()


def list2dict(itemlist, title):
    # create XML
    root = etree.Element('root')
    root.tag = "dictionary"
    root.attrib["title"] = args.title
    for item in itemlist:
        new_elem = etree.Element('entry')
        new_elem.attrib["term"] = item
        new_elem.attrib["name"] = item
        root.append(new_elem)
    return root

def clean_itemlist(itemlist):
    """
    Does lower-casing, de-duplication and alphabeting sorting.
    """
    cleaned_itemlist = []
    for item in itemlist:
        if type(item) == list:
            item = " ".join(item)
        item = item.lower()
        cleaned_itemlist.append(item)
    return sorted(list(set(cleaned_itemlist)))

def read_wordfreq_xml(infile):
    """
    Reads in a wordfrequency result-dict.
    """
    itemlist = []
    with open(args.inputfile, "r") as infile:
        root = etree.parse(infile)
        itemlist = root.xpath("//result/text()")
    return itemlist

def read_csv(infile):
    itemlist = []
    with open(args.inputfile, "r") as infile:
        reader = csv.reader(infile, delimiter=",")
        for row in reader:
            itemlist.append(row)
    return itemlist

def main(args):
    if args.action == "list2dict":
        itemlist = read_csv(args.inputfile)
    if args.action == "wordfreq2dict":
        itemlist = read_wordfreq_xml(args.inputfile)

    cleaned_itemlist = clean_itemlist(itemlist)
    print("There are %d items in the dictionary." %len(cleaned_itemlist))
    root = list2dict(cleaned_itemlist, args.title)
    tree = etree.ElementTree(root)
    tree.write(args.outputfile)

if __name__ == '__main__':
    main(args)
