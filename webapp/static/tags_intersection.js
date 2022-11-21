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
    // from api we get a list [{rating: count at that rating}, ...]

    // we want to graph:
    // x axis is rating range
    // y axis is the number of problems with that rating?
    
    // This is only the graph, the other return types still need to be implemented
    fetch(url, {method: 'get'})
    .then((response) => response.json())
    .then(function(problemsData) {
        var dataPoints = problemsData.map(pt => ({x: pt[0], y: pt[1]}));
        var c = new CanvasJS.Chart("chartContainer", {
            axisX: { title: "Rating of problem" },
            axisY: { title: "Number of problems" },
            data: [{type: "column", dataPoints: dataPoints}]
        });
        c.render();
    })
    .catch(function(error) {
        console.log(error);
    });
}
