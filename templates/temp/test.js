function myFunction() {
  document.getElementById("demo").innerHTML = "Paragraph changed.";
}


function redirectFunctionTest() {
	// Selecting the input element and get its value
	var inputVal = document.getElementById("myInput").value;
    // Displaying the value
    inputVal = inputVal/10;
    alert(inputVal);

    // var currURL = window.location.href;

    //var fontTag = document.getElementByClassName("")
    var fontTag = document.getElementsByTagName('font');
    var fontItem;
    // alert(inputVal+1) ;
    // alert(fontTag[0].value)
    for (fontItem of fontTag){
        var classID = fontItem.className;
        var colourID = classID.slice(6,8);
        var id = parseInt(colourID);
        // alert('clour id = '+id) ;
        // alert(fontItem.className);
        if (id < inputVal){
            fontItem.className="colour"+colourID;
        }else{
            fontItem.className="colour"+colourID+"in";
        }
        // if (fontItem.className=="colour02") {
        //     // alert(fontItem.className+222);
        //     fontItem.className="colour01";
        // }else{
        //     // alert(fontItem.className+333);
        //     fontItem.className="colour02";
        // }
    }
}



function getInputValue(){
            // Selecting the input element and get its value 
            var inputVal = document.getElementById("myInput").value;
            
            // Displaying the value
            alert(inputVal);
        }