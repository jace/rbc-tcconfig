#!/usr/bin/env python

"""
PackageGraph generates a .dot file (for GraphViz) showing dependencies
between packages. It currently only works for EPM .list definition
files.

Usage: PackageGraph.py [options] output.dot package1.list ...

Call "PackageGraph.py -h" for full list of options.
"""

__docformat__='restructuredtext'
__revision__='$Id$'

import sys
import re
import os.path
from optparse import OptionParser

class PackageDefinition:
    """
    Container for package definition.
    """
    def __init__(self, id=None, version=None, release=0):
        self.id = id
        self.version = version
        self.release = release
        self.requires = []
        self.provides = []
        self.isdep = False # True if this package is in dependency path.
        self.ischoice = False # True if provider selection is stuck here.

    def versionString(self):
        """
        Returns version string suitable for display.
        """

        if self.version is not None and self.release != 0:
            return "%s-%s" % (self.version, self.release)
        elif self.version is not None:
            return self.version
        else:
            return "R%s" % self.release

    def parseList(self, listfile):
        """
        Class constructor. Parses listfile and returns a
        PackageDefinition object.
        """
        lines = open(listfile, 'r').readlines()
        for line in lines:
            tokens = line.strip().replace('\t', ' ').split(' ')
            while '' in tokens:
                tokens.remove('')
            if line.startswith('%'): # XXX: Use regexes, you fool!
                if tokens[0] == '%product':
                    self.id = tokens[1]
                    if self.id != \
                            os.path.basename(listfile).replace('.list', ''):
                        raise ValueError, \
                            "%s: mismatch with product name %s" % (
                                listfile, self.id)
                elif tokens[0] == '%version':
                    self.version = tokens[1]
                elif tokens[0] == '%release':
                    self.release = tokens[1]
                elif tokens[0] == '%requires':
                    self.requires.append(tokens[1:])
                elif tokens[0] == '%provides':
                    self.provides.append(tokens[1])
        return self

    def __repr__(self):
        return "<PackageDefinition %s %s>" % (self.id,
                                              self.versionString())

def _markDependenciesRecurse(basepackage, packagedict, packageproviders):
    """
    Recursively mark packages as being in the dependency path.
    """
    package = packagedict[basepackage]
    package.isdep = True

    # Now that this package is being installed, everyone who provides
    # the same entities this package provides are no longer competing to
    # be selected. Unmark them.
    for provided in package.provides:
        for provider in packageproviders[provided]:
            packagedict[provider].ischoice = False

    # Find and mark dependencies.
    for required in [r[0] for r in package.requires]:
        if required in packagedict:
            try:
                _markDependenciesRecurse(required, packagedict,
                    packageproviders)
            except RuntimeError: # maximum recursion depth exceeded
                print >> sys.stderr, "Recursion error with %s and %s." % (
                    basepackage, required)
        elif required in packageproviders:
            # Only one provider? Keep following. If more than one, mark
            # all as competing to be chosen.
            if len(packageproviders[required]) == 1:
                _markDependenciesRecurse(packageproviders[required][0],
                        packagedict, packageproviders)
            else:
                if len([p for p in packageproviders[required]
                        if packagedict[p].isdep == True]) == 0:
                    for provider in packageproviders[required]:
                        packagedict[provider].ischoice = True
            #for provider in packageproviders[required]:
            #    _markDependenciesRecurse(provider, packagedict,
            #        packageproviders)

def markDependencies(bases, packages):
    """
    Given a list of base packages, recursively marks packages as being
    required to install the base packages.
    """
    packagedict = {}
    packageproviders = {}
    for package in packages:
        packagedict[package.id] = package
        for provided in package.provides:
            providers = packageproviders.get(provided, [])
            providers.append(package.id)
            packageproviders[provided] = providers
    for base in bases:
        if base in packagedict:
            _markDependenciesRecurse(base, packagedict, packageproviders)

def writePackageDef(out, options, package):
    out.write('"%s" [label="%s\\n%s" color="%s"];\n' % (package.id,
        package.id, package.versionString(), package.ischoice and
        options.providerchoice or package.isdep and options.dependency
        or options.node))

def writePackageLinks(out, options, package):
    for required in package.requires:
        if len(required) > 1:
            out.write('"%s" -> "%s" [color="%s" label="%s"];\n' % (
                package.id, required[0], options.requiresline,
                ' '.join(required[1:])))
        else:
            out.write('"%s" -> "%s" [color="%s"];\n' % (package.id,
                required[0], options.requiresline))
    for provided in package.provides:
        out.write('"%s" -> "%s" [arrowhead=none arrowtail=invinv color="%s"];\n' %
            (provided, package.id, options.providesline))
    return package.provides

def _updateProvidedList(provideddict, providedlist):
    """
    Updates the provided package dictionary.
    """
    for provided in providedlist:
        provideddict[provided] = None

def makeGraph(options, outputfile, *listfiles):
    """
    Makes dot file given output file name and list file paths.
    """
    # Prepare to create package groups
    mainpackages = []
    packagegroups = {}
    groupregexes = []
    for group in options.groups:
        packagegroups[group] = [] # Initialise blank list
        groupregexes.append((group, re.compile(group)))

    # Examine and sort packages into groups
    packages = []
    for listfile in listfiles:
        package = PackageDefinition().parseList(listfile)
        packages.append(package)
        unmatched = True
        for (groupname, groupregex) in groupregexes:
            if groupregex.search(package.id) is not None:
                unmatched = False
                packagegroups[groupname].append(package)
                break
        if unmatched:
            mainpackages.append(package)

    # Mark dependency path for packages, if requested
    markDependencies(options.bases, packages)

    # Start writing graph
    out = open(outputfile, "w")
    out.write("digraph packages {\n")
    #out.write('size="7,4.1";\n')
    out.write('node [style=filled];\n')

    # Define package groups
    groupcounter = 0
    for (groupname, grouppackages) in packagegroups.items():
        groupcounter += 1
        out.write('subgraph cluster_sg%d {\n' % groupcounter)
        out.write('label="%s";\n' % groupname)
        out.write('color=purple;\n')
        out.write('style=dashed;\n')
        for package in grouppackages:
            writePackageDef(out, options, package)
        out.write('}\n')

    # Connect packages
    providedpackages = {}
    for package in packages:
        _updateProvidedList(providedpackages,
                            writePackageLinks(out, options, package))

    # Write package definitions for ungrouped packages
    for package in mainpackages:
        writePackageDef(out, options, package)

    # Fill in details for provided packages
    for provided in providedpackages.keys():
        out.write('"%s" [color="%s"];\n' % (provided, options.provided))
    out.write("}\n")
    return 0

def main(argv):
    parser = OptionParser(version=__revision__) # XXX: Replace with version
    parser.add_option("-n", "--node", default="0.650 0.200 1.000",
        help="Package node fill color [default 0.650 0.200 1.000]")
    parser.add_option("-P", "--provided", default="0.355 0.563 1.000",
        help="Provided package node fill color [default 0.355 0.563 1.000]")
    parser.add_option("-c", "--providerchoice", default="0.0 0.3 0.4",
        help="Multiple provider choice [default 0.0 0.3 0.4]")
    parser.add_option("-r", "--requiresline", default="0.002 0.999 0.999",
        help="Requires line color [default 0.002 0.999 0.999]")
    parser.add_option("-p", "--providesline", default="0.647 0.702 0.702",
        help="Provides line color [default 0.647 0.702 0.702]")
    parser.add_option("-g", "--group", type="string", action="append",
        dest="groups", metavar="GROUPEXP", default=[],
        help="Group packages matching regex pattern")
    parser.add_option("-d", "--dependency", default="0.455 0.500 0.700",
        help="Dependency path node color [default 0.455 0.500 0.700]")
    parser.add_option("-b", "--basepackage", type="string",
        action="append", dest="bases", default=[], metavar="BASEPACKAGE",
        help="Trace dependency path from base package")
    (options, args) = parser.parse_args(args=argv[1:])
    if len(args) < 2:
        print >> sys.stderr, __doc__
        return 1
    return makeGraph(options, args[0], *args[1:])

if __name__=='__main__':
    sys.exit(main(sys.argv))
