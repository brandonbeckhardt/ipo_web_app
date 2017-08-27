var showOrHideGroupTable = function(button, table) {
    if (table.style.display === 'none') {
        table.style.display = '';
        button.innerHTML = '-';
    } else {
        table.style.display = 'none';
        button.innerHTML = '+';
    }
}


var loadMatchesToJavaScript = function(matches, groups) {
    allMatchesGlobal = matches;
    allGroupsGlobal = groups;
}


var sortMatches = function(button, sortBy, groupIdentifier, edit, urlHandler) {
    var order = 'none';
    if (button != null) {
        if (button.value == '&#9660;') { //already downcarrot (ascending)
            order = 'desc'; //set order to descending
        } else if (button.value == '&#9650;') { //already  upcarrot (descending)
            order = 'none'; //set order to desc
        } else {
            order = 'asc'; //set order to asc
        }
    }
    var group = getGroupFromIdentifier(groupIdentifier);
    if (group == null) {
        return null;
    }
    var matches = allMatchesGlobal[groupIdentifier];

    if (edit == null) edit = false;
    $.ajax({type:'POST',url: "default/matcher_table", 
        data: {'edit':edit, 'matches':JSON.stringify(matches),  
        'group': JSON.stringify(group), 'urlHandler':urlHandler,
        'sortBy':sortBy, 'order':order},
        success: function(result){
            var groupIdentifier = group[1]
            var divIdRef = "#table_wrapper_" + groupIdentifier
            var tableWrapperRef = "#table_wrapper_group_" + groupIdentifier
            $( divIdRef ).html( $( result ).filter( tableWrapperRef ).html() );
        }});
}

var getGroupFromIdentifier = function(groupIdentifier) {
    for (var i = 0; i < allGroupsGlobal.length; i++) {
        if (allGroupsGlobal[i][1] == groupIdentifier) {
            return allGroupsGlobal[i];
        }
    }
    return null;
}