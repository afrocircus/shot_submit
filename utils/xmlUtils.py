__author__ = 'Natasha'

import xml.etree.cElementTree as ET

def createXMLfile(inputDict, outfile):
    root = ET.Element('RenderSet')
    for key in inputDict:
        value = inputDict[key]
        if type(value) == dict:
            element = ET.SubElement(root, key)
            for each in value:
                subelement = ET.SubElement(element, each)
                if type(value[each]) == list:
                    for item in value[each]:
                        ET.SubElement(subelement, 'Value').text = item
                else:
                    ET.SubElement(subelement, 'Value').text = value[each]
        else:
            ET.SubElement(root, key).text = value

    tree = ET.ElementTree(root)
    tree.write(outfile)

def readXMLfile(outfile):
    valueDict = {}
    tree = ET.ElementTree(file=outfile)
    root = tree.getroot()
    for child in root.getchildren():
        if not child.getchildren():
            valueDict[child.tag] = child.text
        else:
            for iter in child.getchildren():
                children = iter.getchildren()
                if children:
                    for i in children:
                        if len(children)>1:
                            if not valueDict.has_key(iter.tag):
                                valueDict[iter.tag] = []
                            valueDict[iter.tag].append(i.text)
                        else:
                            valueDict[iter.tag] = i.text
    return valueDict
