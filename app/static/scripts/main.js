var spinClass;
var bulkUpdate;
window.onload = function() {
  bulkUpdate = false;
  var dataBtn = document.getElementById("showData");
  var pdfBtn = document.getElementById("downloadPDF");
  var savePlotBtn = document.getElementById("savePlots");

  dataBtn.onclick = function() {
    var data = document.getElementById("dataDiv");
    data.style.display = "block";
    return false;
  };

  pdfBtn.onclick = function() {
    //redirect to pdf.html with selected datasets
    //window.location.href = "{{ url_for('pdf') }}";
    post('/pdf', {name: 'Donnie Darko'});
    return false;
  };

  savePlotBtn.onclick = function () {
    var plotNameInput = document.getElementById("plotName");
    if(plotNameInput.value == ''){
      alert('Please provide a name for the data set.');
      return false;
    }
    //post('/savePlot', {name: 'Set E',data:{{selected_datasets|tojson}} });
    post('/savePlot', {name: plotNameInput.value, data:selected_datasets_js });
    return false;
  };
  //Update the initial metadata
  var datasetForm = document.getElementById("datasets");
  displayMetadata(datasetForm);
};

function displayMetadata(form){
  checkSpinConsistency(form);
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

/**
* Notes:
*  Only one filter is applied at a time.
*  No support for multiple selection within a certain filter (ie CMS and LUX will result in CMS only)
*  Does not clear other filter selections, so may appear as if multple selects are made.
**/
function updateFilter(selectFilter,filterType){
  var displayText = "<h4>Select a Dataset:</h4>";
  //Grab the main form that displays the dataset selection
  var datasetForm = document.getElementById("datasets");
  for (filterIndex=0; filterIndex<selectFilter.options.length; filterIndex++) {
      if (selectFilter.options[filterIndex].selected) {
        //Grab the filter from the selected value
        var filter = selectFilter.options[filterIndex].value;
        //For each dataset option (pulled from the main selection form)
        for (datasetIndex=0; datasetIndex<datasetForm.options.length; datasetIndex++) {
          if(metadata[datasetIndex][filterType] == filter){
             //Wrap the metadata in a clickable element- take action when the dataset is selected
             displayText += "<div class='filteredOption' onClick='selectDataset("+datasetIndex+")'>";
             displayText += getMetadataDisplay(metadata[datasetIndex]);
             displayText += "</div>"

          }
        }
      }
  }
  //Updated the selectable datasets from the filtered option
  var textElement = document.getElementById('filterDatasets');
  textElement.innerHTML = displayText;
}
//Select/Deselect the dataset option from the main list
function selectDataset(datasetIndex){
  var datasetForm = document.getElementById("datasets");
  datasetForm.options[datasetIndex].selected = !(datasetForm.options[datasetIndex].selected);
  //Focus the main select form, update the metadata for the options selected in the main select form
  datasetForm.focus();
  displayMetadata(datasetForm);
}

//Ensures all selected data sets have the same spin consistency
//Avoid checking if bulk update
function checkSpinConsistency(form){
  var errorIndex = -1;
  var count = 0;
  var localSpin = 0;
  for (i=0; i<form.options.length; i=i+1) {
    if (form.options[i].selected) {
      count++;
      //dataSelected = true;
      localSpin = metadata[i].spinDependency;
      if(spinClass){
        if(metadata[i].spinDependency != spinClass){
          //Deselect the error spin selection
          errorIndex = i;
        }
      }
      else{
        spinClass = metadata[i].spinDependency;
      }
    }
  }
  //If none are selected, (deselection from 1), then reset the spinClass
  if(count==0){
    spinClass = 0;
  }
  else if(count == 1){
    spinClass = localSpin;
  }
  else if(count>1 && errorIndex>=0 && !bulkUpdate){
    form.options[errorIndex].selected = false;
    alertSpinSelectError(spinClass);
  }
  bulkUpdate=false; //Reset the flag
}

function alertSpinSelectError(spinClass){
  alert('Please be consistant with your spin selection.');
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
  bulkUpdate = true;
  displayMetadata(datasetForm);
}

function getMetadataDisplay(metadata){
  var displayText = "";
  displayText += "<div class='row'>";
  displayText += "<div class='col col-2' style='font-weight:bold'>";
  displayText += "Filename:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata.fileName;
  displayText += "</div>";
  displayText += "</div>";

  displayText += "<div class='row'>";
  displayText += "<div class='col col-2' style='font-weight:bold'>";
  displayText += "Label:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata.dataLabel;
  displayText += "</div>";
  displayText += "</div>";

  displayText += "<div class='row'>";
  displayText += "<div class='col col-2' style='font-weight:bold'>";
  displayText += "Comment:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata.dataComment;
  displayText += "</div>";
  displayText += "</div>";

  displayText += "<div class='row'>";
  displayText += "<div class='col col-2' style='font-weight:bold'>";
  displayText += "Spin:";
  displayText += "</div>";
  displayText += "<div class='col'>";
  displayText += metadata.spinDependency;
  displayText += "</div>";
  displayText += "</div>";
  displayText += '<hr>';

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
  bulkUpdate=true;
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

  var csrfField = document.createElement("input");
  csrfField.setAttribute("type", "hidden");
  csrfField.setAttribute("name", "csrf_token");
  csrfField.setAttribute("value", csrf);
  form.appendChild(csrfField);

  document.body.appendChild(form);
  form.submit();
}
