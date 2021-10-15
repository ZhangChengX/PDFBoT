
from flask import Flask, flash, request, redirect, render_template
import config

import os

import wget
import subprocess
from extractTextFromHTML import getTextFromHTML
from extractTextFrom2colHTML import getTextFrom2HTML

import pikepdf


from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__,template_folder='templates',static_url_path='/static')

app.secret_key = config.secret_key
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH


@app.route('/pdfbot')
def pdfbotEX():
	return render_template('upload.html')


@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print('file name = '+str(filename))
			abPath = os.path.join(os.getcwd(),app.config['UPLOAD_FOLDER'])
			file.save(os.path.join(abPath, filename))
			flash('File successfully uploaded')
			redirectURL = '/pdftohtml/'+str(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			htmlFilePath = pdftohtml_test(str(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
			text =  getTextFrom2HTML(htmlFilePath)


			print('redirect url = '+str(redirectURL))
			print('text == '+str(text))

			return render_template('render_text.html', text=text)

			# return redirect(redirectURL)
		else:
			flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
			return redirect(request.url)

@app.route('/pdftohtml_test/<path:subpath>')
def pdftohtml_test(subpath):
	# for test
	filePath = subpath
	# unlock pdf
	pdf=pikepdf.open(filePath)
	unlockedFile = filePath.replace(' ','_').replace('-','_').replace('.pdf','_unlocked.pdf')
	pdf.save(unlockedFile)
	filePath = unlockedFile
	fileName = os.path.basename(filePath)
	print('file name = '+str(fileName))

	if not os.path.exists('/' + filePath.replace('.pdf', '')):
		commandtemp = 'mkdir ' + filePath.replace('.pdf', '')
		subprocess.call(commandtemp, shell=True)


	command = 'pdf2htmlEX --zoom 1.3 --embed fi ' + filePath + ' --dest-dir '  + filePath.replace(
		'.pdf', '')
	print('command 002 = ' + str(command))
	process = subprocess.call(command, shell=True)
	htmlFilePath = filePath.replace('.pdf', '')+"/"+fileName.replace('.pdf', '.html')
	print('html file path = ' + str(htmlFilePath))


	return htmlFilePath

@app.route('/downloadPDFtest/<path:subpath>')
def downloadPDF(subpath):
	testURL = 'https://www.aclweb.org/anthology/P15-1109.pdf'
	fileName = os.path.basename(subpath)
	downloadedPDFpath = 'output/tempOutput/'+str(fileName).replace('(','_').replace(')','_')
	inputfilePath = subpath
	currDir = os.getcwd()
	outputfile = str(currDir)+'/'+downloadedPDFpath
	wget.download(subpath,outputfile)
	return downloadedPDFpath



@app.route('/convertPDFtoHTML/<path:subpath>')
def convertPDFtoHTML(subpath):
	filePath = subpath
	# download the pdf file and clean the file name
	filePath = downloadPDF(subpath)
	print('file path pikepdf = ' + str(filePath))

	# unlock pdf
	pdf=pikepdf.open(filePath)
	unlockedFile = filePath.replace(' ','_').replace('-','_').replace('.pdf','_unlocked.pdf')
	pdf.save(unlockedFile)
	filePath = unlockedFile
	print('file path 02 = ' + str(filePath))

	fileName = os.path.basename(filePath)
	print('file name = '+str(fileName))

	if not os.path.exists('/' + filePath.replace('.pdf', '')):
		commandtemp = 'mkdir ' + filePath.replace('.pdf', '')
		subprocess.call(commandtemp, shell=True)

	command = 'pdf2htmlEX --zoom 1.3 --embed fi ' + filePath + ' --dest-dir '  + filePath.replace(
		'.pdf', '')
	process = subprocess.call(command, shell=True)
	htmlFilePath = filePath.replace('.pdf', '')+"/"+fileName.replace('.pdf', '.html')
	print('html file path = ' + str(htmlFilePath))
	return htmlFilePath


@app.route('/pdf2htmlEX/<path:subpath>')
# @app.route('/<path:subpath>')
def getContext(subpath):
	print('subpath = '+str(subpath))
	# convert pdf to html and return the path of html file
	htmlFilePath = convertPDFtoHTML(subpath)
	return htmlFilePath

@app.route('/pdftotext/<path:subpath>')
def pdftotext(subpath):
	print('subpath = '+str(subpath))
	htmlFilePath = convertPDFtoHTML(subpath)
	text = getTextFromHTML(htmlFilePath)
	string = ''
	for key in text:
		string = string+'\n\n'+text[key]
	return string.replace('  ',' ')

# auto = "single", "double", "auto"
@app.route('/pdftotextAuto/<auto>/<path:subpath>')
def pdftotextAuto(auto, subpath):
	print('subpath = ' + str(subpath))
	# subpath= 'testPDF/single/01.pdf'
	# subpath = 'testPDF/double/01.pdf'
	htmlFilePath = convertPDFtoHTML(subpath)
	text = getTextFrom2HTML(htmlFilePath, auto=auto)
	print('text 00 = '+str(text))
	string = ''
	for txt in text:
		print('txt = '+str(txt))
		string = string + '\n\n' + txt
	return string.replace('  ', ' ')



if __name__ == '__main__':
   app.run()