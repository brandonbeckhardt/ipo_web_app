var showOrHideGroupTable = function(button, table) {
    if (table.style.display === 'none') {
        table.style.display = '';
        button.innerHTML = '-';
    } else {
        table.style.display = 'none';
        button.innerHTML = '+';
    }
}

var sortMatches = function(matches, group, edit, urlHandler) {
    $.ajax({url: "default/matcher_table", 
        data: {'edit':edit, 'matches':JSON.stringify(matches),  
        'group': JSON.stringify(group), 'urlHandler':urlHandler},
        success: function(result){
            console.log(result)
            var groupIdentifier = group[1]
            var divIdRef = "#table_wrapper_" + groupIdentifier
            var tableWrapperRef = "#table_wrapper_group_" + groupIdentifier
            $( divIdRef ).html( $( result ).filter( tableWrapperRef ).html() );
            console.log(result)
        }});
}