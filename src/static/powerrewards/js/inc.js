$(document).ready(function(){
	windowResizer();

});

window.onresize = windowResizer;
	
$(document).on("click","#transitionExample-screen",function(){
	$('#video').get(0).pause();
	$('#myCarousel').carousel('cycle');
});

$(document).on("hide","#add-form",function(){
	$('.ui-panel-dismiss-open').hide();
});
 
$(document).on("click",".ui-panel-dismiss-open",function(){
	$('.ui-panel-dismiss-open').hide();
});

$(document).on("click","#imgprvw",function(){
	$('#filUpload').click();
});

$(document).on("click",".playimg",function(){
	$('#myCarousel').carousel('pause');
});

function slideSplash(){
	// alert("un")
	$.mobile.changePage("#welcome", { transition : 'flip'});
}


$(document).on("pagecreate",function(){

	// $("#rewards").click(function(){

	// 	// alert("in")
	// 	// $.mobile.loadPage("pages/rewards.html",{
	//  //        pageContainer: $('#target'),
	//  //        type: 'post',
	//  //        reloadPage: true
	//  //    });

	// 	// $( ":mobile-pagecontainer" ).pageContainer( "load", "pages/rewards.html", { role: "page" } );

	//     // $.mobile.changePage( "pages/rewards.html", { transition: "slideup"} );
	//      // $.mobile.changePage( "pages/faq.html");

 //    });



	$("#add-form").on('hide',function () {
            $('.ui-panel-dismiss').hide();
    });


	$(".topMenu").navbar();

	$(".footer").html('<nav id="footerMenu" class="footerMenu">\
		<a href="#add-form" class="ui-link footer_links" data-role="none">Reward Catalogue</a> |\
		<a href="#page4" class="footer_links">Terms and Conditions</a> |\
		<a href="#page5" class="footer_links">Legal Disclaimer</a>\
		</nav>')

	$(".footerMenu").navbar();

	

	



// 	var str = '<div data-role="panel" class="panel" data-position="right" data-display="reveal"  data-dismissible="true"  data-theme="a" id="add-form"  >\
// 	 	<div class="wrapper" style="height: 454px;">\
// 	 	<a href="" data-rel="close" class="ui-btn ui-icon-delete ui-btn-icon-notext ui-corner-all "></a>\
// 	            <div class="bajaj-header-bar centered">\
// 	                <div class="header content clearfix" id="brand_image">	\
// 	                <img class="img-responsive logo" src="img/Bajaj_Logo.png"></div>\
// 	            </div>\
// 	            <div class="main content clearfix">\
// 	                <div class="card signin-card clearfix">\
// 	                    <h1 class="login-aftersell-title">\
// 	                        One Company...One Experience\
// 	                    </h1>\
// 	                    <form method="post" id="login-form" autocomplete="off" action="#">\
// 	                    	<input type="hidden" id="csrfmiddlewaretoken" name="csrfmiddlewaretoken" value="" />\
// 	                        <div class="text-left alert alert-danger" id="error-msg-login-window">Invalid Credientials</div>\
// 	                        <label class="hidden-label" for="Email">Email</label>\
// 	                        <input id="Email" name="username" type="email" placeholder="Email" value="" spellcheck="false" required>\
// 	                        <label class="hidden-label" for="Passwd">Password</label>\
// 	                        <input id="Passwd" name="password" type="password" placeholder="Password" value="" required><br/>\
// 	                        <button type="submit" id="signIn" name="signIn" class="rc-button rc-button-submit">Sign In</button>\
// 	                        <!-- <div class="forgot-pwd">\
// 	                            <label class="remember">\
// 	                                <a href="#">\
// 	                                    Forgot Password?\
// 	                                </a>\
// 	                            </label>\
// 	                        </div> -->\
// 	                    </form>\
// 	                </div>\
// 	              <!--   <div class="text-center aftersell-logo">\
// 	                    <img class="profile-img after-sell img-circle img-responsive" src="img/aftersell.png" alt="aftersell">\
// 	                </div>\
// 	                <div class="oneApp-bajaj">\
// 	                    <p class="create-account">\
// 	                        <a id="link-signup" class="new-user-reg" href="">\
// 	                            Create an account\
// 	                        </a>\
// 	                    </p>\
// 	                </div> -->\
// 	            </div>\
// 	            <div class="browserSupport">\
// 	                Supporting Browsers: <a href="https://www.google.co.in/chrome/" target="_blank"><img data-toggle="tooltip" title="" data-placement="top" src="img/chrome.png" data-original-title="Download Chrome"></a> <a href="https://www.mozilla.org/en-US/firefox/new/" target="_blank"><img data-toggle="tooltip" title="" data-placement="top" src="img/firefox.png" data-original-title="Download Firefox"></a><br/>\
// 	            </div>\
// 	    </div>\
// 	        <footer><img id="panelimg" src="img/panelimg.png" alt="jQuery Mobile"><br><span>All rights reserved by Bajaj Auto. Ltd.</span><br>        <div style="margin:2px 0"><span class="framed circle" style="line-height:20px;margin:10px 20px 10px 0;"><img style="width:16px;height:16px" src="img/phone.png" alt="phone icon" align="top"> <a href="tel:917847011011">+917847011011</a></span> <span class="framed circle"><img style="width:16px;height:16px" src="img/mail.png" alt="Mail icon" align="top"> <a href="mailto:hello@gladminds.co">hello@gladminds.co</a></span></div>        <div style="margin-bottom:10px;"><span>Powered by <a href="//www.gladminds.co/#products" target="_blank">GladMinds Connect Platform</a></span>         </div></footer>\
// 	</div>';

// 	$(document).one('pagebeforecreate', function () {
//   $.mobile.pageContainer.prepend(str);
  
// });
	

	$( ".panel" ).panel();

	$(document).on('close', ".ui-panel", function() {
	    $(".ui-panel-dismiss").css("display","none");
	    alert("in")

	});

	$(".ui-panel").on("close",function(){
	        alert("byebye");
	});

  // (you have to add IDs to each page like 'page1content')
    $(".footer a").removeClass("active");

// debugger
// 	pageID = $.mobile.activePage.attr('id');

//     $('.footer a[href="#'+pageID+'"]').addClass("active");

	
  //   $("#signIn").click(function(){

  //       $.post("//bajajcv.gladminds.co/admin/", function(data, status){
  //           alert("Data: " + data + "\nStatus: " + status);
  //       });
		// alert('clicked');

		// ajaxify("login-form",pageRedirect)
  //   });

});

qaLoginURL = "/v1/gm-users/login/";

// qaLoginURL = "//bajaj.gladminds.co/v1/gm-users/login/";


// $("#signIn").bind('click', function(e){

$(document).on('click','#signIn',function(e){
	e.preventDefault();
	// $("#error-msg-login-window").css("display", "none");

	showLoading();
	var input_email = $("#Email").val();
	var email = input_email.trim();
	 localStorage.setItem('email', email);

	var input_password = $("#Passwd").val();
	var password = input_password.trim();

	// var pwd_encrypted = $.md5(password);
	var pwd_encrypted = password;

	    var formData = {"username":email,"password":pwd_encrypted}
	    serilizedData = JSON.stringify(formData);


	    //console.log(formData)

	    $.ajax({
	        url : qaLoginURL,
	        type: "POST",
	        cache: false,
	        data: serilizedData,
	        async: true,
	        success: function(data, resp){	
	        	console.log(data)
	        	if (data.status == 1) {
	        		localStorage.setItem('access_token', data.access_token)
	        		$("#csrfmiddlewaretoken").val(data.access_token);
//	        		$("#login-form").attr("action", "/login/");
//	        		$("#login-form").submit();
	        		window.location.replace("/login/");
	        	} else {
	                $("#error-msg-login-window").css("display", "block");   
	                hideLoading();
	            }
	        },
	        error: function(error)
	        {
	        	hideLoading();
	            $(".error-msg-login-window").css("display", "block");
	        }
	});

});


$(document).on("pageshow", function (e, data) {


    pageID = ($.mobile.activePage.attr('id'));
    // alert(pageID)

    
    if(pageID=="splashScreen")
    	setTimeout(slideSplash,2000);


    $('.footer a[href="#'+pageID+'"]').addClass("ui-btn-active");

});

function windowResizer(){
	docHeight = $(document).height();
	ht1 = $("#page1 .jqm-header").height();
	ht2 = $("#page1 .f.ooter").height();
	


	carousalHeight = docHeight - (135);

	$("#myCarousel, .carousel-inner, .item").height(carousalHeight);
}


function hover(element) {
    element.setAttribute('src', '/static/powerrewards/img/play_mo.png');
}
function unhover(element) {
    element.setAttribute('src', '/static/powerrewards/img/play.png');
}

function showimagepreview(input) {
if (input.files && input.files[0]) {
var filerdr = new FileReader();
filerdr.onload = function(e) {
$('#imgprvw').attr('src', e.target.result);
}
filerdr.readAsDataURL(input.files[0]);
}
}


jQuery.browser = {};
(function () {
    jQuery.browser.msie = false;
    jQuery.browser.version = 0;
    if (navigator.userAgent.match(/MSIE ([0-9]+)\./)) {
        jQuery.browser.msie = true;
        jQuery.browser.version = RegExp.$1;
    }
})();
	$(function() {


		$('#sig1').signature({color: 'blue',width: '100% !important', height:'80%'});
		$('#clear1').click(function() {
			$('#sig1').signature('clear');
		});
		$('#sig2').signature();
		$('#clear2').click(function() {
			$('#sig2').signature('clear');
		});
		$('#sig3').signature();
		$('#clear3').click(function() {
			$('#sig3').signature('clear');
		});


	});



// function ajaxify(formObj,successfunction){

// 		showLoading();
// 		var input_email = $("#Email").val();
// 		var email = input_email.trim();

// 		var input_password = $("#Passwd").val();
// 		var password = input_password.trim();

// 		// var pwd_encrypted = $.md5(password);
// 		var pwd_encrypted = password;

// 		var formData = {"username":email,"password":pwd_encrypted}
// 		serilizedData = JSON.stringify(formData);
// 		alert(serilizedData)
//   		testURL = "http://bajajcv.gladminds.co/v1/gm-users/login";




//         $.ajax({
//             url : testURL,
//             type: "POST",
//             cache: false,
//             data: serilizedData,
//             success: function(data, resp){	
//             	//console.log(data)
//             	if (data.status == 1) {

//             		alert(data.access_token)
//             		// localStorage.setItem("email", email);
//             		// localStorage.setItem("access_token", data.access_token);
//             		// var txtPermissions = getPermissions(data);
// 					hideLoading();

//             	} else {
//                     $("#error-msg-login-window").css("display", "block");   
//                     hideLoading();
//                 }
//             },
//             error: function(error)
//             {
//             	hideLoading();
//                 $(".error-msg-login-window").css("display", "block");
//             }
//     });

//     return false;
// }


function pageRedirect(jsonObj){
	alert(jsonObj);
	$("#csrfmiddlewaretoken").val($(jsonObj).access_token)
}


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


