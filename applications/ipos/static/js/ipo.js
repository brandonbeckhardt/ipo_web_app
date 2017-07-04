var showOrHideGroupTable = function(button, table) {
    if (table.style.display === 'none') {
        table.style.display = '';
    	button.innerHTML = '-';
    } else {
        table.style.display = 'none';
    	button.innerHTML = '+';
    }
}

var sortMatches = function(matchesWrapper, matches, edit, urlHandler) {
	console.log(matches)
}