#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides basic function to read a ContentMine CProject and CTrees into python datastructures.
"""


# import file io
import re
import os
from lxml import etree
import json
from collections import Counter

# import data handling
from bs4 import BeautifulSoup


__author__ = "Christopher Kittel"
__copyright__ = "Copyright 2015"
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Christopher Kittel"
__email__ = "web@christopherkittel.eu"
__status__ = "Prototype" # 'Development', 'Production' or 'Prototype'



class CProject(object):
    """
    Maps the CProject file structure to a data object.
    Initialize with the project path (absolute) and foldername.
    """
    def __init__(self, projectpath, projectname):
        self.projectname = projectname
        self.projectfolder = os.path.join(projectpath, projectname)
        self.size = self.get_size()
    
    def get_ctrees(self):
        return iter(self)
    
    def get_size(self):
        return len(self)

    def get_ctree(self, ctreeID):
        """
        Return a CTree object by its ID.
        """
        return CTree(self.projectfolder, ctreeID)
        
    def get_title(self, ctreeID):
        """
        Returns the title of a paper by its ID.
        """
        return self.get_ctree(ctreeID).get_title()

    def get_results(self):
        """
        Iterates over all results, yields content of results.xml as dict,
        plus name of ami-plugin and the plugin-type.
        """
        for ctree in iter(self):
            for plugin, types in ctree.results.items():
                for ptype, results in types.items():
                    for result in results:
                        result["plugin"] = plugin
                        result["type"] = ptype
                        yield result

    def __len__(self):
        """
        Returns size of dataset = number of ctrees.
        """
        # must loop through since get_ctrees() is a generator
        return sum(1 for x in self.get_ctrees())

    def __iter__(self):
        """
        Returns a generator, yielding CTree objects.

        Yields: CTree
        """
        for dir_entry in os.listdir(self.projectfolder):
            if os.path.isdir(os.path.join(self.projectfolder, dir_entry)):
                ctree = CTree(self.projectfolder, dir_entry)
                yield ctree

    def __repr__(self):
        return '<CProject: {}>'.format(self.projectname)

        
class CTree(object):
    """
    Reads a CTREE within a CProject,
    and maps the CTree file structure to a data object.
    Provides some preprocessing and data access methods.
    self.ID = "string"
    self.shtmlpath = "path/to/scholarly.html"
    self.fulltextxmlpath = "path/to/fulltext.xml"
    self.available_plugins = []
    self.plugin_queries = {'regex': set(['regexname']), 
                           'gene': set(['human']), 
                           'sequence': set(['carb3', 'prot3', 'dna', 'prot']),
                           'species':set([binomial, genus, genussp])}
    self.results = {'species':{'binomial':[list_of_dicts]}}
    self.entities = {"PERSON": [], "LOCATION": [], "ORGANIZATION": []}
    """
    
    def __init__(self, projectfolder, ctreeID):
        self.path = os.path.join(projectfolder, ctreeID)
        self.ID = ctreeID
        self.shtmlpath = self._get_shtmlpath()
        self.fulltextxmlpath = self._get_fxmlpath()
        self.resultspath = os.path.join(self.path, "results")
        self.available_plugins = self._get_plugins()
        self.plugin_queries = self._get_queries()
        self.results = self._get_results()
        self.entities = self._load_entities()
    
    def _load_entities(self):
        """
        Tries to load entities, returns {} if none found.
        """
        try:
            with open(os.path.join(os.getcwd(), self.path, "entities"), "r") as dumpfile:
                return json.load(dumpfile)
        except:
            # needs logging for missing entity results
            return {}
    
    def _get_shtmlpath(self):
        return os.path.join(self.path, "scholarly.html")
    
    def _get_fxmlpath(self):
        return os.path.join(self.path, "fulltext.xml")
    
    def _get_plugins(self):
        """
        Returns a list of available ami-plugin-results.
        ['sequence', 'regex', 'gene']
        """
        try:
            return os.listdir(self.resultspath)
        except:
            # needs logging of missing plugin-results
            return []
    
    def _get_queries(self):
        """
        Returns a dict of plugin:types,
        where plugin is an ami-plugin and types are the
        queries that have been run.
        {'regex': set(['clintrialids']), 
        'gene': set(['human']), 
        'sequence': set(['carb3', 'prot3', 'dna', 'prot']),
        'species': set(['binomial', 'genus', 'genussp'])}
        """
        return {plugin:set(os.listdir(os.path.join(self.resultspath, plugin))) 
            for plugin in self.available_plugins}
            
    
    def _get_results(self):
        results = {}
        for plugin, queries in self.plugin_queries.items():
            results[plugin] = {}
            for query in queries:
                results[plugin][query] = self.read_resultsxml(
                                                    os.path.join(self.resultspath,
                                                                 plugin,
                                                                 query,
                                                                 "results.xml"))
        return results
        
    def read_resultsxml(self, filename):
        """
        Reads a results xml,
        returns a list of dicts containing attribs and values.
        """
        try:
            with open(filename, 'r') as infile:
                tree = etree.parse(infile)
            root = tree.getroot()
            results = root.findall('result')
            return [res.attrib for res in results]
        except:
            # needs logging of missing results.xml
            return []
    
    def show_results(self, plugin):
        """
        Returns ami-plugin results as a dictionary with
        {plugin-type: [list of results]}
        Args: plugin = "string", one of ["gene", "sequence", "regex", "species"]
        Returns: list of results
        """
        # catch entities request first, since not official plugin
        if plugin == "entities":
            return self.entities
        else:
            if not plugin in self.available_plugins:
                print("%s is not available for %s, run ami-%s first." %(plugin, self.ID, plugin))
            else:
                return self.results.get(plugin)
    
    def get_shtml(self):
        """
        Returns the scholarly.html as a BeautifulSoup object.
        """
        with open(self.shtmlpath, "r") as infile:
            return BeautifulSoup(infile, "lxml")
    
    def get_fulltext_xml(self):
        with open(self.fulltextxmlpath, "r") as infile:
            return etree.parse(infile)

    def get_section(self, section_title):
        """
        Returns a section of shtml.
        """
        section = []
        for sec in self.get_shtml().find_all():
            if sec.string == section_title:
                for sib in sec.next_siblings:
                    section.append(sib.string)
        try:
            section = " ".join(section)
            section = " ".join(section.split())
        except:
            # needs logging of empty section for document
            section = ""
        return section
        
    def get_authors(self):
        """
        Searches the scholarly.html for the contrib-group tag,
        returns a list of authors.
        """
        authors = []
        contrib_group = self.get_shtml().find_all("div", {"class":"contrib-group"})
        for contrib in contrib_group:
            for author in contrib.find_all("span", {"class":"citation_author"}):
                authors.append(author.string)
        return authors

    def get_keywords(self):
        """
        Searches the scholarly.html for the contrib-group tag,
        returns a list of authors.
        """
        keywords = [kwd.text for kwd in self.get_fulltext_xml().getroot().xpath("//kwd")]
        return keywords

    def get_institutions(self):
        """
        Searches the scholarly.html for the contrib-group tag,
        returns a list of authors.
        """
        institutions = []
        return institutions

    def get_journal(self):
        return self.get_fulltext_xml().getroot().xpath("//journal-title/text()")[0]
    
    def get_acknowledgements(self):
        return self.get_section("Acknowledgements")
    
    def query_soup(self, tag, text):
        """
        Finds tags containing a certain text,
        returns a list of BeautifulSoup tag objects.
        Args: tag = "string"
              text = "string"
        Returns: [bs4.tag, bs4.tag, bs4.tag3]
        """
        return self.get_shtml().find_all(tag, text = re.compile(text))
    
    def find_tag(self, tag, attr=None):
        """
        Searches the scholarly.html for a specific tag,
        returns the text of the first instance found.
        Args: tag = "string"
              attr = {"attribute":"value"}
        Returns: "string"
        """
        text = [""]
        if attr is not None:
            tags = self.get_shtml().find(tag, attr)
        else:
            tags = self.get_shtml().find(tag)
        if tags:
            for p in tags.find_all("p"):
                if p.string:
                    text.append(p.string)
        text = " ".join(text)
        return " ".join(text.split())
    
    def get_competing_interests(self):
        """
        Searches the scholarly.html for a section leading in with
        "Competing interests", returns the text following after.
        Returns: "string"
        """
        cis = []
        for ci in self.query_soup("b", "Competing interests"):
            cis.append(ci.find_next().string)
        try:
            text = " ".join(cis)
        except:
            # needs logging of empty text for document
            text = ""
        text = " ".join(text.split())
        return text
    
    def get_abstract(self):
        """
        Searches the scholarly.html for the attribute "abstract",
        returns the text.
        Returns: "string"
        """
        abstract = []
        for ab in self.get_shtml().find_all("div", {"tag":"abstract"}):
            for p in ab.find_all("p"):
                abstract.append(p.string)
        try:
            return " ".join(abstract)
        except:
            # needs logging for missing abstract in document
            return ""
    
    def get_title(self):
        """
        Searches the scholarly.html for the "title" tag,
        returns the corresponding string.
        Returns: "string"
        """
        return self.get_fulltext_xml().getroot().xpath("//article-title/text()")[0]

    def __repr__(self):
        return '<CTree: {}>'.format(self.ID)

    def get_classifier_features(self):
        """
        Yields feature dictionaries:

        {'ID': ['PMC4427447'],
          'authors': ['Kraisak Kesorn',
           'Phatsavee Ongruk',
           'Jakkrawarn Chompoosri',
           'Atchara Phumee',
           'Usavadee Thavara',
           'Apiwat Tawatsin',
           'Padet Siriyasatien'],
          'binomial': [('Ae. aegypti', 20),
           ('Aedes aegypti', 2),
           ('Model construction', 1),
           ('Data integration', 1)],
          'journal': ['PLoS ONE'],
          'keywords': [],
          'title': ['Morbidity Rate Prediction of Dengue Hemorrhagic Fever (DHF) Using the Support Vector Machine and the ']
        }
        """
        features = {}
        features["authors"] = self.get_authors()
        features["title"] = [self.get_title()]
        features["keywords"] = self.get_keywords()
        features["journal"] = [self.get_journal()]
        features["binomial"] = Counter([r.get("exact") for r in self.results.get("species").get("binomial")]).most_common(5)
        features["ID"] = [self.ID]
        return features