function dump_data(data){
    var pretty_data = JSON.stringify(data, null, 2);
    $('#dump').html(pretty_data)
}

$(function() {
    console.log('Clients');
    $("form").submit(function(){
        console.log("Submitted");

        var data = {'scrapper': 'reddit'};

        $.getJSON('/_add_numbers',
        data,
        , function(responnse) {
          $("#dump").text(response.result);
        });
    });
    return false;
});
