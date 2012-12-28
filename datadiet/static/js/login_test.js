window.fbAsyncInit = function() {
	FB.init({
		appId      : '426368957414799', // App ID
		channelUrl : '/home/polypatentpending/patent-pending-assets/website/templates/channels.html', // Channel File
		status     : true, // check login status
		cookie     : true, // enable cookies to allow the server to access the session
		frictionlessRequests : true, // enable frictionless requests
		xfbml      : true  // parse XFBML
	});
	// Additional initialization code here

	//Next, find out if the user is logged in
	FB.getLoginStatus(function(response) {
		if (response.status === 'connected') {
			var uid = response.authResponse.userID;
			var accessToken = response.authResponse.accessToken;
			FB.api('/me/picture', function(response) {
				console.log(response);
				$('#picture').html("<img class \"profile_photo_img\" src = \"" + response.data.url + "\">");
			});
			FB.api('/me/', function(info) {
				console.log(info);
				$('#welcome').html("Hello there Mr." + info.last_name);
			});
			
			console.log('User is logged on');
		} else if (response.status === 'not_authorized') {
			//User is logged into facebook but not on your app
			console.log('User is in Facebook but not in your app');
		} else {
			//User is not logged into facebook at all
			console.log('User is not in facebook at all?');
		}
	});
	
		
};
// Load the SDK Asynchronously
(function(d){
	var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0]; if (d.getElementById(id)) {return;}
	js = d.createElement('script'); js.id = id; js.async = true;
	js.src = "//connect.facebook.net/en_US/all.js";
	ref.parentNode.insertBefore(js, ref);
}(document));

