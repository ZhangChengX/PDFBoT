#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import cssutils
from copy import deepcopy
from tool.tool import isValidParagraph, isValidtext


# check if text is a valid css text
def isCSStext(text):
    flag = False
    texts = text.splitlines()
    for txt in texts:
        if txt.startswith('.'):
            return True
    return flag

# return a list of css
def getCSStext(path):
    cssText = []
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
            except:
                pass
        # print('class dict = ' + str(classDict))
    return classDict

# return a list of page div
def getSoup(path):
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(str(htmlhandle), 'html.parser').find(name='div', id='page-container')
    # print('num of children soup = '+ str(len(soup)))
    return soup

#calculate how many children tag have
def numOfTextTag(soup):
    num = 0
    for item in soup:
        if len(item['class']) == 11:
            num = num+1
    return num


#store pages in the form of class of each div
# input soup
# return pagesDivClasses if a list of each page in form of list of class of each div
def getPagesDivClass(inputSoup, classDict):
    soup = inputSoup.find_all(recursive=False)
    pagesDivClasses = []  # list of pageDivClasses
    pageDivClasses = []  # list of list of each div classes
    divDict = {}
    totalPages = len(soup)

    for item in soup:
        item.find_all('div', recursive=False)
        pageID = item['data-page-no']
        print('page id = '+str(pageID))
        for subItem in item:
            if len(subItem['class']) >= 4:
                print('num of text div = '+str(numOfTextTag(subItem)))
                if numOfTextTag(subItem)>0:
                    for subItem01 in subItem:
                        if len(subItem01['class']) == 11 and len(subItem01.getText().strip())>1:
                            divDict['text']=subItem01.getText()
                            divDict['pageID']= pageID
                            divDict['totalPages'] = totalPages
                            divDict['fs'] = classDict[getClassName(subItem01['class'],'fs')]
                            divDict['x'] = classDict[getClassName(subItem01['class'], 'x')]
                            divDict['y'] = classDict[getClassName(subItem01['class'], 'y')]
                            pageDivClasses.append(deepcopy(divDict))
                            divDict.clear()
                else:
                    for subItem01 in subItem:
                        if numOfTextTag(subItem01)==0:
                            continue
                        for item02 in subItem01:
                            if len(item02['class']) == 11 and len(item02.getText().strip()) > 1:
                                divDict['text'] = item02.getText()
                                divDict['pageID'] = pageID
                                divDict['totalPages'] = totalPages
                                divDict['fs'] = classDict[getClassName(item02['class'], 'fs')]
                                divDict['x'] = classDict[getClassName(item02['class'], 'x')]
                                divDict['y'] = classDict[getClassName(item02['class'], 'y')]
                                print('div dict test = '+str(divDict))
                                pageDivClasses.append(deepcopy(divDict))
                                divDict.clear()

        # pagesDivClasses.append(deepcopy(calculateLineSpace(pageDivClasses)))
        for divDictitem in pageDivClasses:
            print('divDictitem = '+str(divDictitem))
        pagesDivClasses.append(calFreFSandLineSpace(calculatePreSpace(sortDivInPage(pageDivClasses,classDict))))
        pageDivClasses.clear()


    cleanPagesDivClasses = []
    # remove empty page,  the page without text div
    for pageItem in pagesDivClasses:
        if len(pageItem)>0:
            cleanPagesDivClasses.append(deepcopy(pageItem))

    # return pagesDivClasses
    return cleanPagesDivClasses

# calculate the space between the div and this div's previous div.
def calculatePreSpace(page):
    newPage = {}
    lastBottom = 0
    for item in page:
        index = item
        DivDict = page[index]
        # print('bottom = '+str(lastBottom))
        if item == 0 :
            preSpace = lastBottom
            lastBottom = DivDict['y']
        else:
            preSpace = abs(lastBottom - DivDict['y'])
            lastBottom=DivDict['y']
        DivDict['preSpace']=preSpace
        newPage[item]=deepcopy(DivDict)
    return newPage

# calculate most frequent font-size and lineSpace
def calFreFSandLineSpace(page):
    newPage={}
    for key in page:
        divDict = page[key]
        divDict['lineSpace'] = getMostFreValueOfKey(page, 'preSpace')
        divDict['freqFS'] = getMostFreValueOfKey(page,'fs')
        newPage[key]=deepcopy(divDict)

    return newPage

# calculate base/macro font-size and base line space
def calBaseFSandLineSpace(pages):
    newPages = []
    baseFS = 0
    baseLineSpace =0
    countFS={}
    countLineSpace = {}
    for page in pages:
        fs = page[0]['freqFS']
        ls = page[0]['lineSpace']
        if fs not in countFS:
            countFS[fs] = 1
        else:
            countFS[fs] = countFS[fs]+1
        if ls not in countLineSpace:
            countLineSpace[ls] = 1
        else:
            countLineSpace[ls] = countLineSpace[ls]+1
    baseLineSpace = max(countLineSpace, key=countLineSpace.get)
    baseFS = max(countFS, key=countFS.get)

    for page in pages:
        for key in page:
            page[key]['macroFS'] = baseFS
            page[key]['macroLineSpace'] = baseLineSpace
        newPages.append(deepcopy(page))
    return newPages




# input page is a list of divDict
# return a newPage, it is a dictionary,
# newPage{  '1': 'divDict01'
#           '2': 'divDict02'
#           '3': 'divDict03'
#           ...........
#        }
def sortDivInPage(page, classDict):
    newPage={}
    i = 0

    while page:
        tempDivDict = page[0]
        frontIndex = 0
        # print('length of page = ' + str(len(page)))
        for index, divDict in enumerate(page):
            if tempDivDict['y']>=divDict['y']:
                pass
            else:
                tempDivDict = divDict
                frontIndex = index
        page.remove(tempDivDict)
        # del page[frontIndex]
        # print('temp div dict = '+str(tempDivDict))
        newPage[i]=deepcopy(tempDivDict)
        i=i+1
    return newPage


# page is a dictionary of  value is divdict
def getMostFreValueOfKey(page, key):
    if len(page)==0:
        return 0
    if len(page)==1:
        return page[0][key]
    countKey = {}
    for index in page:
        value = page[index][key]
        if key == 'preSpace' and value<1:
            continue
        if value not in countKey:
            countKey[value] = 1
        else:
            countKey[value] = countKey[value]+1

    return max(countKey, key=countKey.get)

# get text x(left of new paragraph) of page
# page is a list of class of the div in that page
def getSecondMostX(page):
    countX = {}
    for divDict in page:
        fs = getClassName(divDict['class'], 'x')
        if fs not in countX:
            countX[fs] = 1
        else:
            countX[fs] = countX[fs]+1
    maxX= max(countX, key=countX.get)
    del countX[maxX]
    return max(countX, key=countX.get)

# get the full name of specific class by the first few letters
# if you want get the fs(font-size), pass in symbol = fs
def getClassName(listOfClass, symbol):
    for item in listOfClass:
        if item.startswith(symbol):
            return item
    return None

# get selection string
def getSelectStr(divDict, tag):
    selectStr=tag
    for item in divDict['class']:
        selectStr=selectStr+'.'+str(item)
    return selectStr


def getTextFromHTML(htmlFilePath):
    text=[]
    # para=''
    para={}

    # get the css in html
    cssText = getCSStext(htmlFilePath)
    # parse css text to dictionary
    classDict = getValueOfClass(cssText)
    # print('class dict = '+ str(classDict))

    soup = getSoup(htmlFilePath)
    print('length of soup = ' + str(len(soup)))

    #store pages in the form of class of each div
    pagesDivClasses = getPagesDivClass(soup, classDict)
    pagesDivClasses = calBaseFSandLineSpace(pagesDivClasses)

    preDivFS = 0
    preDivText = ''

    for index, page in enumerate(pagesDivClasses):
        print('---------------------------------'+"index = "+str(index)+'-----------------------------------------')
        pageFS = page[0]['macroFS']
        lineSpace = page[0]['macroLineSpace']
        print('font size = '+str(pageFS))
        print('line space = '+str(lineSpace))

        i = 0
        for key in page:
            if page[key]['fs'] >= pageFS-2 and len(page[key]['text'].strip())>1:

                divText_temp = page[key]['text']
                divText = divText_temp
                # check if it is first text line in page
                if str(i)=='0':
                    i = i+1
                    print('i ====== 0')
                    if page[key]['fs']>pageFS+5:
                        text.append(deepcopy(para))
                        # para = divText
                        print('para 01 = '+str(para))
                        para.clear()
                        para['text']=divText
                        para['fs']= deepcopy(page[key]['fs'])
                        para['macroFS'] = deepcopy(page[key]['macroFS'])


                    elif len(preDivText.strip())<=2:
                        print('len = '+str(len(preDivText.strip())))
                        text.append(deepcopy(para))
                        print('para 02 = ' + str(para))
                        # para = divText
                        para.clear()
                        para['text'] = divText
                        para['fs'] = deepcopy(page[key]['fs'])
                        para['macroFS'] = deepcopy(page[key]['macroFS'])
                    elif preDivText.strip()[-1].isalpha():
                        print('last letter = '+str(preDivText.strip()[-1]))
                        # para = para + ' ' + divText
                        if para['text'].endswith('-'):
                            para['text'] = deepcopy(para['text'][:-1]) + divText
                        else:
                            para['text'] = deepcopy(para['text'])+ ' ' + divText
                    else:
                        text.append(deepcopy(para))
                        # para = divText
                        para.clear()
                        para['text'] = divText
                        para['fs'] = deepcopy(page[key]['fs'])
                        para['macroFS'] = deepcopy(page[key]['macroFS'])
                else:
                    # if classDict[getClassName(page['class'], 'x')]==secondMostX:
                    if page[key]['preSpace'] > page[key]['macroLineSpace'] + 2 and abs(
                            page[key]['fs'] - page[key]['macroFS']) < 5:
                        text.append(deepcopy(para))
                        print('para 04 = ' + str(para))
                        # para = divText
                        para.clear()
                        para['text'] = divText
                        para['fs'] = deepcopy(page[key]['fs'])
                        para['macroFS'] = deepcopy(page[key]['macroFS'])

                    elif abs(page[key]['fs'] - preDivFS) > 5:  #
                        text.append(deepcopy(para))
                        # para = divText
                        print('para 05 = ' + str(para))
                        para.clear()
                        para['text'] = divText
                        para['fs'] = deepcopy(page[key]['fs'])
                        para['macroFS'] = deepcopy(page[key]['macroFS'])
                    else:
                        # para = para + ' ' + divText
                        if para['text'].endswith('-'):
                            para['text'] = deepcopy(para['text'][:-1]) + divText
                        else:
                            para['text'] = deepcopy(para['text'])+ ' ' + divText

                        pass
                    pass

                preDivFS = deepcopy(page[key]['fs'])
                preDivText = deepcopy(page[key]['text'])
    text.append(deepcopy(para))

    newText={}
    tempPara={}
    i=0
    outputfile = open('output/outputFile.txt', 'w')
    # for page in listOfpage:
    for pg in text:
        if 'text' not in pg.keys():
            continue
        if not isValidtext(pg['text']):
            tempPara['text']=pg['text']
            tempPara['fs'] = pg['fs']
            tempPara['macroFS']= pg['macroFS']
            tempPara['type'] = 'noise'
        # print('paragraph = ' + str(pg))
        elif abs(pg['fs']-pg['macroFS'])>6:
            tempPara['text'] = '<title>'+pg['text']+'</title>'
            tempPara['fs'] = pg['fs']
            tempPara['macroFS'] = pg['macroFS']
            tempPara['type'] = 'title'
            print('pg  title = '+str(tempPara))
            newText[i] = deepcopy(tempPara['text'])
            i = i + 1
        elif not isValidParagraph(pg['text']):
            tempPara['text'] = pg['text']
            tempPara['fs'] = pg['fs']
            tempPara['macroFS'] = pg['macroFS']
            tempPara['type'] = 'noise'
        else:
            tempPara['text'] = pg['text']
            tempPara['fs'] = pg['fs']
            tempPara['macroFS'] = pg['macroFS']
            tempPara['type'] = 'normal'
            newText[i] = deepcopy(pg['text'])
            i=i+1

    for key in newText:

        outputfile.write(newText[key]+ '\n')
        outputfile.write(' -------------\n')
    outputfile.close()
    return newText






if __name__ == '__main__':
    pass