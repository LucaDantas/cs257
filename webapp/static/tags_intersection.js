/*
 * Zimri Leisher and Luca Aurajo
 * Adopted from code from Jeff Ondich
 */

window.onload = initialize;

function initialize() {
    var element = document.getElementById('search');
    populateTags();
    element.onclick = onSearchButtonClicked;
}

function populateTags() {
    var url = getAPIBaseURL() + '/tag_names';

    fetch(url, {method: 'get'})
        .then(response => response.json())
        .then(function(tag_names) {
            var options = '';
            for (let i = 0; i < tag_names.length; i++) {
                options += '<option value="' + tag_names[i] + '">' + tag_names[i] + '</option>';
            }
            var select_tags = document.getElementById('tags');
            if (select_tags) {
                    select_tags.innerHTML = options;
            }
        })
}

function getAPIBaseURL() {
    var baseURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/api';
    return baseURL;
}

function onSearchButtonClicked() {
    var tagsRequested = [...document.getElementById('tags').options].filter(option => option.selected).map(option => option.value);
    // tagsRequested should be a comma separated list of tags

    var url = getAPIBaseURL() + '/tags_intersection/' + tagsRequested;
    // from api we get a list [(rating, count at that rating, solves at that rating), ...]

    var displayType = document.getElementById('displayType').value;

    var tagsTableElement = document.getElementById('tagsTable');
    var chartContainerElement = document.getElementById('chartContainer');
    var totalDisplayElement = document.getElementById('totalDisplay');
    fetch(url, {method: 'get'})
    .then((response) => response.json())
    .then(function(problemsData) {
        // if the user wants a graph...
        if(displayType == 'graph') {
            // for the graph the data won't include solves, just rating as x axis and
            // problems at that rating for y
            var dataPoints = problemsData.map(pt => ({x: pt[0], y: pt[1]}));
            var c = new CanvasJS.Chart("chartContainer", {
                axisX: { title: "Rating of problem" },
                axisY: { title: "Number of problems" },
                data: [{type: "column", dataPoints: dataPoints}]
            });
            c.render();
            tagsTableElement.innerHTML = '';
            totalDisplayElement.innerHTML = '';
            // otherwise, if the user wants a table...
        } else if(displayType == 'table') {
            // now we want a table with each row being (rating, count of problems, count of solves)
            var tableBody = '<table class="table">';
            tableBody += '<thead><tr><th>Rating range</th><th>Number of problems</th><th>Number of solutions</th></tr></thead>';
            for(const problem of problemsData) {
                tableBody += '<tr>';
                tableBody += '<td>' + problem[0] + '</td>';
                tableBody += '<td>' + problem[1] + '</td>';
                tableBody += '<td>' + problem[2] + '</td>';
                tableBody += '</tr>';
            }
            tableBody += '</table>';
            tagsTableElement.innerHTML = tableBody;
            chartContainerElement.innerHTML = '';
            totalDisplayElement.innerHTML = '';
        } else if(displayType == 'total') {
            tagsTableElement.innerHTML = '';
            chartContainerElement.innerHTML = '';
            var problemCount = 0;
            var solutionCount = 0;
            for(const problem of problemsData) {
                problemCount += problem[1];
                solutionCount += problem[2];
            }
            totalDisplayElement.innerHTML = '<p style="border-width:3px; border-style: solid; border-color:#000000; padding: 1em;">Number of problems: ' + problemCount + '<br>Number of solutions: ' + solutionCount + '</p>';
        }
    })
    .catch(function(error) {
        console.log(error);
    });
}
