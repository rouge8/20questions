$(document).ready(function() {
    
    $('.known').change(function() {
        if($('#new_character').attr('readonly') == false) {
            $('#new_character').attr('readonly', true);
        }
    });
    
    $('#unknown').change(function() {
        if($('#new_character').attr('readonly') == true) {
            $('#new_character').removeAttr('readonly');
        }
    });

    $('#new_character').click(function() {
        if($('#new_character').attr('readonly') == true) {
            $('#new_character').removeAttr('readonly');
            $('#unknown').attr('checked', true);
        }
    });
    
});