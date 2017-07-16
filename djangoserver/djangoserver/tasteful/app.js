$(function() {
	$("body").css("backgroundColor", "#111714");
});

var FormPane = React.createClass({
	getInitialState: function() {
		return {
			hasimg: false,
			value: "",
			profiles: []
		}
	},
	updated: function(event) {
		this.setState({
			value: event.target.value
		});

//		if(this.state.value == "reddit") {
//			this.setState({hasimg: true});
//		} else {
//			this.setState({hasimg: false});
//		}
	},
	checkIfUsernameExistsInReddit: function(json) {
		if(json) {
			$("body").css({"backgroundColor": "#ff2222"});
			$("body").animate({"backgroundColor": "#ff6600"},2000);
			return;
		}
		var old = this.state.profiles.slice();
		old.push(this.state.value);
		this.setState({
			profiles: old
		});
	},
	onButtonClick: function() {
		var reddit = new RegExp('reddit.com/u/([a-zA-Z0-9]+)');
		var redditresult = reddit.exec(this.state.value);
		$.ajax({
			url: "https://www.reddit.com/api/username_available.json?user=" + redditresult[1],
			type: "GET",
			dataType: "json",
		})
		.done(this.checkIfUsernameExistsInReddit)
//		console.log("pressed");
//		var old = this.state.profiles.slice();
//		old.push(this.state.value);
//		this.setState({
//			profiles: old
//		});
	},
	finalSubmit: function() {
		var reddit = new RegExp('reddit.com/u/([a-zA-Z0-9]+)');
		if(this.state.profiles.length == 0) return;
		var redditresult = reddit.exec(this.state.profiles[0]);
		if( redditresult != null){
			$.ajax({
				url: "../../../submitprofile?username=" + redditresult[0] + "&platform=reddit",
				type: "GET",
				dataType: "json",
			})
			.done(function(json) {
				alert("Score is: " + json.score);
			});
		}
	},
	render: function() {
		var reddit = new RegExp('reddit.com');
//		if(this.state.value == "reddit") {
		if(reddit.exec(this.state.value) != null) {
			$("body").animate({'backgroundColor': "#ff6600"}, 300);
			console.log("ok");
		}
		else {
			$("body").animate({"backgroundColor": "#112017"}, 200);
		}
		return (
			<div>
				<div className="formsection">
					<NiceForm onClick={this.onButtonClick} value={this.state.value} onChange={this.updated} img="fa fa-reddit" hasimg={this.state.hasimg} id="f1" bid="formb" /> 
					<h1>{this.state.value}</h1>
				</div>
				<ProfileListView profiles={this.state.profiles} />
				<br />
				<button onClick={this.finalSubmit} id="finalsubmit">Submit</button>
			</div>
		);
	}
});

var NiceForm = React.createClass({
	render: function() {
		var jsx;
		if(this.props.hasimg) {
			console.log("oops");
			jsx = (
				<div className="niceform">
					<i className={this.props.img}></i> <input value={this.props.value} onChange={this.props.onChange} type="text"></input> <button id={this.props.bid} onClick={this.props.onClick}>Enter</button>
				</div>
			);
		}
		else {
			jsx = (
				<div className="niceform">
					<input value={this.props.value} onChange={this.props.onChange} type="text"></input> <button id={this.props.bid} onClick={this.props.onClick}>Enter</button>
				</div>
			);
		}
		return (
			jsx
		);
	}
});

var ProfileListView = React.createClass({
	render: function() {
		console.log(this.props.profiles);
		var listitems = this.props.profiles.map((profile) => <li>{profile}</li>);
		return (
			<div className="profilelistview">
				<ul>
					{listitems}
				</ul>
			</div>
		);
	}
});

ReactDOM.render(<FormPane />, document.getElementById("app"));
