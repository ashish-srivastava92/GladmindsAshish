(function() {

    $('input.advisor-action').click(function() {
        var actionSet = $(this).parents('.advisor-action-item'), postAction = $(this).val(), sibblingActionSet = actionSet.siblings('.advisor-action-item'), disabledInputs = actionSet.find('input[type="text"]'), activeInputs = sibblingActionSet.find('input[type="text"]');

        activeInputs.attr('disabled', 'disabled').removeAttr('required');
        disabledInputs.removeAttr('disabled').attr('required', 'required');
    });

    $('form.coupon-check-form, form.coupon-close-form').on('submit', function(e) {
    	var data = $(this).serializeArray();
    	Utils.submitForm(e, data, '/v1/messages');
        return false;
    });

    $('.asc-form').on('submit', function(e) {
        var data = Utils.getFormData('.asc-form')
        Utils.submitForm(e, data, '/register/asc');
        return false;
    });
    
    $('.asc-self-form').on('submit', function(e) {
        var data = Utils.getFormData('.asc-self-form');
        Utils.submitForm(e, data, '/asc/self-register/');
        return false;
    });
    
    $('.sa-form').on('submit', function(event) {
        var data = Utils.getFormData('.sa-form');
        Utils.submitForm(event, data, '/register/sa');
        return false;
    });
    

    $('.customer-form').on('submit', function(e) {
    	var data = Utils.getFormData('.customer-form'),
            vin = $('#srch-vin').val();
    	data['vin'] = vin;
    	Utils.submitForm(e, data, '/register/customer');
        return false;
      });
    
    $('.vin-form').on('submit', function() {
      var vin = $('#srch-vin').val(),
          messageModal = $('.modal.message-modal'),
          messageBlock = $('.modal-body', messageModal);
      $('.customer-vin').val(vin);
      
      var jqXHR = $.ajax({
            type: 'POST',
            url: '/exceptions/customer',
            data: {'vin': vin},
            success: function(data){
              if(data['customer_phone']){
                  $('.customer-phone').val(data['customer_phone']);
                  $('.customer-name').val(data['customer_name'])
                  $('.name-readonly').attr('readOnly', true);
                  $('.purchase-date').val(data['purchase_date']).attr('readOnly', true);
                  $('.customer-submit').attr('disabled', false);
              }	
              else{
                  $('.customer-phone').val(data['customer_phone']);
            	  $('.customer-name').val('')
                  $('.name-readonly').attr('readOnly', false);
                  $('.purchase-date').val('').attr('readOnly', false);  
                  messageBlock.text(data.message);
                  messageModal.modal('show');
              }
            },
            error: function() {
            	messageBlock.text('Oops! Some error occurred!');
                messageModal.modal('show');
            }
          });
      return false;
    });
    
    $('.ucn-recovery-form').on('submit', function() {
      var formData = new FormData($(this).get(0));
      var messageModal = $('.modal.message-modal'),
          messageBlock = $('.modal-body', messageModal),
          waitingModal = $('.modal.waiting-dialog'),
          jqXHR = $.ajax({
          type: 'POST',
          url: '/exceptions/recover',
          data: formData,
          cache: false,
          processData: false,
          contentType: false,
          beforeSend: function(){
            $(this).find('input[type="text"]').val('');
            waitingModal.modal('show');
          },
          success: function(data){
            messageBlock.text(data.message);
            waitingModal.modal('hide');
            messageModal.modal('show');
          },
          error: function() {
            messageBlock.text('Invalid Data');
            waitingModal.modal('hide');
            messageModal.modal('show');
          }
        });
      return false;
    });
    
    $('#jobCard').on('change', function() {
      var fileInput = $(this),
          ext = fileInput.val().split('.').pop().toLowerCase();
      if($.inArray(ext, ['pdf','tiff','jpg']) == -1) {
          alert('Invalid file type!');
          fileInput.replaceWith(fileInput=fileInput.clone(true));
      }
    });
    
    $(document).ready(function() {

    });
})();
