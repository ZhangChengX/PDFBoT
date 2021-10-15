
CKEDITOR.plugins.add( 'zc_saveas', {
	icons: 'save',
	init: function( editor ) {
		//Plugin logic goes here.
		var label = "Save as docx file";
		if (editor.langCode == "zh-cn") {
			label = "另存为docx文件";
		}

		editor.addCommand( 'saveas', {
			exec: function( editor ) {

				var text = CKEDITOR.instances[editor.name].getData();
				text = text.replace(/class="font-color-0"/g, 'style="color:' + $(".font-color-0").css("color") + ';font-weight: bold;"');
				text = text.replace(/class="font-color-1"/g, 'style="color:' + $(".font-color-1").css("color") + '"');
				text = text.replace(/class="font-color-2"/g, 'style="color:' + $(".font-color-2").css("color") + '"');
				text = text.replace(/class="font-color-3"/g, 'style="color:' + $(".font-color-3").css("color") + '"');
				text = text.replace(/class="font-color-4"/g, 'style="color:' + $(".font-color-4").css("color") + '"');
				text = text.replace(/class="font-color-5"/g, 'style="color:' + $(".font-color-5").css("color") + '"');
				text = text.replace(/class="font-color-6"/g, 'style="color:' + $(".font-color-6").css("color") + '"');
				text = text.replace(/class="font-color-7"/g, 'style="color:' + $(".font-color-7").css("color") + '"');
				text = text.replace(/class="font-color-8"/g, 'style="color:' + $(".font-color-8").css("color") + '"');
				text = text.replace(/class="font-color-9"/g, 'style="color:' + $(".font-color-9").css("color") + '"');
				text = text.replace(/class="font-color-10"/g, 'style="color:' + $(".font-color-10").css("color") + '"');
				text = '<!doctype html> <body>' + text + '</body> </html>';
				console.log(text);
				var converted = htmlDocx.asBlob(text);
				saveAs(converted, 'document.docx');

				// generate txt
				// // var text = editor._.data;
				// text = text.replace(/<br>/g,"\n");
				// text = text.replace(/<p>/g," ");
				// text = text.replace(/<\/p>/g,"\n");
				// text = text.replace(/<span class=\'font-color-[0-9]+\'>/g, "");
				// text = text.replace(/<\/span>/g,"");
				// text = text.replace(/<!--.*-->/g,"");

				// var filename = "data.txt";
				// var pom = document.createElement('a');
				// pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
				// pom.setAttribute('download', filename);
				// if (document.createEvent) {
				// 	var event = document.createEvent('MouseEvents');
				// 	event.initEvent('click', true, true);
				// 	pom.dispatchEvent(event);
				// } else {
				// 	pom.click();
				// }

			}
		});

		editor.ui.addButton( 'Saveas', {
			label: label,
			command: 'saveas',
			toolbar: 'others2,10'
		});
	}
});