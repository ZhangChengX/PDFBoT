$(document).foundation();

var has_popup = false;

var show_popup_box = function(selection, text) {
	// wrap the hightlight text
	var span_wrapper = document.createElement("span");
	span_wrapper.setAttribute("class", "selected_text");
	var range = selection.getRangeAt(0);
	range.surroundContents(span_wrapper);
	// popup box inside wrapper
	var popup_box = document.createElement("span");
	popup_box.setAttribute('class', 'popup_box');
	popup_box.innerHTML = text;
	// wrapper not empty
	if (span_wrapper.innerHTML.length > 0) {
		span_wrapper.appendChild(popup_box);
	}
	has_popup = true;
	// remove selection
	if (selection.removeAllRanges) {
		selection.removeAllRanges();
	} else if (selection.empty) {
		selection.empty();
	}
}

var lookup = function(selection, func) {
	$.ajax({
		url: en_to_en_api,
		dataType: 'jsonp',
		data: {
			phrase: selection.toString(),
			from: lang,
			dest: lang,
			format: "json"
		}, 
		success: function(data) {
			//console.log(data);
			var lookup_result = "No definitions found.";
			if ("tuc" in data && data.tuc.length > 0) {
				if("meanings" in data.tuc[0]) {
					lookup_result = "";
					for (var i = 0; i < 3 && i < data.tuc[0].meanings.length; i++) {
					 	lookup_result += data.tuc[0].meanings[i].text + "<br>";
					}
				} else if ("phrase" in data.tuc[0]) {
					lookup_result = data.tuc[0].phrase.text;
				}
			}
			func(selection, lookup_result);
		}
	});
}

$("#reading").on("mouseup", function() {
	var selection = window.getSelection ? window.getSelection() : document.selection;
	if(selection) {
		// remove popup
		if (has_popup) {
			$("span.selected_text span.popup_box").remove();
			$("span.selected_text").contents().unwrap();
			has_popup = false;
		}
		// lookup dict 
		selection = window.getSelection();
		if ("" != selection.toString()) {
			lookup(selection, show_popup_box);
		}
	} else {
		alert("Error: Your client doesn't support text selection.");
	}
});

