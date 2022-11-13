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
    var data_requested = document.getElementById('data_requested').value;
    var lowest_index = document.getElementById('lowIndex').value;
    var highest_index = document.getElementById('highIndex').value;

    var url = getAPIBaseURL() + '/contests?data_requested=' + data_requested + '&lowest_id=' + lowest_index + '&highest_index=' + highest_index;
    
    fetch(url, {method: 'get'})
    .then((response) => response.json())
    .then(function(usersList) {
        dataPoints = []
        var c = new CanvasJS.Chart("chartContainer", {
            data: [{
                type: "column",
                dataPoints: dataPoints
            }]
        });
        for(var i = 0; i < usersList.length; i++) {
            dataPoints.push({x: usersList[i][0], y: usersList[i][1]});
        }
        c.render();
    })
    .catch(function(error) {
        console.log(error);
    });
}
