# PDFBoT API
PDFBoT is a tool for accurately extracting body text of the article in PDF format.  
## Publications
Please cite the following paper if you are using our tool. Thanks!
* Changfeng Yu, Cheng Zhang, and Jie Wang. 2020. [Extracting Body Text from Academic PDF Documents for Text Mining](https://arxiv.org/abs/2010.12647). In Proceedings of the 12th International Conference on Knowledge Discovery and Information Retrieval (KDIR 2020).
## Environment
MacOS with python3.6+ installed

Dependencies

* pdf2htmlEX
* bs4
* flask

## Usage
### Command to run PDFBoT API on local computer
```
python3 main.py
```
Once the builtin server is launched, head over to [http://127.0.0.1:5000/](http://127.0.0.1:5000/). Follow the instrucation to upload PDF file to extract text. 

### Run the source code to extract the text
step 1 convert the PDF to HTML by the function "pdftohtml_test", in main.py L72. 
* The input is the url of the PDF document.
* The output is the path of the corresponding HTML file.
 
step 2 extract body text from HTML file by the function "getTextFrom2HTML", in extractTextFrom2colHTML.py. 
* The input is the path of the HTML file. 
* The output is the a list of string, each string in the list represents one paragraph of the article in document. 


