#!/bin/env python2
# -*- coding: utf-8 -*-

"""
Provides basic function to read a ContentMine CProject and CTrees into python datastructures.
"""


# import file io
import re
import os
from lxml import etree
import json

# import data handling
from bs4 import BeautifulSoup


__author__ = "Christopher Kittel"
__copyright__ = "Copyright 2015"
__license__ = "MIT"
__version__ = "0.0.1"
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
        """
        Returns a generator, yielding CTree objects.
        """
        for name in os.listdir(self.projectfolder):
            ctree = CTree(self.projectfolder, name)
            yield {ctree.ID: ctree}
    
    def get_size(self):
        """
        Returns size of dataset = number of ctrees.
        """
        i = 0
        for ct in self.get_ctrees():
            # must loop through since get_ctrees() is a generator
            i += 1
        return i

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
        Tries to lead entities, returns {} if none found.
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
        Returns a dict of available ami-plugin-results.
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
        'sequence': set(['carb3', 'prot3', 'dna', 'prot'])}
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
            assert plugin in self.available_plugins, \
                    "%s is not available, run ami-%s first." %(plugin, plugin)
            return self.results.get(plugin)
    
    def get_soup(self):
        """
        Returns the scholarly.html as a BeautifulSoup object.
        """
        with open(self.shtmlpath, "r") as infile:
            return BeautifulSoup(infile)
    
    def get_section(self, section_title):
        """
        Returns a section of shtml.
        """
        section = []
        for sec in self.get_soup().find_all():
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
        contrib_group = self.get_soup().find_all("div", {"tagx":"contrib-group"})
        for meta in contrib_group:
            for author in meta.find_all("meta", {"name":"citation_author"}):
                authors.append(author.get("content"))
        return authors
    
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
        return self.get_soup().find_all(tag, text = re.compile(text))
    
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
            tags = self.get_soup().find(tag, attr)
        else:
            tags = self.get_soup().find(tag)
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
        for ab in self.get_soup().find_all("div", {"tag":"abstract"}):
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
        return self.get_soup().find("title").string