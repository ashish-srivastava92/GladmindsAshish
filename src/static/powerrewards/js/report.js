$(".footer").html('<nav id="footerMenu" class="footerMenu">\
				</nav>')

	// $(".footerMenu").navbar();

	$(".footer a").removeClass("active");

$(document).on("pageshow", function (e, data) {


    pageID = ($.mobile.activePage.attr('id'));
    // alert(pageID)

    
    $('.footer a[href="#'+pageID+'"]').addClass("ui-btn-active");

});

// $(document).ready(function() {
//     $('#mytable').DataTable( {
//         "processing": true,
//         "serverSide": true,
//         "ajax": "http://qa.bajajcv.gladminds.co/v1/members/active/?access_token="+localStorage.getItem('access_token')+"&active_days=30"
//     } );
// } );






function showLoading(){
    $("body").append('<div class="modalWindow"/>');

    $.mobile.loading( 'show', {
        textVisible: true,
        theme: 'z',
        html: ""
    });

  // $.mobile.showPageLoadingMsg();

}

function hideLoading(){
    $.mobile.loading( 'hide');
    $(".modalWindow").remove();

}

/**---------- Start of datepicker js----------**/
var date = new Date();
        var d = new Date();        
        d.setDate(date.getDate());
        
$('#sandbox-container input').datepicker({
    format: "yyyy-mm-dd",
    autoclose: true,
    endDate: '+0d',
    todayHighlight: true
    
});


