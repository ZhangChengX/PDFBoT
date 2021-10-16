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
Command to run PDFBoT API on local computer
```
python3 main.py
```
Once the builtin server is launched, head over to [http://127.0.0.1:5000/](http://127.0.0.1:5000/). Follow the instrucation to upload PDF file to extract text. 
