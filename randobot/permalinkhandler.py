import xml.etree.ElementTree as ET
from collections import OrderedDict

import os
from paths import RANDO_ROOT_PATH

def getChildTypes(*args):
  UI_PATH = os.path.join(RANDO_ROOT_PATH,"wwr_ui")

  tree = ET.parse(os.path.join(UI_PATH,"randomizer_window.ui"))
  root = tree.getroot()

  listChildren = root.findall(".//")

  invalidList = ["QMainWindow","QScrollArea","QLabel","QPushButton","QLineEdit","QWidget","QTabWidget","QGroupBox"]

  resultDict = OrderedDict()

  for child in listChildren:
    if( (child.tag == "widget") and (child.attrib["class"] not in invalidList) ):
      key = child.attrib["name"]
      val = child.attrib["class"]
      resultDict[key] = val
      #print(child.tag,child.attrib)

  return resultDict

def cleanChildTypes(input):
  resultDict = OrderedDict(sorted(input.items(), key=lambda t: t[0][1]))
  resultDict = OrderedDict(sorted(resultDict.items(), key=lambda t: t[0][0]))
  resultDict = OrderedDict(sorted(resultDict.items(), key=lambda t: t[1][2]))
  resultDict = OrderedDict(sorted(resultDict.items(), key=lambda t: t[1][1]))

  return resultDict

def printChildTypes(input):
  lastClass = ""
  for key in input:
    value = input[key]
    lenKey = len(key)
    spacer = " "*40
    if value != lastClass:
      print("\n")
      lastClass = value
    print(key,spacer[lenKey:],value)




#printChildTypes(cleanChildTypes(getChildTypes()))
