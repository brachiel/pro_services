
function process_task(task) {
	$.ajax({
		url: data_base_url + task + '/',
		success: function(data) {
			if (data == true) {
				$("#" + task).removeClass("waiting").addClass("success");
			} else {
				$("#" + task).removeClass("waiting").addClass("failure");
			}

			task_done();
		},
		error: function() {
			$("#" + task).removeClass("waiting").addClass("failure");

			task_done();
		}
	});

	// We immediatly start the next task, without waiting for the old one to finish.
	process_next_task();
}

var tasks_active = 0;
function process_next_task() {
	if (tasks.length > 0) {
		var task = tasks.shift();
	
		$("#" + task).addClass("waiting");
		tasks_active++;
		setTimeout("process_task('" + task + "')", time_to_wait*1000);
	}
}

function task_done() {
	tasks_active--;
	if (tasks_active <= 0) {
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
		tasks_active = 1;
		process_task(task);
	} else {
		error("There was an error initialising the data gatherer script.");
	}
}

