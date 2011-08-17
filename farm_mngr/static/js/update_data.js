
function process_task(task) {
	$.ajax({
		url: data_base_url + task + '/',
		success: function(data) {
			if (data == true) {
				$("#" + task).removeClass("waiting").addClass("success");
			} else {
				$("#" + task).removeClass("waiting").addClass("failure");
			}
			process_next_task();
		},
		error: function() {
			$("#" + task).removeClass("waiting").addClass("failure");
			process_next_task();
		}
		});
}

function process_next_task() {
	if (tasks.length > 0) {
		var task = tasks.shift();
	
		$("#" + task).addClass("waiting");
		setTimeout("process_task('" + task + "')", time_to_wait*1000);
	} else {
		$("#done").css("display", "block");
	}
}

function error(msg) {
	$("#error").css('display','block');
	$("#error").html(msg);
}

function init_data_gathering() {
	if (tasks.length > 0 && data_base_url.length > 0 && time_to_wait > 0) {
		task = tasks.shift();
		$("#" + task).addClass("waiting");
		process_task(task);
	} else {
		error("There was an error initialising the data gatherer script.");
	}
}

