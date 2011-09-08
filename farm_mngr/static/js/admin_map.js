
var current_map;
var race = {long: ['Human','Azterk','Xillor'], short: ['H','A','X']};
var ptype = {long: ['Agro','Minero','Techno'], short: ['A','M','T']};

/* is called on document.ready */
function map_init() {
	$('#content').append('<div id="log"></div>');

	$('#map_ctrl_form').append('<ul id="territory_ctrl">Territories: </ul>');

	$.each(territories, function(alliance){
		$('<li><input type="checkbox" id="territory_ctrl_'+alliance+'">'+alliance+'</input></li>').appendTo($('#territory_ctrl'));
		$('#territory_ctrl_' + alliance).change(function(){
			if (this.checked) 
				$('.'+alliance).addClass('territory_highlight');
			else 
				$('.'+alliance).removeClass('territory_highlight');
		});

	});

	$('#map_ctrl_form').append('<div id="farm_data"></div>');
	$('#map_ctrl_form').append('<div id="unit_data"></div>');
	map_menu_reset();

	$('#fixed_panel').append('<div id="planet_info"></div>');
}
function map_menu_reset() {
	$('#farm_data').html('<button onclick="javascript:load_farm_data();">Load farm data</button>');
	$('#unit_data').html('<button onclick="javascript:load_unit_data();">Load fleet data</button>');
	$('#planet_info').html();
}

function log(message) {
	$("#log").append('<p style="padding:0;margin:0">' + message + '</p>');
}

function map_show(sc) {
	var presets = {"SC14 core": { min_y: -875, max_y: -862, min_x: -6, max_x: 5 }};

	add_sc = function(name, center){ presets[name] = {min_y: center-32, max_y: center+32, min_x: -32, max_x: 32} };
	add_sc("SC5", -264);
	add_sc("SC10", -594);
	add_sc("SC14", -858);
	
	if (! presets[sc]) sc = "SC14 core";

	$.getJSON(base_map_url + 'sector/', presets[sc],
		function(data) { create_base_map(deserialise_planets(data)); });
}

function load_farm_data() {
	$.getJSON(base_map_url + 'farms/', {min_y: current_map.min_y, max_y: current_map.max_y, 
										min_x: current_map.min_x, max_x: current_map.max_x },
		function(data) {
			var frmlst = deserialise_planet_extra_data("farm", data); 
			alert("C" + frmlst);
			process_farm_data(frmlst); 
		});
	
}

function load_unit_data() {
	$.getJSON(base_map_url + 'units/', {min_y: current_map.min_y, max_y: current_map.max_y,
										min_x: current_map.min_x, max_x: current_map.max_x },
		function(data) {
			deserialise_unit_data(data);
			process_unit_data();
		});

}

function deserialise_planets(data) {
	var planet_data = {};
	$.each(data, function(i, obj){
		if (obj.model != 'farm_mngr.planet')
			return;

		obj.fields.id = obj.pk;
		planet_data[obj.pk] = obj.fields;
	});
	return { planets: planet_data, farms: [] };
}

function deserialise_planet_extra_data(name, data) {
	$.each(data, function(planet_id, obj) {
		if (typeof(planet_id) == "string") planet_id = parseInt(planet_id);
		
		if (planet_id in current_map.planets) {
			if (! ("extra" in current_map.planets[planet_id]))
				current_map.planets[planet_id]["extra"] = {};

			current_map.planets[planet_id]["extra"][name] = obj;
		}
	});

	return data;
}

function deserialise_unit_data(units) {
	var unitfunc = function(type, unit) {
		planet_id = unit.planet;
		if (typeof(planet_id) == "string") planet_id = parseInt(planet_id);

		if (unit.planet in current_map.planets) {
			if (! ("extra" in current_map.planets[planet_id]) )
				current_map.planets[planet_id]["extra"] = {"gas": [], "fleets": []};
			if (! (type in current_map.planets[planet_id]) )
				current_map.planets[planet_id]["extra"][type] = [];
			current_map.planets[planet_id]["extra"][type].push(unit.fleetid);
			if (! current_map.players) current_map.players = {};
			if (! (unit.owner in current_map.players))
				current_map.players[unit.owner] = {"gas": [], "fleets": []};
			else if (! type in current_map.players[unit.owner])
				current_map.players[unit.owner][type] = [];
			current_map.players[unit.owner][type].push(unit.fleetid);
			// Add the unit to the internal unit database
			unit.type = type;
			if (! current_map.units) current_map.units = {};
			current_map.units[unit.fleetid] = unit;
		}
	}

	$.each(units.gas, function(i, gas) { unitfunc("gas", gas)} );
	$.each(units.fleets, function(i, fleets) { unitfunc("fleets", fleets)} );
}

function process_farm_data(farm_list) {
	current_map.farms = farm_list;

	$.each(farm_list, function (planet_id, data) {
		$("#map_planet_" + planet_id).addClass("farm");
	});

	$("#farm_data").html('<input type="checkbox" id="highlight_farms">Highlight farms</input>');
	$("#highlight_farms").change(function(){
		if (this.checked)
			$(".farm").addClass("highlight");
		else
			$(".farm").removeClass("highlight");
	});

}

function process_unit_data() {
	$.each(current_map.units, function (unitid, unit) {
		$("#map_planet_" + unit.planet).addClass("has_" + unit.type);
		if (unit.defend == false)
			$("#map_planet_" + unit.planet).addClass("battle");
	});

	$("#unit_data").html('<input type="checkbox" id="highlight_units">Highlight units</input>');
	$("#unit_data").append('<br /><input type="checkbox" id="highlight_battles">Highlight battles</input>');
	$("#highlight_units").change(function(){
		if (this.checked) {
			$(".has_gas").addClass("highlight");
			$(".has_fleets").addClass("highlight");
		} else {
			$(".has_gas").removeClass("highlight");
			$(".has_fleets").removeClass("highlight");
		}
	});
	$("#highlight_battles").change(function(){
		if (this.checked) {
			$(".battle").addClass("highlight");
		} else {
			$(".battle").removeClass("highlight");
		}
	});
}

function show_planet_info(planet_id) {
	var p = current_map.planets[planet_id];

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
	if (! current_map.players)
		current_map.players = {};

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

