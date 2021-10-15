from bs4 import BeautifulSoup
import bs4
# html_content00 = '<div class="t m0 x6 h6 yb ff2 fs2 fc0 sc0 ls0 ws0" id="90">PDF documents<span class="_ _7" id="91"> </span>w<span class="_ _2" id="92"></span>ould<span class="_ _7" id="93"> </span>often mix<span class="_ _7" id="94"> </span>body<span class="_ _7" id="95"> </span>and<span class="_ _7" id="96"> </span>nonbody<span class="_ _7" id="97"> </span>texts. W<span class="_ _2" id="98"></span>e<span class="_ _7" id="99"> </span>de<span class="_ _2" id="100"></span>vise<span class="_ _7" id="101"> </span>and<span class="_ _7" id="102"> </span>implement<span class="_ _7" id="103"> </span>a<span class="_ _7" id="104"> </span>system<span class="_ _7" id="105"> </span>called PDFBoT</div>'
html_content01 = '<div class="t m0 x9 h8 y9f ff5 fs4 fc0 sc0 ls0 ws0" id="1179">(2)<span class="_ _0" id="1180"> </span>P<span class="_ _2" id="1181"></span>age<span class="_ _4" id="1182"> </span>structure.<span class="_ _13" id="1183"> </span><span class="ff2" id="1184">Each<span class="_ _0" id="1185"> </span>page<span id="1186">  test text01  </span>starts<span class="_ _0" id="1187"> </span>with<span class="_ _4" id="1188"> </span>a<span class="_ _0" id="1189"> </span>page</span></div>'
html_content02 = '<div class="t m0 x5 h6 y7 ff2 fs2 fc0 sc0 ls0 ws0" id="50">Abstract:</div>'
# soup = BeautifulSoup(html_content00, "html.parser")
soup01= BeautifulSoup(html_content02,"html.parser").contents[0]

for child in soup01.recursiveChildGenerator():
    if type(child) is bs4.element.NavigableString and str(child).strip() != '':
        # if str(child).strip() != '':
        print('node = '+str(child.strip()))
        child.replace_with('hello')
print('soup = '+str(soup01))




