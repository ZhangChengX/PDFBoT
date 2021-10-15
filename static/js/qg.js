$(document).foundation();

var server_api = "/api";
var session_id = window.location.href.split("session_id=")[1];
var lang = window.location.href.split("lang=")[1].substring(0,2);
var qg_api = server_api + "/question-generation?lang=" + lang + "&session_id=" + session_id;
var qg_cn_api = "http://72.93.242.201:8581/en_data";
var qg_data = [];
var qg_index = 0;
var number_of_question_per_page = 5;

var sending_qg_request = function() {
	setInterval(update_progress, 1000);

	$.ajax({
		method: 'get',
		url: qg_api,
		dataType: 'json',
		success: function(data) {
			// Send the data to CN QG API
			// console.log(JSON.stringify(data));
			redirect_qg_request(qg_cn_api, data);
			return;

			qg_data = data["qg_data"];
			// render_question(qg_data, qg_index, number_of_question_per_page);
			render_question(qg_data, qg_index, qg_data.length);
			// if(qg_data.length > 5) {
			// 	$("#more").html('<button type="button" class="button expanded" id="more-question" onclick="javascript:render_question(qg_data, qg_index, number_of_question_per_page);"><span lang="en">More question</span><span lang="zh">更多问题</span></button>');
			// }
			// $("#qg-summary").removeClass("hide");
			$("#qg").removeClass("hide");
			$("#qg-submit").removeClass("hide");
			$("#qg-loading").addClass("hide");
		},
		error: function(jqXHR, textStatus, errorThrown) {
			alert('Error: ' + errorThrown);
		}
	});
};

var redirect_qg_request = function(url, data) {
	var timestamp = Date.parse(new Date());
	var post_data = {
		"timestamp": timestamp,
        "en_content": JSON.stringify(data)
    };
	$.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        data: post_data
    }).done(function(data) {
    	console.log(post_data);
    	console.log(data);
        if (200 == data.result) {
        	window.location.href = url + "?name="+ timestamp;
        } else {
        	alert("Unknown Error");
        }
    });
};

var update_progress = function() {
	var progress = (parseFloat($('#qg-loading .progress .progress-meter-text').html().replace('%', '')) + 0.3).toFixed(1);
	if (progress < 99.5) {
		var percentVal = progress + '%';
		$('#qg-loading .progress .progress-meter').width(percentVal)
		$('#qg-loading .progress .progress-meter-text').html(percentVal);
	}
};

var render_question = function(qg_data, start=0, number_of_question_per_page=10) {
	if (start >= qg_data.length) {
		$("#qg").html($("#qg").html() + '<b>No more question. </b>');
		return;
	}
	var end = 0;
	if ((qg_data.length - start) < number_of_question_per_page) {
		end = qg_data.length;
	} else {
		end = start + number_of_question_per_page;
	}
	var qg_html = '';
	// console.log(start, end);

	// random qg_data
	if (qg_page == "qg") {
		qg_data = qg_data.sort(function() {
		    return .5 - Math.random();
		});
	}

	for (var i = start; i < end; i++) {
		// console.log(qg_data[i]["type"]);
		if (qg_data[i]["type"] == "choice") {
			qg_html += '<fieldset class="large-10 cell" id="q'+i+'"><legend><strong></strong>' + qg_data[i]["question"] + '</legend>';
			// put all answers into array
			var tmp_array = new Array();
			for (var j = 0; j < qg_data[i]["wrong_answer"].length; j++) {
				tmp_array[j] = '<p><input type="radio" name="q'+i+'" value="wrong_answer" id="q'+i+j+'"><label for="q'+i+j+'">'+qg_data[i]["wrong_answer"][j]+'</label></p>';
			}
			tmp_array[j] = '<p><input type="radio" name="q'+i+'" value="right_answer" id="q'+i+'x"><label for="q'+i+'x">'+qg_data[i]["right_answer"]+'</label></p>';
			// random array
			tmp_array = tmp_array.sort(function() {
				return .5 - Math.random();
			});
			// array to html
			for (var k = 0; k < tmp_array.length; k++) {
				qg_html += tmp_array[k];
			}
			// for (var j = 0; j < qg_data[i]["wrong_answer"].length; j++) {
			// 	qg_html += '<p><input type="radio" name="q'+i+'" value="wrong_answer" id="q'+i+j+'"><label for="q'+i+j+'">'+qg_data[i]["wrong_answer"][j]+'</label></p>';
			// }
			// qg_html += '<p><input type="radio" name="q'+i+'" value="right_answer" id="q'+i+'x"><label for="q'+i+'x">'+qg_data[i]["right_answer"]+'</label></p>';
			qg_html += '</fieldset>';
			// $("#qg").html($("#qg").html() + qg_html);
		}
	}
	$("#qg").html(qg_html);
	qg_index = start + number_of_question_per_page;
};



if (qg_page == "qg") {
	sending_qg_request();
}

if (qg_page == "qg_sat") {
	qg_api = server_api + "/question-generation-sat?session_id=" + session_id;
	sending_qg_request();
}

if (qg_page == "qg_summary") {

	// var max_length = 20;
	$('#qg-summary #rchars').html(max_length);
	$("#qg-summary textarea").attr("maxLength", max_length);
	$('#qg-summary textarea').keyup(function() {
		var textlen = max_length - $(this).val().length;
		$('#qg-summary #rchars').text(textlen);
	});

	$( "#qg-submit button" ).click(function() {
		$.post(
			server_api + "/rouge?lang=" + lang + "&session_id=" + session_id,
			{ text: $("#qg-summary textarea").val() },
			function(data){
				if (data["error"] != "") {
					alert(data["error"]);
				} else {
					$("#qg-summary strong").html("(Score: " + Math.round(data['rouge_score'] * 100) + "/100) ");
				}
			}
		);
	});

} else {
	$( "#qg-submit button" ).click(function() {
		var tmp_right_answer = 0;
		for (var i = 0; i < qg_data.length; i++) {
			if ($('input[name=q'+i+']:checked').val() == 'right_answer') {
				$("#q" + i + " legend strong").html("(Correct) ");
				tmp_right_answer ++;
			} else {
				$("#q" + i + " legend strong").html("(Wrong) ");
			}
		}
		alert("Total Question: " + qg_data.length + ".  Correct: " + tmp_right_answer + ".  Grade: " + (tmp_right_answer / qg_data.length * 100) + "/100.");
	});
}


