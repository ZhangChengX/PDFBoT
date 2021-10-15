
import re
# check if string ends with letter or number,
# if yes, then string is not paragraph
def isValidtext(str):
    # if text doesn't contain letter, then it is not a valid paragraph
    if not re.search('[a-zA-Z]', str):
        return False
    elif len(str.strip())<=3:
        return False
    else:
        return True

def isValidParagraph(text):
    if len(text.strip())<=3:
        return False
    # print('last char = ' + str(text.strip()[-1]))
    if text.strip()[-1].isdigit() or text.strip()[-1].isalpha() or text.strip()[-1]==')':
        return False
    else:
        return True

# calculate the number of item in the interval
def numItemInInterval(list, start, end):
    count=0
    for item in list:
        if item>=start and item<end:
            count=count+1

    # print('['+str(start)+','+str(end)+')\t'+str(count))
    return count
