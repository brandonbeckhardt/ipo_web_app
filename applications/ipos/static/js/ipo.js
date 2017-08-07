var showOrHideGroupTable = function(button, table) {
    if (table.style.display === 'none') {
        table.style.display = '';
        button.innerHTML = '-';
    } else {
        table.style.display = 'none';
        button.innerHTML = '+';
    }
}

var sortMatches = function(sortBy, order, matches, group, edit, urlHandler) {
    console.log(matches);
    console.log(sortBy);
    $.ajax({url: "default/matcher_table", 
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