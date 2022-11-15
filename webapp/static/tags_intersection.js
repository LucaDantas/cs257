/*
 * Zimri Leisher and Luca Aurajo
 * Adopted from code from Jeff Ondich
 */

window.onload = initialize;

function initialize() {
    var element = document.getElementById('search');
    element.onclick = onSearchButtonClicked;
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
    
    fetch(url, {method: 'get'})
    .then((response) => response.json())
    .then(function(problemsData) {
        var chartData = [];
        var dataPoints = problemsData.map(pt => ({x: pt[0], y: pt[1]}));
        chartData.push({name: tagsRequested,
                        type: "line",
                        dataPoints: dataPoints,
                        showInLegend: true});
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
