
var current_map;
var race = {long: ['Human','Azterk','Xillor'], short: ['H','A','X']};
var ptype = {long: ['Agro','Minero','Techno'], short: ['A','M','T']};

/* is called on document.ready */
function map_init() {
	$('#content').append('<div id="log"></div>');

	$('#fixed_panel').append('<div id="territory_ctrl">Territories: </div>');

	$.each(territories, function(alliance){
		$('<span id="territory_ctrl_'+alliance+'">'+alliance+' </span>').mouseover(function(){
			$('.'+alliance).addClass('territory_highlight');
			$('#territory_ctrl_'+alliance).css('color', 'red');
		}).mouseout(function(){
			$('.'+alliance).removeClass('territory_highlight');
			$('#territory_ctrl_'+alliance).css('color', 'inherit');
		}).appendTo($('#territory_ctrl'));
	});

	$('#fixed_panel').append('<div id="planet_info"></div>');
}

function log(message) {
	$("#log").append('<p style="padding:0;margin:0">' + message + '</p>');
}

function map_show(sc) {
	if (! sc) sc = "SC14";

	$.getJSON(base_map_url + 'sector/', {min_y: -881, max_y: -835},
		function(data) { create_base_map(deserialise_planets(data)); });
}

function deserialise_planets(data) {
	var planet_data = {};
	$.each(data, function(i, obj){
		if (obj.model != 'farm_mngr.planet')
			return;

		obj.fields.id = obj.pk;
		planet_data[obj.pk] = obj.fields;
	});
	return {planets: planet_data};
}

function show_planet_info(planet_id) {
	p = current_map.planets[planet_id];

	$('#planet_info').html('<ul id="planet_info_list"></ul>');
	
	$('#planet_info_list').append('<li>Name: <strong>'+p.name+'</strong></li>');
	$('#planet_info_list').append('<li>Tag: '+p.publictag+'</li>');
	$('#planet_info_list').append('<li>Civ: '+p.civlevel+'</li>');
	$('#planet_info_list').append('<li>Race: '+race.long[p.race]+'</li>');
	$('#planet_info_list').append('<li>Prod: '+ptype.long[p.prod]+'</li>');
	$('#planet_info_list').append('<li>Activity: '+p.activity+'</li>');

}

function hide_planet_info() {
	$('#planet_info').html("");
}

function create_base_map(data) {
	data.max_x = 0; data.min_x = 0; data.min_y = 0; data.max_y = -1000;
	$.each(data.planets, function(id,planet) {
		data.min_x = Math.min(data.min_x, planet.x);
		data.max_x = Math.max(data.max_x, planet.x);
		data.min_y = Math.min(data.min_y, planet.y);
		data.max_y = Math.max(data.max_y, planet.y);
	});
	current_map = data;

	$("#map").html('<table id="maptable"></table>');

	/* create basic map frame */
	for (var y = data.min_y; y <= data.max_y; y++) {
		$('#maptable').append('<tr class="coords" id="map_coords_' + y + '"></tr>');
		$('#maptable').append('<tr class="planet" id="map_' + y + '"></tr>');
		for (var x = data.min_x; x <= data.max_x; x++) {
			$('#map_coords_' + y).append('<td class="coords invisible" id="map_coords_'+y+'_'+x+'">('+x+','+y+')</td>');
			$('#map_' + y).append('<td class="planet invisible" id="map_'+y+'_'+x+'" />');

			$.each(territories, function(alliance, t){
				if (t[0] >= y && x <= t[1] && y >= t[2] && t[3] <= x) {
					$('#map_coords_'+y+'_'+x).addClass("not_pro").addClass(alliance);
					$('#map_'+y+'_'+x).addClass("not_pro").addClass(alliance);
				}
			});
		}
	}

	$.each(data.planets, function(planet_id, planet) {
		text = planet.name;
		$('<div id="map_planet_'+ planet_id +'" class="planet">'+text+'</div>').mouseover(
				function(){show_planet_info(planet_id)}).mouseout(hide_planet_info).appendTo($('#map_' + planet.y + '_' + planet.x));

		if (planet.publictag == 'Pro14')
			$('#map_planet_'+planet_id).css('color','blue');
		else if (planet.publictag == 'Pro-T')
			$('#map_planet_'+planet_id).css('color','cyan');
		else if (planet.publictag == 'Pro')
			$('#map_planet_'+planet_id).css('color','red');
		else if (planet.publictag == 'Pro-M')
			$('#map_planet_'+planet_id).css('color','red');
		else if (planet.publictag == 'Pro-N')
			$('#map_planet_'+planet_id).css('color','red');

		$('#map_coords_' + planet.y + '_' + planet.x).removeClass('invisible');
		$('#map_' + planet.y + '_' + planet.x).removeClass('invisible');
	});
}

