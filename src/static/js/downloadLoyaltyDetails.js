function downloadDetails(e, check_url, url){
    var downloadModal = $('.modal.download-modal');
    downloadModal.modal('hide');
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: check_url,
        success: function(data){
        	e.preventDefault()
        	if (data.status) {
        		window.location.replace(url)
        	}
        	else{
        		$('.download-fail').removeClass('hide');
        	}
        },
        error: function(data){
        	e.preventDefault();
        }
    });
}

(function() {
    $(".modal-footer .download-member-detail").click(function(e) {
        $('.download-fail').addClass('hide');
        var choice = $( "#download-option option:selected" ).val();
            downloadChoice = {'choice':choice},
            check_url = '/check-detail/'+'Member/'+choice,
            url = '/member-download/'+choice;
        downloadDetails(e, check_url, url);
    });
	
    $(".modal-footer .download-welcome-detail").click(function(e) {
        $('.download-fail').addClass('hide');
        var choice = $( "#kit-download-option option:selected" ).val();
            downloadChoice = {'choice':choice},
            check_url = '/check-detail/'+'WelcomeKit/'+choice;
            url = '/kit-download/'+choice
        downloadDetails(e, check_url, url);
    });
	
    $(".modal-footer .download-redmeption-detail").click(function(e) {
        $('.download-fail').addClass('hide');
        var choice = $( "#redemption-download-option option:selected" ).val();
            downloadChoice = {'choice':choice},
            check_url = '/check-detail/'+'RedemptionRequest/'+choice;
            url = '/redemption-download/'+choice
        downloadDetails(e, check_url, url);
    });
    
    $(".modal-footer .download-accumulation-detail").click(function(e) {
        $('.download-fail').addClass('hide');
        var choice = $( "#accumulation-download-option option:selected" ).val();
            downloadChoice = {'choice':choice},
            check_url = '/check-detail/'+'AccumulationRequest/'+choice;
            url = '/accumulation-download/'+choice
        downloadDetails(e, check_url, url);
    });
})();