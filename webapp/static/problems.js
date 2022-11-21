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

function getAPIBaseURL() {
    var baseURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/api';
    return baseURL;
}

function populateTags() {
    var url = getAPIBaseURL() + '/tag_names';

    fetch(url, {method: 'get'})
        .then(response => response.json())
        .then(function(tag_names) {
            var options = '<option></option>'; // Leave the option for no tag
            for (let i = 0; i < tag_names.length; i++) {
                options += '<option value="' + tag_names[i] + '">' + tag_names[i] + '</option>';
            }
            var select_tags = document.getElementById('tags');
            if (select_tags) {
                    select_tags.innerHTML = options;
            }
        })
}

function onSearchButtonClicked() {
    var tag = document.getElementById('tags').value;
    var lowestRating = document.getElementById('lowRating').value;
    var highestRating = document.getElementById('highRating').value;
    var maxProblems = document.getElementById('count').value;

    var url = getAPIBaseURL() + '/problems?tag=' + tag + '&lowest_rating=' + lowestRating + '&highest_rating=' + highestRating + '&max_problems=' + maxProblems;
    
    fetch(url, {method: 'get'})
    .then((response) => response.json())
    .then(function(problemsList) {
        var tableBody = '';
        tableBody += '<thead><tr><th>Id</th><th>Name</th><th>Rating</th><th>Tags</th><th>Solved Count</th></thead>'
        for (var i = 0; i < problemsList.length; i++) {
            var size = problemsList[i]['id'].length;
            var contestID = problemsList[i]['id'].substring(0, size-1);
            var problemLetter = problemsList[i]['id'][size-1];
            tableBody += '<tr>';
            tableBody += '<td><a href=https://codeforces.com/contest/' + contestID + '/problem/' + problemLetter + '>' + problemsList[i]['id'] + '</a></td>';
            tableBody += '<td>' + problemsList[i]['name'] + '</td>';
            tableBody += '<td>' + problemsList[i]['rating'] + '</td>';
            tableBody += '<td>' + problemsList[i]['tags'] + '</td>';
            tableBody += '<td>' + problemsList[i]['solved_count'] + '</td>';
            tableBody += '</tr>';
        }
        var resultsTableElement = document.getElementById('problems');
        if (resultsTableElement) {
            resultsTableElement.innerHTML = tableBody;
        }
    })
    .catch(function(error) {
        console.log(error);
    });
}
