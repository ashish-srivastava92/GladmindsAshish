'use strict';
$(function() {
    $('a.otp-redirect').click(function(event) {
        if(!$('#mobile').val()) {
            event.preventDefault();
            var messageBlock = $('.user-message .message');
            messageBlock.text('Enter Mobile Number');
            messageBlock.stop().fadeOut(0);
            messageBlock.fadeIn(1000).fadeOut(7000);
        }
    });
  
    var userMessage = function() {
        var splittedUrl = window.location.href.split('?'),
        messageBlock = $('.user-message .message'),
        flag = 0;
    
        if(splittedUrl.length > 1) {
            if(splittedUrl[1].indexOf('details=invalid')>=0){
                messageBlock.text('Invalid Details');
                flag = 1;
            } else if(splittedUrl[1].indexOf('token=invalid')>=0){
                messageBlock.text('Invalid Token');
                flag = 1;
            } else if(splittedUrl[1].indexOf('update=true')>=0){
                messageBlock.text('Your password has been updated. Please Login.');
                flag = 1;
            } else if(splittedUrl[1].indexOf('auth_error=true')>=0){
                messageBlock.text('Invalid Credentials');
                flag = 1;
            } else if(splittedUrl[1].indexOf('error=true')>=0){
                messageBlock.text('Password cannot be updated. Please try again Later');
                flag = 1;
            }
            if(flag === 1) {
                messageBlock.fadeIn(1000).fadeOut(7000);
            }
        }
    };
 
    var populateFields = function() {
        var splittedUrl = window.location.href.split('?');
        if(splittedUrl.length > 1) {
            if(splittedUrl[1].indexOf('username')>=0){
                var username = splittedUrl[1].split('=')[1];
                $('.otp-validation-form #username').val(username);
            }
        }
    };

    $(document).ready(function() {
        userMessage();
        populateFields();
    });
  
});