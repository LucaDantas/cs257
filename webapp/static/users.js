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
	var maxUsers = document.getElementById('count').value;
	var searchType = document.getElementById('searchType').value;
	var lowestRating = document.getElementById('lowRating').value;
	var highestRating = document.getElementById('highRating').value;
	var institutionName = document.getElementById('name').value;
	var url = getAPIBaseURL() + '/users?max_users=' + maxUsers + '&institution_name=' + institutionName + '&institution_type=' + searchType + '&lowest_rating=' + lowestRating + '&highest_rating=' + highestRating;
	
	fetch(url, {method: 'get'})
	.then((response) => response.json())
	.then(function(usersList) {
		var tableBody = '';
		tableBody += '<thead><tr><th>Handle</th><th>Name</th><th>Rating</th><th>Max Rating</th><th>Rank</th><th>Max Rank</th></tr></thead>'
		for (var i = 0; i < usersList.length; i++) {
			tableBody += '<tr>';
			tableBody += '<td>' + usersList[i]['handle'] + '</td>';
			tableBody += '<td>' + usersList[i]['first_name'] + ' ' + usersList[i]['last_name'] + '</td>';
			tableBody += '<td>' + usersList[i]['rating'] + '</td>';
			tableBody += '<td>' + usersList[i]['max_rating'] + '</td>';
			tableBody += '<td>' + usersList[i]['user_rank'] + '</td>';
			tableBody += '<td>' + usersList[i]['max_user_rank'] + '</td>';
			tableBody += '</tr>';
		}
		var resultsTableElement = document.getElementById('users');
		if (resultsTableElement) {
			resultsTableElement.innerHTML = tableBody;
		}
	})
	.catch(function(error) {
		console.log(error);
	});
}
