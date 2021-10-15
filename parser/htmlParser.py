#!/usr/bin/env python
# coding: utf-8



import cssutils
from bs4 import BeautifulSoup
from copy import deepcopy



# return a list of css
def getCSStext(path):

    cssText = []
    # htmlfile = open(path, 'r', encoding='latin-1')
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    # soup = BeautifulSoup(str(htmlhandle), 'html.parser').find(name='style', type='text/css').find_all(recursive=False)
    soup = BeautifulSoup(str(htmlhandle), 'html.parser').find_all(name='style')
    for style in soup:
        # print("soup = " + str(style))
        if isCSStext(str(style)):
            cssText.append(str(style))

    return cssText
    pass

def isCSStext(text):
    flag = False
    texts = text.splitlines()
    for txt in texts:
        if txt.startswith('.'):
            return True
    return flag

def getValueOfClass(cssTexts):
    classDict = {}
    for cssText in cssTexts:
        sheet=cssutils.parseString(cssText.replace('<style type="text/css">','').replace('</style>',''))
        for rule in sheet:
            try:
                if rule.selectorText.startswith('.x'):
                    for property in rule.style:
                        if property.name == 'left':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('.h'):
                    for property in rule.style:
                        if property.name == 'height':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('.y'):
                    for property in rule.style:
                        if property.name == 'bottom':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('.fs'):
                    for property in rule.style:
                        if property.name == 'font-size':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('._'):
                    for property in rule.style:
                        if property.name == 'width':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
            except:
                pass
        # print('class dict = ' + str(classDict))
    return classDict

def getClassName(listOfClass, symbol):
    for item in listOfClass:
        if item.startswith(symbol):
            return item
    return None

# get the longest inserted white space
def getLongestWS(node, classDict):
    lgtWS = 0
    spans = node.find_all('span')
    # print('node = '+str(node))
    for span in spans:
        # print('span = '+str(span))
        for item in span['class']:
            # print('class = '+str(item))
            if item in classDict:
                # print('value = '+str(classDict[item]))
                if classDict[item]>lgtWS:
                    lgtWS = classDict[item]
    # print('lgtws = '+str(lgtWS))
    return lgtWS

# return a list of page div
def getSoup(path):
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(str(htmlhandle), 'html.parser').find(name='div', id='page-container').find_all(recursive=False)
    # print('num of children soup = '+ str(len(soup)))
    return soup

# convert list of class to a dic of class
# class = ['t', 'm0', 'x12', 'h9', 'y5a', 'ff2', 'fs3', 'fc0', 'sc0', 'ls0', 'ws0']
def getDicOfClass(listOfClass):
    dicOfClass ={}
    for item in listOfClass:
        if item.startswith('x'):
            dicOfClass['left']=item
        if item.startswith('h'):
            dicOfClass['height']=item
        if item.startswith('y'):
            dicOfClass['bottom']=item
        if item.startswith('fs'):
            dicOfClass['font-size']=item
    return dicOfClass

def hasAttX(node, X):
    classList = node['class']
    for att in classList:
        if att.startswith(X):
            return True
    return False

# page is list of line, line is list of txtnodeDict
# key is the key in txtNodeDict
# 按整篇计算base value
def getBaseValue(pages, key):
    countKey = {}
    for page in pages:

        for node in page:
            if key in node:
                value = node[key]
                if value not in countKey:
                    countKey[value] = 1
                else:
                    countKey[value] = countKey[value] + 1
    return max(countKey, key=countKey.get)

def insertNodeToLine(line, txtNode):
    flag = False   #false indicate txtNode not inserted,  True indicate inserted
    tempLine = []
    if len(line)==0:
        tempLine.append(txtNode)
        return tempLine
    for node in line:
        if node['absX'] < txtNode['absX'] and flag==False:
            tempLine.append(deepcopy(node))
        elif node['absX'] > txtNode['absX'] and flag==False:
            tempLine.append(deepcopy(txtNode))
            tempLine.append(deepcopy(node))
            flag = True
        else:
            tempLine.append(deepcopy(node))
    return tempLine


def printPages(pages):
    for page in pages:
        for item in page:
            print('item = '+str(item))





