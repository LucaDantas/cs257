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

    var url = getAPIBaseURL() + '/tags_graph/' + tagsRequested;
    // from api we get a map of tag: [{rating: count at that rating}, ...]

    // we want to graph:
    // x axis is rating range
    // y axis is the number of problems with that rating?
    // graph one line for each tag selected
    
    fetch(url, {method: 'get'})
    .then((response) => response.json())
    .then(function(problemsData) {
        var chartData = [];
        for(var key in problemsData) {
            var dataPoints = problemsData[key].map(pt => ({x: pt[0], y: pt[1]}));
            chartData.push({name: key,
                            type: "line",
                            dataPoints: dataPoints,
                            showInLegend: true});
        }
        var c = new CanvasJS.Chart("chartContainer", {
            axisX: { title: "Rating of problem" },
            axisY: { title: "Number of problems" },
            data: chartData
        });
        c.render();
    })
    .catch(function(error) {
        console.log(error);
    });
}
