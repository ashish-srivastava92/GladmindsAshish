//accessToken = localStorage.getItem("access_token");

mainURL = "http://powerrewardsreports.elasticbeanstalk.com/api/index.php?access_token="+access_token+"&action=";
$(document).ready(function(){
	 initAddChart("mhome",1);
	

    $(".nav-tabs a").click(function(){
        $(this).tab('show');
    });

    $('.nav-tabs a').on('shown.bs.tab', function(event){
        var x = $(event.target).text();         // active tab
        var y = $(event.relatedTarget).text();  // previous tab
        $(".act span").text(x);
        $(".prev span").text(y);
    });


    $(document).on("click",".downloadBtn",function(){
    	stateID = $(this).parent().find(".allstates").val();
    	yearID = $(this).parent().find(".allyears").val();

    	monthID = "";

    	if($(this).parent().find(".allmonths")){
    		// debugger;
    		// alert("in");

			monthID = $(this).parent().find(".allmonths").val();
    	}

    	tabPaneID = $(this).parents(".tab-pane").attr("id");
    	className = $("."+tabPaneID).attr("charturl");


    	dataURL = mainURL+className+"download&stateid="+stateID+"&year="+yearID;

		if(monthID!="")
			dataURL +="&monthID="+monthID;

    	document.location.assign(dataURL);

		// $.ajax({
		// 	url: dataURL, 
		// 	success: function(result){
		// 		// loadChart(result,className);
		// 		// hideLoading();
		// 		alert(result)
		// 	}
		// });	
    })



    var checkbox = $("#checkbox");
	checkbox.change(function(event) {
	    var checkbox = event.target;
	    if (checkbox.checked) {
	    	$("body").removeClass("retailer").addClass("mechanic");
	        //Checkbox has been checked
			$(".pageRetailer").fadeOut("fast",function(){

		        $(".pageMechanic").fadeIn("slow"); 
		        $('.pageMechanic a:first').tab('show');
			});


	    } else {
	    	$("body").removeClass("mechanic").addClass("retailer");
	        //Checkbox has been unchecked
			$(".pageMechanic").fadeOut("fast",function(){

		        $(".pageRetailer").fadeIn("slow"); 
		        $('.pageRetailer a:first').tab('show');
		        initAddChart("rhome",1);
		        // alert($('.pageRetailer a:first').css("class"));

		        

			});
	    }

	});

    $("a").on('shown.bs.tab', function(e) {
	    var target = $(e.target).attr("class");
		initAddChart(target,1)
	 });

	$(document).on('change', '.allstates,.allyears,.allmonths', function(event){

		divName = $(this).parents(".tab-pane")[0].id;
		// alert(divName)
		// $("#"+divName+"DataChart").remove();
		// getChartData(divName+"Data");
		FusionCharts(divName+"DataChart").dispose();
		getChartData(divName+"Data");

	});



});

// $( window ).resize(resizeChart);


function resizeChart(){
	// $("#page-wrapper").css("min-height",$(window).height()-$("nav.navbar").height());
}

function initAddChart(className,loadChart){

	obj = $("#"+className+"Data");
	chartWidth = window.innerWidth-200;
	chartHeight = window.innerHeight-250;
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

	if(obj.length==0){
		// alert(className)

		str = '<div id="'+className+'Data" width="'+chartWidth+'" height="'+chartHeight+'" class="canvasStyle"></div>\
				<div class="row-fluid">\
			 		<div class="col-md-12 text-right form-group" style="position: absolute;top: 0;right: 0;padding-top: 15px;">\
			 			<label>';

		if($("."+className).attr("showstate")!="0"){
			str +='<select class="form-control allstates">\
	 					<option value="">All States</option>\
	 				</select>';
		}

		if($("#"+className).attr("foruser")=="mechanic"){
			buttonClass = "warning";
		}
		else{
			buttonClass = "info";
		}


		//For Product Fitment
		if(className=="mmenu6" || className=="rmenu6"){
			str +='</label> <label><select class="form-control allmonths">';

			months.forEach(function(month,index) {
			    str +="<option value='"+ parseInt(index+1) +"'>"+month+"</option>"
			});

			str +="</select>";
		}

			str += '</label>\
				 			<label>\
				 				<select class="form-control allyears">\
				 				</select>\
				 			</label>'

			if(className!="mmenu1")
				str += ' <button type="button" class="downloadBtn btn btn-'+buttonClass+'" >Download</button>';
				 		

			str += '</div></div>';

	 	$("#"+className).append(str);
	 	 getStates(className, loadChart);

	}

}

function getStates(className,loadChart){

	dataURL = mainURL+"getstates";
	showLoading();
	$.ajax({
		url: dataURL, 
		dataType: 'json',
		success: function(result){
			if(result.status==0){
				
				alert(result.message)
				hideLoading();
				$("#splash .loading").hide();
				return;
			}
			else{

				$("#splash").fadeOut("slow",function(){


			
					if(result.user_role=="SuperAdmins"){
						$(".mmenu1, .rmenu1, #mmenu1, #rmenu1").removeAttr("style")
					}


				    years = result.years.split(",").sort();
					currYear = new Date().getFullYear();
					$.each(years, function(a,obj) {

						selected = ""
						if(currYear == obj)
							selected = " selected "
						// debugger;

				        $("#"+className+" .allyears").append("<option value='"+obj+"'"+selected+">"+obj+"</option>");
				    });

					$.each(result.states, function(a,obj) {
				        $("#"+className+" .allstates").append("<option value='"+obj.id+"'>"+obj.state_name+"</option>");
				    });



				 	if(loadChart){
				 		getChartData(className+"Data");
				 	}


				});
			}
		}
	});
}

function getChartData(className){

	parentDivID = $("#"+className).parents(".tab-pane")[0].id;
	// alert(parentDivID.length)
	// debugger;
	stateID = $("#"+parentDivID+" .allstates").val();
	yearID = $("#"+parentDivID+" .allyears").val();
	monthID = "";

	if($("#"+parentDivID+" .allmonths"))
		monthID = $("#"+parentDivID+" .allmonths").val();

	tabClassName = className.replace('Data','');
	// debugger;
	action = $("."+tabClassName).attr("chartURL");
	showLoading();

	dataURL = mainURL+action+"&stateid="+stateID+"&year="+yearID;

	if(monthID!="")
		dataURL +="&monthID="+monthID;


	$.ajax({
		url: dataURL, 
		dataType:"json",
		success: function(result){
			loadChart(result,className);
			hideLoading();
		}
	});

}

function loadChart(result,renderObj){
	FusionCharts.ready(function() {
		chartID = renderObj+'Chart';
		// alert(chartID+"----")
	// alert(chartID)
	    var revenueChart = new FusionCharts({
	        id: chartID,
	        type: 'column3d',
	        width: "100%",
	        height: "100%",
	        renderAt: renderObj,
	        dataFormat: 'json',
	        dataSource: result
	        });
	 
	    revenueChart.render();
	});

}

function changeRole(obj){
	alert(obj.value)
}

function showLoading(){
	$("#loading").show();
}

function hideLoading(){
	$("#loading").hide();
}
