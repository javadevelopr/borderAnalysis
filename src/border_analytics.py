#!/usr/bin/env python
# File Name: border_analytics.py
#
# Date Created: Oct 27,2019
#
# Last Modified: Mon Oct 28 13:05:03 2019
#
# Author: samolof
#
# Description:	
#
##################################################################
import argparse
import sys
import csv
import collections
import operator

Keys= ('Border','Date', 'Measure','Value')
sortKeys = ('Date','Value', 'Measure','Border')
runningAverageKey = 'Date'

#pythons round() rounds down for in between floating point number
#so need to implement this to pass the tests
import math
_round = lambda n: ((n - math.floor(n)) == 0.5) and round(n) + 1  or round(n)


def _missing(self, key):
    self[key] = value = type(self)._Inner()
    return value


    

class Tree:
    """This class creates a tree data structure as a nested 'Dict' object to allow 
    operations such as tree['US-Mexico border']['2019']['Pedestrians']
    Usage E.g: 
        Tree.makeTree(3)
    
    ,will return a class data structure representing a tree of depth 3.
    Can nest to an arbitrary number of levels (subject to Python's nested scoping limits)
    """
    @staticmethod
    def makeTree(depth):
        TypeList = []
        TypeList.append(type('_' + str(0), (collections.Counter,),{})) 

        for k in range(1,depth):
            TypeList.append( type('_' + str(k), (dict,), {
                    "__missing__" : _missing,
                    "_Inner" : TypeList[len(TypeList)-1]
                    })
                    )
        return TypeList[-1]

    @staticmethod
    def makeFlatMap(rootTree, row=[]):
        """Returns a Tree object as a flat list of lists"""
        if hasattr(rootTree, 'items'):
            for k in rootTree.keys():
                yield from Tree.makeFlatMap(rootTree[k], row + [k])
        else:
            yield row + [rootTree]





parser = argparse.ArgumentParser(description="Border crossing analytics")
parser.add_argument('input', metavar='input_file',type=str, help="Csv input file")
parser.add_argument('output', metavar='output_file',  type=str,
                        help='Write output to file output_file (Optional)',
                        default="../output/report.csv"
                    )

if __name__ == "__main__":
    args = parser.parse_args()
    inputfile = args.input
    outputfile = args.output


    #the last Key is the 'Value' key
    ValueKey = Keys[-1]
    _Keys = Keys[:-1]
    averageOverKeys = tuple(filter(lambda k: k!= runningAverageKey, _Keys))

    searchTree = Tree.makeTree(len(_Keys))()


    with open(inputfile,'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        header = next(reader)
        
        keyMap = dict(map(lambda k: (k, header.index(k)), Keys))
        sortKeyMap = dict(map(lambda sk: (sk, Keys.index(sk)), sortKeys))

        _ExecStr = "searchTree" + "".join(map("[row[keyMap['{0}']]]".format, _Keys)) + "+= int(row[keyMap[ValueKey]])"

        for row in reader:
            try:
                exec(_ExecStr)
            except:
                print("{}\nError processing line: {}.".format(",".join(row),sys.exc_info()[0]))


        results = list(Tree.makeFlatMap(searchTree))

        #sort results
        results.sort(key=operator.itemgetter(*sortKeyMap.values()), reverse = True)

        #Now print out results while calculating a running average for the 'runningAverageKey' column
        with open(outputfile, 'w') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            writer.writerow(list(Keys) + ['Average'])
            _EvalStr = " and ".join(map("row[sortKeyMap['{0}']] == x[sortKeyMap['{0}']]".format, averageOverKeys))
            _EvalStr = "list(filter(lambda x:"+ _EvalStr + ", results[i+1:]))"

            for i,row in enumerate(results):
                similar = eval(_EvalStr)
                n = len(similar)
                runningAvg = n > 0 and _round(sum(map(lambda x: x[sortKeyMap[ValueKey]], similar)) / n) or 0

                writer.writerow(row + [runningAvg])

