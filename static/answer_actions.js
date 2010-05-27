$(document).ready(function() {

    $(document).shortkeys({
        'y':    
            function () { 
                $('[name=answer]').val('yes')
                $('#answer_form').submit() ;  
            },
                
        'u':    
            function () { 
                $('[name=answer]').val('unsure')
                $('#answer_form').submit() ;  
            },
        'n':    
            function () { 
                $('[name=answer]').val('no')
                $('#answer_form').submit() ;  
            }
    });
    
    $('[name=yes]').click( function() {
        $('[name=answer]').val('yes')
        $('#answer_form').submit() ;
    });

    $('[name=unsure]').click( function() {
        $('[name=answer]').val('unsure')
        $('#answer_form').submit() ;
    });

   $('[name=no]').click( function() {
        $('[name=answer]').val('no')
        $('#answer_form').submit() ;
   });


});