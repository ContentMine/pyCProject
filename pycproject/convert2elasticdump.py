"""
takes input from a CProject and converts it to
metadata.json and facts.json with format similar to elasticsearch-dump
from ContentMine-API
"""

import os
import json
import argparse
from readctree import CProject

def write_factjson(cproject, outputfolder):
    for result in cproject.get_results():
        if (result.get("type") != "word" and result.get("exact") is not None):
            source = {}
            source["term"] = result.get("exact")
            source["prefix"] = result.get("pre")
            source["post"] = result.get("post")
            source["cprojectID"] = result.get("ID")
            source["identifiers"] = {"contentmine":result.get("type")}
            raw = {"_index":"facts",
                    "_type":"snippet",
                    "_source":source}
            with open(os.path.join(outputfolder, "facts.json"), "a") as outfile:
                outfile.write(json.dumps(raw)+"\n")

def write_metadatajson(cproject, outputfolder):
    for ctree in cproject.get_ctrees():
        source = ctree.metadata
        source["cprojectID"] = ctree.ID
        raw = {"_index":"metadata",
                "_type":"eupmc",
                "_source":source}
        with open(os.path.join(outputfolder, "metadata.json"), "a") as outfile:
            outfile.write(json.dumps(raw)+"\n")

def main(args):
    cproject = CProject(args.raw, args.name)
    write_factjson(cproject, args.output)
    write_metadatajson(cproject, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert facts and metadata from CProjects to input-json for visualizations')
    parser.add_argument('--raw', dest='raw', help='relative or absolute path of the raw data folder', required=True)
    parser.add_argument('--name', dest='name', help='name of the CProject', required=True)
    parser.add_argument('--output', dest='output', help='relative or absolute path of the output folder', required=True)
    args = parser.parse_args()
    main(args)
