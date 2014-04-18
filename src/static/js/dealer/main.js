(function (){

  $("input.advisor-action").click(function() {
    var actionSet = $(this).parents(".advisor-action-item"),
        postAction = $(this).val(),
        sibblingActionSet = actionSet.siblings(".advisor-action-item")
        disabledInputs = actionSet.find("input[type='text']")
        activeInputs = sibblingActionSet.find("input[type='text']");

        activeInputs.attr("disabled", "disabled").removeAttr("required");
        disabledInputs.removeAttr("disabled").attr("required", "required");
  });
  
  $(".query-form").on("submit", function(e) {
    var messageBlock = $(".user-message .message");
    var jqXHR = $.ajax({
      url: "/v1/messages",
      data: $("form.query-form").serializeArray(),
      type: "POST",
      beforeSend: function() {
        messageBlock.stop().fadeOut(0);
        $(".query-submit").prop("disabled", true);
      },
      success: function() {
        messageBlock.text("Query has been submitted");
        messageBlock.fadeIn(1000).fadeOut(5000);
        $(".query-submit").prop("disabled", false);
      },
      error: function() {
        messageBlock.text("Invalid Data. Please Check");
        messageBlock.fadeIn(1000).fadeOut(5000);
        $(".query-submit").prop("disabled", false);
      }
    });
    return false;
  })
  
  $(document).ready(function() {
    
  });
})();