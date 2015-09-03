<div data-url="panel-responsive-page1" data-role="page" class="jqm-demos ui-responsive-panel" data-title="Power Rewards" id="page6">

    <div data-role="header" class="jqm-header" data-id="main-header">

		<!--<div data-role="navbar" id="topMenu" class="topMenu">
			<ul id="navlist">
				<li><a href="#page1">Power Rewards Program</a></li>
				<li><a href="#page2">Enrollment Conditions</a></li>
				<li><a href="#page3">FAQs</a></li>
				<li><a href="#add-form">Login</a></li>
			</ul>
		</div>-->



		<div class="bs-example">
		    <nav role="navigation" class="navbar navbar-default">
		        <!-- Brand and toggle get grouped for better mobile display -->
		        <div class="navbar-header">
		            <button type="button" data-target="#navbarCollapse6" data-toggle="collapse" class="navbar-toggle navbar_mob_toggle">
		                <span class="sr-only">Toggle navigation</span>
		                <span class="icon-bar"></span>
		                <span class="icon-bar"></span>
		                <span class="icon-bar"></span>
		            </button>
		            <a href="index.html" title="jQuery Mobile Demos home">
		            	<img src="img/power_rewards_logo.png" alt="jQuery Mobile">
		            </a>
		        </div>
		        <!-- Collection of nav links, forms, and other content for toggling -->
		        <div id="navbarCollapse6" class="collapse navbar-collapse">
		            <ul class="nav navbar-nav navbar-right">
		                <li ><a href="#page1">Power Rewards Program</a></li>
		                <li><a href="#page2">Enrollment Conditions</a></li>
		                <li ><a href="#page3">FAQs</a></li>
		                <!-- <li><a href="#page6">Registration</a></li> -->
		                <li><a href="#add-form">Login</a></li>
		                
		            </ul>

		            <!-- <ul class="nav navbar-nav navbar-right">
		                <li><a href="#">Login</a></li>
		            </ul> -->
		        </div>
		    </nav>
		</div>






    	<!--<h3>
			<a href="index.html" title="jQuery Mobile Demos home"><img src="img/power_rewards_logo.png" alt="jQuery Mobile"></a>
		</h3>-->
		
    </div><!-- /header -->



    <div data-role="content" id="content3">

		<div id="disclaimer" style="padding:2% 2%">
			<span class='spanclass' style="font-size:150%;">Registration</span>

			<div class="container-fluid" style="padding: 0 8%;">
				<form action="#page7" method="post" >
					<div class="row">
						<div class="col-md-9" style="padding:0;">
					    	<div class="container-fluid">
					    		<div class="row">
									<div class="col-md-3">
								        <label>Date:</label>
								        <input type="text" name="date" placeholder="Date" id="datepicker" readonly>
								    </div>
								</div> 
								<div class="row">
									<div class="col-md-3">
								        <label>Name of Mechanic:</label>
								    </div>
								</div>    
								<div class="row">    
								    <div class="col-md-4">
								    	<label>First Name:</label>
								        <input type="text" name="firstname" placeholder="First Name" required>
								    </div>
								    <div class="col-md-4">
								    	<label>Middle Name:</label>
								      	<input type="text" name="middlename" placeholder="Middle Name">
								    </div>
								    <div class="col-md-4">
								    	<label>Surname:</label>
								       	<input type="text" name="surname" placeholder="Surame">
								    </div>
								</div>    
								<div class="row">    
								    <div class="col-md-3">
								       	<label>Date of Birth:</label>
								        <input type="text" name="dob" placeholder="Date of Birth" id="datepicker1" readonly>
								    </div>
								</div>
								<div class="row">
								    <div class="col-md-3">
								        <label>Address1:</label>
								    </div>
								</div>    
								<div class="row">
								    <div class="col-md-8">
								        <label for="shopname">Shop Name</label>
								        <input type="text" name="shopname" placeholder="Shop Name" >
									</div>
								    <div class="col-md-4">
								        <label for="shopno">Shop No</label>
								        <input type="text" name="shopno" placeholder="Shop No" >
								    </div>
								</div>    
									
								 
					    	</div>
					    </div>
						<div class="col-md-3" >
					    	<label>Upload Image</label>
					    	
					       	<input type="file"  id="filUpload" onchange="showimagepreview(this)" name="image" style="display: none;">
					       	<img src="img/user.png" id="imgprvw" name="imgpre" style="width:100%;height:50%;" alt="Select Image to preview">
					    </div>
					</div>
					<div class="row">
					    <div class="col-md-3">    
					        <label for="street">Street Name</label>    
					        <input type="text" name="streetname" placeholder="Street Name">
					    </div>
					    
					    <div class="col-md-3">    
					        <label for="locality">Locality</label>   
					        <input type="text" name="locality" placeholder="Locality" >
					    </div>    
					    <div class="col-md-3">    
					        <label for="tehsil">Tehsil Name</label>   
					        <input type="text" name="tehsil" placeholder="Tehsil Name">
					    </div>
					    <div class="col-md-3">
					        <label for="taluka">Taluka</label>
					        <input type="text" name="taluka" placeholder="Taluka" >
					   	</div>    
					</div>    
					<div class="row">
					    <div class="col-md-3">
					        <label for="district">District</label>
					        <input type="text" name="district" placeholder="District" >
					    
					    </div>
					    <div class="col-md-3">
					        <label for="state">State</label>
					        <input type="text" name="state" placeholder="State" >
					    </div>
					    <div class="col-md-3">
					        <label for="pincode">Pincode</label>
					        <input type="text" name="pincode" placeholder="Pincode" >
					    </div>
					    <div class="col-md-3">
					        <label for="distributername">Name Of Distributer</label>
					        <input type="text" name="distributer" placeholder="Name Of Distributer" >
					    </div>
					</div>   
					<div class="row">
					    <div class="col-md-3">
					        <label for="distributercode">Code Of Distributer</label>
					        <input type="text" name="code" placeholder="Code" >
					    </div>
					    <div class="col-md-3">
					        <label for="town">Town</label>
					        <input type="text" name="town" placeholder="Town" >
					    </div>    
					</div>
					<div class="row">
					    <div class="col-md-4">
					        <label for="wallsize">*Avilable wall size for painting (length* width):</label>
					    </div>
					    <div class="col-md-5">
					        <label for="mobno">*Mobile Number (Velid no of mechanic, is must):</label>
					    </div>
					</div>
					<div class="row">
					    <div class="col-md-4">
					    	<input type="text" name="wallsize" placeholder="Wall Size" >
					    </div>
					    <div class="col-md-4">
					        <input type="text" name="mobno" placeholder="Mobile Number" >
					    </div>
					</div> 
					<div class="row">
					    <div class="col-md-4">
					        <label for="mobno">Product Segment handled:</label>
					    </div>
					    <div class="col-md-1">
					    	<label for="mobno">2S</label>
					        <input type="checkbox" name="2S" value="2S">
					    </div>
					    <div class="col-md-2">
					    	<label for="4S">4S CNG/LPG</label>
					        <input type="checkbox" name="4S" value="4S">
					    </div>
					    <div class="col-md-1">
					    	<label for="Diesel">Diesel</label>
					        <input type="checkbox" name="Diesel" value="Diesel">
					    </div>
					    <div class="col-md-2">
					    	<label>(Please tick)</label>
					    </div>
					</div> 
					<div class="row">
					    <div class="col-md-7">
					        <label>No of Vehicles (avg) attended/Month-Bajaj vehicles</label>
					    </div>
					</div>  
					<div class="row">
					    <div class="col-md-3">
					        <label>2S</label>
					        <input type="text" name="2sattended" placeholder="2S Attended">
					    </div>
					    <div class="col-md-3">
					        <label>4S</label>
					        <input type="text" name="4sattended" placeholder="4S Attended">
					    </div>
					    <div class="col-md-3">
					        <label>CNG/LPG</label>
					        <input type="text" name="CNGsattended" placeholder="CNG/LPG Attended">
					    </div>
					    <div class="col-md-3">
					        <label>Diesel</label>
					        <input type="text" name="Dieselattended" placeholder="Diesel Attended">
					    </div>
					</div>  
					<div class="row">
					    <div class="col-md-4">
					        <label for="partsused">Spare Parts Used in &#8377; Lacs/Month</label>
					        <input type="text" name="partsused" placeholder="&#8377;" >
					    </div>
						<div class="col-md-4">
					        <label for="bajaj">Bajaj Genuine parts %</label>
					        <input type="text" name="bajaj" placeholder="" >
					    </div>
					    <div class="col-md-4">
					        <label for="other">Other %</label>
					        <input type="text" name="other" placeholder="" >
					    </div>
					</div> 
					<div class="row">
					    <div class="col-md-4">
					        <label>Name of prefered Retailer for buying parts</label>
					        <input type="text" name="preferedretailer" placeholder="Prefered Retailer">
					    </div>
					    <div class="col-md-4">
					        <label>Town</label>
					        <input type="text" name="retailertown" placeholder="Town">
					    </div>
					</div> 
					<div class="row">
					    <div class="col-md-11">
					        <label>*Suggestion for new Parts/Kit Development/other details:-</label>
					    </div>
					</div> 
					<div class="row">
					    <div class="col-md-12">
					        <textarea name="suggestion"></textarea>
					    </div>
					</div>
					<div class="row">
					    <div class="col-md-11">
					        <label>All fields are mandatory else will be rejected</label>
					    </div>
					</div><br><br>
					<div class="row">
					    <div class="col-md-4">
					       <div id="sig1"></div>
					       <label>Signature of Mechanic</label>
								<p style="clear: both;"><a id="clear1">Clear</a> </p>
					        <!-- <canvas id="sigmachanic" width="400" height="200">Your browser doesn't support signing</canvas> -->
					    </div>
					    <div class="col-md-4">
					       <div id="sig2"></div>
					       <label>Signature of Mechanic</label>
								<p style="clear: both;"><a id="clear2">Clear</a> </p>
					        <!-- <canvas id="sigasm" width="400" height="200">Your browser doesn't support signing</canvas> -->
					    </div>
					    <div class="col-md-4">
					       <div id="sig3"></div>
					       <label>Signature of Mechanic</label>
								<p style="clear: both;"><a id="clear3">Clear</a> </p>
					        <!-- <canvas id="sigdistributor" width="400" height="200">Your browser doesn't support signing</canvas> -->
					    </div>
					</div> 
					<div class="row">
					    <div class="col-md-11">
					        <a href="#page7"><input type="button" name="submit" value="Submit"></input></a>
					    </div>
					</div> 
				</form>
			</div>

		</div>


    </div><!-- /content -->
 
	<div data-role="footer" class="footer" data-id="main-footer" data-position="fixed">
		
	</div> 
</div>

<div data-url="panel-responsive-page1" data-role="page" class="jqm-demos ui-responsive-panel" data-title="Power Rewards" id="page7">

    <div data-role="header" class="jqm-header" data-id="main-header">

		<!--<div data-role="navbar" id="topMenu" class="topMenu">
			<ul id="navlist">
				<li><a href="#page1">Power Rewards Program</a></li>
				<li><a href="#page2">Enrollment Conditions</a></li>
				<li><a href="#page3">FAQs</a></li>
				<li><a href="#add-form">Login</a></li>
			</ul>
		</div>-->



	<div class="bs-example">
	    <nav role="navigation" class="navbar navbar-default">
	        <!-- Brand and toggle get grouped for better mobile display -->
	        <div class="navbar-header">
	            <button type="button" data-target="#navbarCollapse7" data-toggle="collapse" class="navbar-toggle navbar_mob_toggle">
	                <span class="sr-only">Toggle navigation</span>
	                <span class="icon-bar"></span>
	                <span class="icon-bar"></span>
	                <span class="icon-bar"></span>
	            </button>
	            <a href="index.html" title="jQuery Mobile Demos home">
	            	<img src="img/power_rewards_logo.png" alt="jQuery Mobile">
	            </a>
	        </div>
	        <!-- Collection of nav links, forms, and other content for toggling -->
	        <div id="navbarCollapse7" class="collapse navbar-collapse">
	            <ul class="nav navbar-nav navbar-right">
	                <li ><a href="#page1">Power Rewards Program</a></li>
	                <li><a href="#page2">Enrollment Conditions</a></li>
	                <li ><a href="#page3">FAQs</a></li>
	                <!-- <li><a href="#page6">Registration</a></li> -->
	                <li><a href="#add-form">Login</a></li>
	                
	            </ul>

	            <!-- <ul class="nav navbar-nav navbar-right">
	                <li><a href="#">Login</a></li>
	            </ul> -->
	        </div>
	    </nav>
	</div>






    	<h3>
			<a href="index.html" title="jQuery Mobile Demos home"><img src="img/power_rewards_logo.png" alt="jQuery Mobile"></a>
		</h3>
		
    </div><!-- /header -->



    <div data-role="content" id="content3">

		<div id="disclaimer" style="padding:2% 2%">
			<span class='spanclass' style="font-size:150%;">Welcome</span>



			<p><b>Dear Partners,</b></p>
			<img src="img/space.png" alt="jQuery Mobile">

			<p>We would like to thank you for the trust and support you have extended to us over the years. We are today, the most preferred brand in the country and leader in <b>AUTOMOTIVE INDUSTRY</b> as a result of your constant support.</p>
			<img src="img/space.png" alt="jQuery Mobile">

			<p>In appreciation of your co-operation, we are pleased to introduce to you <b>POWER REWARDS 'BAJAJ CV LOYALTY	PROGRAME'</b>- an exclusive programme designed for your benefit. In this new programme, we would like to continue offering the value and rewards that you truly deserve.</p>
			<img src="img/space.png" alt="jQuery Mobile">

			<p>As a member of <b>POWER REWARDS</b> Program, you can now enjoy a host of privileges:- Earn points of every genuine spare parts you purchase which are later used for redeeming Exciting gifts. All you have to do is send an SMS to a uniwue number by SMS accumulate points.</p>
			<img src="img/space.png" alt="jQuery Mobile">

			<p>To get you off to a flying start, we present to you a pre-aproved membership. Wishing you to all the best to reach your first landmark of 100 points and start claiming your gifts.</p> 
			<img src="img/space.png" alt="jQuery Mobile">

			<p>Start sending your SMSs today, and enjoy the benefits.</p> 
			<img src="img/space.png" alt="jQuery Mobile">

			<p>For more information on how the programme works, kindly read on.</p> 
			<img src="img/space.png" alt="jQuery Mobile">

			<p>Best Regards</p> 
			<img src="img/space.png" alt="jQuery Mobile">

			<p><b>Bajaj Genuine Parts - CV Team</b><br/>Bajaj Auto Limited<br/>Pune</p>

		</div>


    </div><!-- /content -->
 
	<div data-role="footer" class="footer" data-id="main-footer" data-position="fixed">
		
	</div> 
</div>