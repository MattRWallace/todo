#!/usr/bin/python

import re
import argparse
import os
import sys
import datetime


def printHeader(outfile, directory):
    outfile.write("Inventory of 'TODO' notations in file: " + directory + "\n")
    outfile.write("=======================================" + "=" * len(directory) + "\n")


def printFooter(outfile, root):
    outfile.write('----\n')
    outfile.write("Report generated: " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + "\n")
    outfile.write("Root directory:   " + root + "\n")


def parseTodos(infile, outfile, path):
    labelWritten = False
    lineno = 1
    for line in infile:
        match = re.search('TODO:\s*(.*)$', line)
        if match is not None:
            if not labelWritten:
                outfile.write(path + "\n")
                outfile.write("-" * len(path) + "\n")
                outfile.write("* " + str(lineno) + ": " + match.group(1) + "\n")
                lineno += 1
    outfile.write("\n")


parser = argparse.ArgumentParser(description='Recursively parse a directory tree and compile a report of "TODO" comments.')
parser.add_argument('-r', '--root', help='Directory that is to be the root for the parse', required=False, default=os.getcwd())
parser.add_argument('-t', '--html', help='Compile report as HTML', required=False, default=False, action='store_true')
parser.add_argument('-o', '--output', help='Specify output file name', required=False, default='todo')
parser.add_argument('-s', '--save', help='Location to save output file', required=False, default=os.getcwd())
parser.add_argument('-d', '--hidden', help='Include hidden files', required=False, default=False)
#TODO: add option to specify list of regex patterns to exclude from processing

# parse the privided arguments
args = vars(parser.parse_args())

root = args['root']
html = args['html']
if html:
    try:
        import markdown
    except ImportError:
        html = False
        sys.stderr.write('Importing markdown module failed, falling back to text only mode.\n')

output = args['output'] + '.html' if html else args['output'] + '.md'
hidden = args['hidden']

#open the output file
outfile = open(output, 'w')

# print output file header
printHeader(outfile, root)

for folder, subs, files in os.walk(root):
    if hidden:
        # remove hidden folders and files
        files = [f for f in files if not f[0] == '.']
        subs[:] = [s for s in subs if not s[0] == '.']
    for filename in files:
        abspath = os.path.abspath(os.path.join(folder, filename))
        with open(abspath, 'r') as current:
            parseTodos(current, outfile, abspath)
            current.close()

# cleanup
printFooter(outfile, root)
outfile.close()

# convert the output to HTML if it was requested
if html:
    with open(output, 'r+') as outfile:
        contents = outfile.read()
        html = markdown.markdown(contents)
        outfile.seek(0)
        outfile.truncate()
        outfile.write(html)
        outfile.close()
