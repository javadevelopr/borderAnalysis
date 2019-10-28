#!/usr/bin/env python
# File Name: border_analytics_simple.py
#
# Date Created: Oct 28,2019
#
# Last Modified: Mon Oct 28 15:23:00 2019
#
# Author: samolof
#
# Description:	
#
##################################################################
import argparse
import sys,csv,collections,operator
import math

#Our data structure for sorting categories
Tree=lambda: collections.defaultdict(Tree)

#Python3 round() apparently rounds down for midpoint floating point numbers
#but Insight's tests require rounding up
_round = lambda n: ((n-math.floor(n)) == 0.5) and round(n) + 1 or round(n)


def flatten_recursive(root, row=[]):
    if hasattr(root, 'items'):
        for k in root.keys():
            yield from flatten_recursive(root[k], row + [k])
    else:
            yield row + [root]



parser = argparse.ArgumentParser(description="Border crossing analytics")
parser.add_argument('infile', type=str, help="input file")
parser.add_argument('outfile', type = str, help="output file")

borderIdx = 3; dateIdx = 4; measureIdx = 5; valueIdx = 6
outputSortOrder = [1,3,2,0] #positions of Date, Value, Measure, Border in output list

if __name__ == "__main__":
    args = parser.parse_args()
    infile = args.infile
    outfile = args.outfile

    searchTree = Tree()

    with open(infile,'r') as infile:
        reader = csv.reader(infile, delimiter=',')

        header = next(reader)

        while header == [] or header is None:
            try:
                header = next(reader)
            except StopIteration:
                print("Input file appears to be empty")
                sys.exit(1)

        for row in reader:
            border=row[3]
            date = row[4]
            measure = row[5]
            value = int(row[6])

            searchTree[border][date][measure] = searchTree[border][date].get(measure,0) + value

        #get summed results and sort by outputSortOrder (Date,Value,Measure, Border)
        resultData = list(flatten_recursive(searchTree))
        resultData.sort(key=operator.itemgetter(*outputSortOrder), reverse=True)


        #write output while also calculating running monthly average over Measure and Border
        with open(outfile, 'w') as outfile:
            writer=csv.writer(outfile, delimiter=',')
            writer.writerow(['Border','Date','Measure','Value','Average'])

            for i,row in enumerate(resultData):
                border=row[0]
                measure=row[2]
            
                #get all entries from previous months with the same measure and border
                same_border_measure = list(filter(lambda x: border==x[0] and measure == x[2],resultData[i+1:]))
                #calculate running avg by summing all the values for previous months and dividing
                #by the number of previous months
                n = len(same_border_measure)
                runningAvg = n > 0 and _round(sum(map(lambda x: x[3], same_border_measure)) / n) or 0

                writer.writerow(row + [runningAvg])

    print("Done!")

