
CKEDITOR.plugins.add( 'zc_wordcount', {
	requires: 'dialog',
	icons: 'count',
	init: function( editor ) {
		//Plugin logic goes here.
		var label = "Word count";
		if (editor.langCode == "zh-cn") {
			label = "字数统计";
		}

		editor.addCommand( 'wordcount', {
			exec: function( editor ) {

				var text = CKEDITOR.instances[editor.name].getData();
				text = $(text).text().replace(/\s/g, '');
				// console.log(text);
				// console.log(text.length);
				/* 
				 * TODO !!!
				 * HOW TO add dynamic text on dialog ???
				 */
				alert(label + ": " + text.length);
				// var dialogObj = new CKEDITOR.dialogCommand( 'wordcountDialog' )
				// var dialogObj = new CKEDITOR.dialog( editor, 'wordcountDialog' );
				// dialogObj.show();

			}
		});

		// editor.addCommand( 'wordcount', new CKEDITOR.dialogCommand( 'wordcountDialog' ) );

		editor.ui.addButton( 'Wordcount', {
			label: label,
			command: 'wordcount',
			toolbar: 'others,8'
		});

		// CKEDITOR.dialog.add( 'wordcountDialog', function( editor, text ) {
		//     return {
		//         title: label,
		//         minWidth: 200,
		//         minHeight: 100,
		//         contents: [
		//             {
		//                 id: 'tab-basic',
		//                 label: 'Basic Settings',
		//                 elements: [
		// 	                {
		// 	                	type: 'html',
		// 	                	html: '<div>' + label + ': ' + text.length + '</div>'
		// 	                }
		//                 ]
		//             }
		//         ],
		//         onShow: function() {
		//         	text = CKEDITOR.instances[editor.name].getData();
		//         },
		//         buttons: [ CKEDITOR.dialog.okButton ]
		//     };
		// });

	}
	// onLoad: function() {

	// 			// var text = CKEDITOR.instances[editor.name].getData();
	// 			var text = CKEDITOR.instances["reading-area"].getData();
				
	// 			// var text = editor._.data;
	// 			text = text.replace(/<br>/g,"\n");
	// 			text = text.replace(/<p>/g," ");
	// 			text = text.replace(/<\/p>/g,"\n");
	// 			text = text.replace(/<span class=\'font-color-[0-9]+\'>/g, "");
	// 			text = text.replace(/<\/span>/g,"");
	// 			text = text.replace(/<!--.*-->/g,"");
	// 			console.log(text.length);
	// 			// editor.addCommand( 'wordcount', new CKEDITOR.dialogCommand( 'wordcountDialog' ) );
 //    }
});