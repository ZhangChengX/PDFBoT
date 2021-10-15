$(document).foundation();

var server_api = "/api";
var en_to_en_api = "https://glosbe.com/gapi/translate";
var qg_cn_api = "http://72.93.242.201:8581/";
var qg_url = "qg";
var session_id = "";
var sentence_rank; // s[0]:order, s[1]:sentence, s[2]:score, s[3]:color
var paragraph_template;
var ratio_record = [0];
var algorithm = "semantic";
var article_structure = 3;
var timer_interval;

var show_text_by_ratio = function(sentence_rank, ratio, element) {
	// empty number of sentences
	$("#reading .numberofsentences").val("");

	// get the top r sentences
	var tmp_array = [];
	for (var i = 0; i < sentence_rank.length; i++) {
		if (sentence_rank[i][3] < ratio) {
			tmp_array.push(sentence_rank[i]);
		}
	}
	// sort by sequence order
	tmp_array.sort(function(a, b) {
		return a[0] - b[0];
	});
	// Filter unexpected characters in paragraph template
	if (95 > ratio) {
		tmp_paragraph_template = paragraph_template.replace(/[^<p><\/p>(\[#\d+\])\n\r ]/g, "");
	} else {
		tmp_paragraph_template = paragraph_template;
	}
	// merge paragraph and sentences together
	var text = merge_paragraph_sentences(tmp_paragraph_template, tmp_array);
	// strip tags
	text = strip_tags(text);
	// show
	element.html(text);
	// console.log(tmp_array);
	// console.log(text);
	get_keywords();
};

var show_text_by_number_of_sentences = function(sentence_rank, numberofsentences, element) {
	// reset ratio
	ratio_record = [0];
	$("#reading .ratio").val(0);
	// reset hotmap and divide into 10
	show_heat_map([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], $("#heat-map"));
	// var tmp_array = [0];
	// for (var i = 1; i <= numberofsentences; i++) {
	// 	if (i > 10) { 
	// 		break; 
	// 	}
	// 	tmp_array.push(i * 10);
	// }
	// show_heat_map(tmp_array, $("#heat-map"));

	// get n sentences
	var tmp_array = [];
	if (numberofsentences > sentence_rank.length) {
		numberofsentences = sentence_rank.length;
	}
	for (var i = 0; i < numberofsentences; i++) {
		tmp_array.push(sentence_rank[i]);
	}
	// sort by sequence order
	tmp_array.sort(function(a, b) {
		return a[0] - b[0];
	});
	// merge paragraph and sentences together
	var text = merge_paragraph_sentences(paragraph_template, tmp_array);
	// strip tags
	text = strip_tags(text);
	// show
	element.html(text);
	// console.log(tmp_array);
	// console.log(text);
	get_keywords();
};

var merge_paragraph_sentences = function(paragraph_template, sentences) {
	// merge paragraph and sentences together
	var text = paragraph_template;
	for (var i = 0; i < sentences.length; i++) {
		if (ratio_record.length > 1) {
			// color divide according to ratio_record
			for (var j = 1; j < ratio_record.length; j++) {
				// console.log("j=" + j + " | " + ratio_record[j-1] + "<=" + sentences[i][3] + "<" + ratio_record[j]);
				if (sentences[i][3] >= ratio_record[j-1] && sentences[i][3] < ratio_record[j]) {
					var sentence = "<span class='font-color-" + (j - 1) + "'>" + sentences[i][1] + "</span>";
				}
			}
		} else {
			// divide into 10, old version
			var sentence = "<span class='font-color-" + Math.round(sentences[i][3]/10) + "'>" + sentences[i][1] + "</span>";
		}
		text = text.replace("[#" + sentences[i][0] + "]", sentence);
	}
	return text;
};

var strip_tags = function(text) {
	// strip tags
	text = text.replace(/\[#\d+\][ \xc2\xa0]*[。！；？!?;]*/g, ""); // match [#id] or [#id]。or [#id] 。
	// text = text.replace(/\[#\d+\] [。！；？!?;]*/g, ""); // match [#id] 。
	// text = text.replace(/<p> *<\/p>/g, ""); // match <p></p> or <p>  </p> 
	return text.replace(/<p>[ \xc2\xa0]*<\/p>/g, ""); // match <p></p> or <p>  </p> or <p> 特殊空格 </p>
};

var show_heat_map = function(ratio_record, element) {
	var html = "";
	for (var i = 1; i < ratio_record.length; i++) {
		html += "<div> " + ratio_record[i] + "% <span class='font-color-" + (i-1) + "'>&#9724;&#9724;&#9724;&#9724;&#9724;&#9724;</span></div>"
	}
	element.html(html);
};

var show_keyword_list = function(keywords, element) {
	var html = "";
	var kw_length = keywords.length;
	for (var i = 0; i < kw_length; i++) {
		html += "<span class='font-size-" + Math.round(1 / kw_length * i * 10) + 
				"' title='" + keywords[i][1] + "'>" + 
				keywords[i][0] + "</span> ";
	}
	element.html(html);
};

var show_title_list = function(sentence_rank, element) {
	var title_list = [];
	for (var i = 0; i < sentence_rank.length; i++) {
		var title_l = sentence_rank[i][1].indexOf("<b>");
		var title_r = sentence_rank[i][1].indexOf("</b>");
		if ( (-1 != title_l) && (-1 != title_r) ) {
			// The length of "<b>" is 3
			title_list.push( sentence_rank[i][1].substr(title_l + 3, title_r - 3) );
		}
	}
	var title_html = "";
	for (var i = 0; i < title_list.length; i++) {
		title_html = title_html + "<li><a href=\"javascript:void();\">" + title_list[i] + "</a></li>";
	}
	element.html(title_html);
};

var sentence_preprocessing = function(sentence_rank) {
	// sort by rank score
	sentence_rank.sort(function(a, b) {
		// return b[2] - a[2]; // for score, 3, 2, 1, ...
		return a[2] - b[2]; // for ranking order, 1, 2, 3, ...
	});
	// add color
	for (var i = 0; i < sentence_rank.length; i++) {
		// // add color label, divide sentence length into 10
		// sentence_rank[i].push(Math.round(1 / sentence_rank.length * i * 10));
		// add color label, divide sentence length into 100
		sentence_rank[i].push(1 / sentence_rank.length * i * 100);
	}
};

var request_finished = function(data) {
	if (null == data) {
		return false;
	}
	if ("" == data["error"]) {
		// Redirect to PDF2HTML
		if ("URL" in data) {
			window.location.href = data["URL"];
		}
		$("#request").addClass("hide");
		paragraph_template = data["paragraph_template"];
		sentence_rank = data["sentences"];
		session_id = data["session_id"];

		generate_qg_link(session_id);

		var ratio = parseInt($("#request .ratio").val());
		sentence_preprocessing(sentence_rank);
		show_text_by_ratio(sentence_rank, ratio, $("#reading-area"));
		show_title_list(sentence_rank, $("#title-list ul"));
		show_heat_map(ratio_record, $("#heat-map"));
		$("#reading .ratio").val($("#request .ratio").val());
		$("#reading").removeClass("hide");
	} else {
		alert(data["error"]);
	}
};

var get_sentences = function() {
	switch_btn("processing-btn");
	var text = $("#request .text").val();
	var ratio = $("#request .ratio").val() / 100;
	var parameters = { text: text, ratio: ratio, lang: lang, session_id: session_id, algorithm: algorithm, article_structure: article_structure };
	$.ajax({
		dataType: "json",
		url: server_api + "/sentences",
		type: "POST",
		data: parameters,
		success: function(data) {
			request_finished(data);
			switch_btn("submit-btn");
		},
		error: function() {
			alert("Error: Service unavailable or connection refused.");
			switch_btn("submit-btn");
		}
	});
};

var file_upload = function() {
	switch_btn("processing-btn");
	$(".file-upload-wrapper form").ajaxSubmit({
		url: server_api + "/file",
		type: "POST",
		data: { 
			lang: lang, 
			// session_id: session_id,
			ratio: $("#request .ratio").val() / 100,
			algorithm: algorithm,
			article_structure: article_structure,
			is_multi_column: $("#multi-column").prop('checked')
		},
	    beforeSend: function() {
	        var percentVal = "0%";
	        $(".progress .bar").width(percentVal)
	        $(".progress .percent").html(percentVal);
	        $(".progress").removeClass("hide");
	    },
	    uploadProgress: function(event, position, total, percentComplete) {
	        // var percentVal = percentComplete + '%';
	        var percentVal = percentComplete/10 + '%';
	        $(".progress .bar").width(percentVal)
	        $(".progress .percent").html(percentVal);
	        if (100 == percentComplete) {
	        	console.log("File upload 100% finished.");
	        	timer_interval = setInterval(update_progress_file_upload, 500);
	        }
	    },
	    success: function() {
	    	// console.log("File upload status: success.");
	        // var percentVal = '100%';
	        var percentVal = '10%';
	        $('.bar').width(percentVal)
	        $('.percent').html(percentVal);
	    },
		complete: function(xhr) {
			// console.log("File upload status complete.");
			clearInterval(timer_interval);
			request_finished(xhr.responseJSON);
			switch_btn("submit-btn");
		}
	}); 
};

var update_progress_file_upload = function() {
	var progress = parseInt($('.percent').html().replace('%', '')) + 3;
	if (progress < 86) {
		var percentVal = progress + '%';
		$('.bar').width(percentVal)
		$('.percent').html(percentVal);
	}
};

// var clear_progress_file_upload - function() {
// 	var percentVal = '0%';
// 	$('.bar').width(percentVal)
// 	$('.percent').html(percentVal);
// 	// $(".progress").addClass("hide");
// };

var get_keywords = function() {
	var text = $("#reading-area").text();
	// var ratio = $("#request .ratio").val() / 100;
	var parameters = { text: text, lang: lang, session_id: session_id };
	$.ajax({
		dataType: "json",
		url: server_api + "/words",
		type: "POST",
		data: parameters,
		success: function(data) {
			show_keyword_list(data, $("#keyword-list span.keyword-box"));
		},
		error: function() {
			// alert("Error: Service unavailable or connection refused.");
		}
	});
};

var switch_btn = function(btn_name) {
	if (btn_name == "submit-btn") {
		$("#submit-btn1").removeClass("hide");
		$("#submit-btn2").removeClass("hide");
		$("#submit-btn3").removeClass("hide");
		$("#submit-btn4").removeClass("hide");
		$("#processing-btn").addClass("hide");
	} else {
		$("#submit-btn1").addClass("hide");
		$("#submit-btn2").addClass("hide");
		$("#submit-btn3").addClass("hide");
		$("#submit-btn4").addClass("hide");
		$("#processing-btn").removeClass("hide");
	}
};

var add_ratio_record = function(ratio) {
	var previous_ratio = ratio_record[ratio_record.length-1];
	// new ratio must be greater than the previous ratio
	if (ratio > previous_ratio) {
		// // any ratio can be added if it is the first time, otherwise greater than 10% 
		// if ( previous_ratio == 0 || (ratio - previous_ratio) >= 10 ) {
			ratio_record.push(ratio);
		// }
	}
};

var generate_qg_link = function(session_id) {
	if (lang == "en") {
		$("#qg").attr("href", qg_url + "?lang=" + lang + "&session_id=" + session_id);
	} else { // lang == 'zh'
		$("#qg").attr("href", "javascript:redirect_to_cn_qg()");
	}
	$("#qg-summary").attr("href", "qg-summary?lang=" + lang + "&session_id=" + session_id);
	$("#qg-sat").attr("href", "qg-sat?lang=" + lang + "&session_id=" + session_id);
};

var redirect_to_cn_qg = function() {
	var timestamp = Date.parse(new Date());
	var text = "";
	for (var i = 0; i < sentence_rank.length; i++) {
		text =  text + sentence_rank[i][1] + "\n\n";
	}
	var cnqgdata =  {
		"name": timestamp,
		"content": text
	};
    $.ajax({
        	type: 'POST',
        	url: qg_cn_api + "io",
        	dataType: 'json',
        	data: cnqgdata
        }).done(function(data){
        window.location.href = qg_cn_api + "get?name="+ timestamp
    });
};

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

/* *** Event binding *** */

$("#switch-lang input").change(function() {
	if ( $("#switch-lang #english").is(":checked") ) {
		lang = "en";
		$("span[lang]").languageSwitcher( lang );
		setCookie("lang", lang, 1);
		create_editor('en');
	} else {
		lang = "zh";
		$("span[lang]").languageSwitcher( lang );
		setCookie("lang", lang, 1);
		create_editor('zh-cn');
	}
});

// $("#login-form").submit(function() {
// 	var loginstr = $("#username").val() + $("#password").val();
// 	if (btoa(loginstr) == "cnVyMTIz") {
// 		return true;
// 	} else {
// 		alert("Username or Password is incorrect.")
// 		return false;
// 	}
// });

$("#reading .ratio").change(function() {
	var ratio = parseInt($(this).val());
	if (ratio <= 100) {
		add_ratio_record(ratio);
		show_text_by_ratio(sentence_rank, ratio, $("#reading-area"));
		show_title_list(sentence_rank, $("#title-list ul"));
		show_heat_map(ratio_record, $("#heat-map"));
	}
});

$("#reading .numberofsentences").change(function() {
	var numberofsentences = $("#reading .numberofsentences").val();
	show_text_by_number_of_sentences(sentence_rank, numberofsentences, $("#reading-area"));
});

$("#read-more").click(function() {
	var ratio = parseInt($("#reading .ratio").val());
	if (ratio <= 90) {
		ratio += 10;
	} else if (ratio == 100) {
		return;
	} else {
		ratio = 100;
	}
	$("#reading .ratio").val(ratio);
	add_ratio_record(ratio);
	show_text_by_ratio(sentence_rank, ratio, $("#reading-area"));
	show_title_list(sentence_rank, $("#title-list ul"));
	show_heat_map(ratio_record, $("#heat-map"));
});

$("#submit-btn1, #submit-btn2, #submit-btn3, #submit-btn4").click(function() {
	add_ratio_record(parseInt($("#request .ratio").val()));
	if ($(this).attr("id") == "submit-btn1") {
		article_structure = 1;
	} else if ($(this).attr("id") == "submit-btn2") {
		article_structure = 0;
	} else if ($(this).attr("id") == "submit-btn3") {
		article_structure = 2;
	} else {
		article_structure = 3;
	}
	if ("" == $("#file-upload").val()) {
		get_sentences();
	} else {
		file_upload();
	}
});

$("#file-upload").change(function() {
	$(".file-upload").html($(this).val());
});

$("#reading #return-btn").click(function(){
	sentence_rank = null;
	paragraph_template = null;
	ratio_record = [0];

	$("#file-upload").val("");
	$("#file-upload").prev("label").html("Upload DOCX/PDF/TXT");
	$("#request .progress").addClass("hide");
	$("#request textarea").html("");

	$("#request").removeClass("hide");
	$("#reading").addClass("hide");
});

$("#reading #restart-btn").click(function(){
	ratio_record = [0];
	$("#reading .ratio").val(0);
	$("#reading .numberofsentences").val("");
	// add_ratio_record(ratio);
	// sentence_preprocessing(sentence_rank);
	// show_text_by_ratio(sentence_rank, ratio, $("#reading-area"));
	// show_title_list(sentence_rank, $("#title-list ul"));
	$("#reading-area").html('');
	// show_heat_map(ratio_record, $("#heat-map"));
	$("#heat-map").html('');
	$("#keyword-list span.keyword-box").html('');
	// $("#reading .ratio").val($("#request .ratio").val());
});

// https://github.com/zhangchengx/simple-multi-lang.js
(function($){
  $.fn.languageSwitcher = function(lang) {
    $.each(this, function(index, value) {
      if (lang == $(value).attr("lang")) {
        $(value).css("display", "inline");
      } else {
        $(value).css("display", "none");
      }
    });      
    return this;
  }
}(jQuery));

var cookieLang = getCookie("lang");
if (cookieLang) {
	lang = cookieLang;
	$("span[lang]").languageSwitcher( lang );
	if (lang == "zh") {
		$("#switch-lang input#chinese").prop("checked", true);
	}
}

/* For page opened directly with session_id. DOM ready */
if (window.location.href.split("#!/")[1]) {
	session_id = window.location.href.split("#!/")[1];
	$("#request").addClass("hide");
	$("#return-btn").addClass("hide");
	add_ratio_record(10);
	get_sentences();
}

/* hide #qg-sat link if no session_id */
if (session_id == "") {
	$("#qg-sat").addClass("hide");
}

/* editor */
if (session_id == "") {
	var editor;
	var create_editor = function ( languageCode ) {
		if ( editor ) {
			editor.destroy();
		}
		if (languageCode == "zh") {
			languageCode = 'zh-cn';
		}

		// editor = CKEDITOR.replace( 'reading-area' , {
		// 	language: languageCode
		// });

		var editorElement = CKEDITOR.document.getById( 'reading-area' );
		if (editorElement) {
			editorElement.setAttribute( 'contenteditable', 'true' );
			editor = CKEDITOR.inline( 'reading-area' , {
				language: languageCode
			});
		}
	};
	if ( CKEDITOR.env.ie && CKEDITOR.env.version < 9 ) {
		CKEDITOR.tools.enableHtml5Elements( document );
	}
	create_editor(lang);
}


