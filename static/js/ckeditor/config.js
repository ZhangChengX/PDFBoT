/**
 * @license Copyright (c) 2003-2018, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for a single toolbar row.
	config.toolbarGroups = [
		// { name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		// { name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
		// { name: 'forms', groups: [ 'forms' ] },
		// '/',
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
		{ name: 'links', groups: [ 'links' ] },
		{ name: 'insert', groups: [ 'insert' ] },
		{ name: 'colors', groups: [ 'colors' ] },
		// { name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
		// '/',
		{ name: 'styles', groups: [ 'styles' ] },
		// { name: 'tools', groups: [ 'tools' ] },
		{ name: 'others', groups: [ 'others' ] },
		{ name: 'others2', groups: [ 'others2' ] }
	];

	// The default plugins included in the basic setup define some buttons that
	// are not needed in a basic editor. They are removed here.
	config.removeButtons = 'Strike,Subscript,Superscript,RemoveFormat,CopyFormatting,CreateDiv,BidiLtr,BidiRtl,Language,Anchor,Image,Flash,PageBreak,Iframe,SpecialChar,Smiley,Maximize,ShowBlocks,NewPage,Preview,Templates,Styles,Blockquote,JustifyBlock,Save,Print,Format,Font';

	// Dialog windows are also simplified.
	config.removeDialogTabs = 'link:advanced';

	config.extraPlugins = 'zc_saveas,zc_wordcount';

};

