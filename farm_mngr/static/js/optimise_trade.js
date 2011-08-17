
// clone to deep-copy arrays and objects
Object.prototype.clone = function() {
  var newObj = (this instanceof Array) ? [] : {};
  for (i in this) {
    if (i == 'clone') continue;
    if (this[i] && typeof this[i] == "object") {
      newObj[i] = this[i].clone();
    } else newObj[i] = this[i]
  } return newObj;
};

function $(name) { return document.getElementById(name); }

// preparations done; now to the real thing

var Planets;
var Dists;
var Pairs;
var BestPairing;
var BestCosts = 100000000000;

function start_optimise() {
    var raw_planets = $("planet_input").value;

	$("result").innerHTML = "<h2>Working...</h2>";

	Planets = parse_planets(raw_planets);
	Dists = calc_distances(Planets);
	Pairs = calc_possible_pairs(Planets);

	generate_pairings(Planets.clone(), [], pairing_found);

	var result = "<h2>Best pairing found:</h2><ul>";
	var B = BestPairing;
	var dstSum = 0;

	if (B) {
		for (var i = 0; i < B.length; ++i) {
			result += "<li>" + Dists[B[i][0]][B[i][1]] + ": " + Planets[B[i][0]].name + " <-> " + Planets[B[i][1]].name + "</li>";
			dstSum += Dists[B[i][0]][B[i][1]];
		}
		dstSum /= BestPairing.length;
		result += "</ul><p>With an average distance of " + dstSum + " and an average cost per exploit of " + (900 + dstSum*300) + ".</p>";
	} else {
		result = "<h2>Sorry...</h2><p>The optimiser was unable to find any pairing for those planets:</p><ol>";
		for (var i = 0; i < Planets.length; ++i)
			result += "<li>(" + Planets[i].x + "," + Planets[i].y + ") " + Planets[i].name + " - " + Planets[i].type + "</li>";
		result += "</ol><p>This can have several reasons. Maybe you have an odd number of planets? Or 6 out of 10 planets are Minero planets? Anyway; try to delete or add planets to the above list and try again.</p>";
	}
	$("result").innerHTML = result;

	return false;
}

function pairing_found(pairing) {
	var costs = pairing_costs(pairing);
	var B = pairing;

	if (costs < BestCosts) {
	/*	var result = costs + "VS" + BestCosts + "<ul>";
		for (var i = 0; i < B.length; ++i) {
			result += "<li>" + Dists[B[i][0]][B[i][1]] + ": " + Planets[B[i][0]].name + " <-> " + Planets[B[i][1]].name + "</li>";
		}
		document.write(result + "</ul>");
*/
		BestPairing = pairing;
		BestCosts = costs;
	}
}

// optimiser functions

function parse_planets(raw_planets) {
	var lines = raw_planets.split("\n");
	var re = /[(]?(-?\d+),(-?\d+)[)]?\s+([\w\d-]+)\s+(?:\[[^\]]*\]\s+)?(H|A|X)\w*\s+(M|A|T)/;

	var planets = new Array(); var j = 0;

	var match, x, y, bane, race, type, planet;
	for (var i = 0; i < lines.length; i++) {
		if (lines[i].match(/^\s*#/))
			continue;

		if (match = re.exec(lines[i])) {
			x = parseInt(match[1]); y = parseInt(match[2]);
			name = match[3];
			race = match[4];
			type = match[5];

			if (! name || ! type) 
				continue;

			planet = { x: x, y: y, name: name, race: race, type: type };
			planets[j++] = planet;
		}
	}

	return planets;
}

function calc_distances(p) {
	var dist = new Array();
	for (var i = 0; i < p.length; i++)
		dist[i] = new Array();

	for (var i = 0; i < p.length; i++) {
		for (var j = i+1; j < p.length; j++) {
			var d = Math.floor(Math.sqrt(Math.pow(p[i].x - p[j].x,2) + Math.pow(p[i].y - p[j].y,2)));
			dist[i][j] = d;
			dist[j][i] = d;
		}
	}

	return dist;
}

function calc_possible_pairs(p) {
	var pair = new Array();
	for (var i = 0; i < p.length; i++)
		pair[i] = new Array();

	for (var i = 0; i < p.length; i++) {
		for (var j = i+1; j < p.length; j++) {
			if (p[i].type != p[j].type) {
				pair[i].push(j);
				pair[j].push(i);
			}
		}
	}

	return pair;
}

function pairing_costs(pairing) {
	var costs = 0;
	for (var i = 0; i < pairing.length; i++) {
		costs += 900 + 300 * Dists[pairing[i][0]][pairing[i][1]];	
	}
	return costs;
}


function generate_pairings(planets, pairing, pairing_callback) {
	var p = null; // index of the base planet

	// find first not empty planet
	for (var i = 0; i < planets.length; i++) {
		if (planets[i]) {
			p = i;
			planets[i] = null;
			break;
		}
	}

	// If we have found a pair, i.e. all planets were paired up, we're calling the callback function
	if (p == null) {
		pairing_callback(pairing); 
		return;
	}
	
	for (var k = 0; k < Pairs[p].length; ++k) {
		var i = Pairs[p][k];

		if (planets[i]) {
			var pl = planets.clone();
			pl[i] = null;

			var pr = pairing.clone();
			pr.push([p,i]);

			generate_pairings(pl, pr, pairing_callback);
		}
	}
}


