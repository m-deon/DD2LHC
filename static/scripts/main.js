window.onload = function() {
  var dataBtn = document.getElementById("showData");
  var pdfBtn = document.getElementById("downloadPDF");
  var savePlotBtn = document.getElementById("savePlots");

  dataBtn.onclick = function() {
    var data = document.getElementById("dataDiv");
    data.style.display = "block";
    return false;
  }

  pdfBtn.onclick = function() {
    //redirect to pdf.html with selected datasets
    //window.location.href = "{{ url_for('pdf') }}";
    post('/pdf', {name: 'Donnie Darko'});
    return false;
  }

  savePlotBtn.onclick = function () {
    var plotNameInput = document.getElementById("plotName");
    //post('/savePlot', {name: 'Set E',data:{{selected_datasets|tojson}} });
    post('/savePlot', {name: plotNameInput.value, data:selected_datasets_js });
    return false;
  }
  //Update the initial metadata
  var datasetForm = document.getElementById("datasets");
  displayMetadata(datasetForm);
}

function displayMetadata(form){
  //Generate the new metadata to display, depending if item is selected
  var displayText = "";
  for (i=0; i<form.options.length; i=i+1) {
  if (form.options[i].selected ) {
      displayText += getMetadataDisplay(metadata[i]);
    }
  }
  //Push the text to the html element
  var textElement = document.getElementById('datasetInfo');
  textElement.innerHTML = displayText;
}

function selectPlots(savedSelection){
  var datasetForm = document.getElementById("datasets");
  var selected = savedSelection.options[savedSelection.selectedIndex].innerHTML;
  var plotArray = plots[selected];

  for (i=0; i<datasetForm.options.length; i=i+1) {
    if(plotArray.indexOf(datasetForm.options[i].innerHTML) > -1){
      datasetForm.options[i].selected = true;
    }
    else{
      datasetForm.options[i].selected = false;
    }
  }
  datasetForm.focus();
  displayMetadata(datasetForm);
}

function getMetadataDisplay(metadata){
  var displayText = "";
  displayText += "<div class='row'>";
  displayText += "<div class='col col-2'>";
  displayText += "Filename:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata['fileName'];
  displayText += "</div>";
  displayText += "</div>";

  displayText += "<div class='row'>";
  displayText += "<div class='col col-2'>";
  displayText += "Label:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata['dataLabel'];
  displayText += "</div>";
  displayText += "</div>";

  displayText += "<div class='row'>";
  displayText += "<div class='col col-2'>";
  displayText += "Comment:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata['dataComment'];
  displayText += "</div>";
  displayText += "</div>";
  displayText = displayText + '<hr>';
  return displayText;
}

function updateConditionalSelect(conditionalSelect){
  var selectedInput = "";
  var inputs = document.getElementsByName("conditional_input");
  for (var i = 0, length = inputs.length; i < length; i++) {
    if (inputs[i].checked) {
      // do whatever you want with the checked radio
      selectedInput = inputs[i].value;
      // only one radio can be logically checked, don't check the rest
      break;
    }
  }

  var form = document.getElementById("datasets");
  for (i=0; i<form.options.length; i=i+1) {
    var meta = metadata[i];
    //If this meta matches the selected input, then we select in form
    form.options[i].selected = false; //Deselect previous selction
    if(meta['spinDependency'] === selectedInput){
      form.options[i].selected = true;
    }
  }
  //Now make sure the metadata is correct
  displayMetadata(form);
}

/******************************************************************************/
function post(path, params, method) {
  method = method || "post"; // Set method to post by default if not specified.

  // The rest of this code assumes you are not using a library.
  // It can be made less wordy if you use one.
  var form = document.createElement("form");
  form.setAttribute("method", method);
  form.setAttribute("action", path);

  for(var key in params) {
      if(params.hasOwnProperty(key)) {
          var hiddenField = document.createElement("input");
          hiddenField.setAttribute("type", "hidden");
          hiddenField.setAttribute("name", key);
          hiddenField.setAttribute("value", params[key]);

          form.appendChild(hiddenField);
      }
  }

  document.body.appendChild(form);
  form.submit();
}