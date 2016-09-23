//Set up isotope
$( function() {
  
  $('.grid').isotope({
    itemSelector: '.grid-item',
	isInitLayout: true,
	masonry: {
      columnWidth: 100,
	  //This gutter property sets the width between elements in the isotope layout
	  gutter: 8,
    }
  });
  
});

//Make the :contains selector case-insensitive
$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

$(document).ready(function() {
	$('.grid').imagesLoaded( function() {
		$('.grid').isotope('layout');
	});
	
	//Make an object to contain the url hash info
	var hash_info = {
	
		hide: [], //an array containing some of ['pictures', 'abstract', 'authors', 'links']
		hide_str: '',
		execute_hide: function(){
			this.hide.forEach(function(elt2, j) {
				var place;
				if(elt2 != 'pictures') {place = '.grid .' + elt2}
				else {place = '.grid img'};
				//console.log(place, "place");
				//uncheck the appropriate boxes
				document.getElementById("hide-" + elt2).checked = false;
				//toggle the correct class
				$(place).toggleClass('no-display');
				$('.grid').isotope('layout');
			});
		},
		
		update_hide: function() {
			var to_hide = [];
			$('.show-hide input:not(:checked)').each(function(i, elt) {
				to_hide.push(elt.id.replace(/^hide-/, ''));
			});
			this.hide = to_hide;
			console.log('this.hide', this.hide);
			if (this.hide) {this.hide_str = 'hide=' + this.hide.join(',') + '&'} 
			else {this.hide_str = ''};
			this.update_hash_str();
		},
		
		filter: '', //a string that's pretty much just what you need
		filter_str: '', 
		execute_filter: function() {
			this.filter.forEach(function(elt, i) {
				$('.select-topics #' + elt).attr('checked', 'true');
			});
			filter();
		},
		update_filter: function() {
			var inclusives = [];
			$('.select-topics input:checked').each( function( i, elem ) {
				inclusives.push( elem.id ); 
			});
			inclusives = inclusives.join(',');
			this.filter = inclusives; 
			this.filter_str = 'filter=' + hash_info.filter + '&';
			this.update_hash_str();
		},
		
		search: '', //a string corresponding to the content of the search box
		search_str: '', 
		search_dom: '', //one of ['titles', 'authors', 'abstracts', 'all']
		search_dom_str: '',
		
		execute_search_dom: function() {
			$('#search').text(this.search);
			switch (hash_info.search_dom) {
				case 'titles': 
					$('#search-titles').attr('checked', 'true');
					break;
				case 'authors': 
					$('#search-authors').attr('checked', 'true');
					break; 
				case 'abstracts': 
					$('#search-abstract').attr('checked', 'true');
					break;
				case 'all': 
					$('#search-all').attr('checked', 'true');
					break;
			};	
		},
		
		update_search: function() {
			this.search = $('#search').val();
			this.search_str = 'search=' + hash_info.search.split(' ').join('+');
			search_dom = $('#search-select input:checked').attr('id');
			search_dom = search_dom.replace(/^search-/, '');
			this.search_dom = search_dom;
			if (this.search_dom == 'all') {this.search_dom_str = ''}
			else {this.search_dom_str = 'search_dom=' + hash_info.search_dom + '&';};
			this.update_hash_str();
		},
		
		update_hash_str: function(){
			hash = '#';
			if (this.hide.length != 0) {hash += this.hide_str};
			if (this.filter) {hash += this.filter_str};
			if (this.search_dom) {hash += this.search_dom_str};
			if (this.search) {hash += this.search_str};
			if (hash.charAt(hash.length -1) == '&') {hash = hash.slice(0, -1)};
			console.log(hash);
			window.location.hash = hash;
		}
	};
	
	//parse the url hash
	if (window.location.hash) {
		var hash = window.location.hash;
		var hash = hash.slice(1);
		hash_array = hash.split('&');
		hash_array.forEach(function(elt, i) {
			//deal with the hide section of the url
			if (/^hide=/.test(elt)) {
				to_hide = elt.replace(/^hide=/, '');
				//update object
				hash_info.hide_str = to_hide;
				hash_info.hide = hash_info.hide_str.split(','); 
				console.log('hash_info.hide', hash_info.hide);
				hash_info.execute_hide();
			};
			
			if (/^filter=/.test(elt)) {
				//console.log('filter match');
				to_filter = elt.replace(/^filter=/, ''); 
				hash_info.filter_str = to_filter;
				hash_info.filter = to_filter.split(',');
				hash_info.execute_filter();
			};
			
			if (/^search_dom=/.test(elt)) {
				domain = elt.replace(/^search_dom=/, '');
				console.log('domain', domain);
				hash_info.search_dom_str = domain;
				hash_info.search_dom = domain;
				hash_info.execute_search_dom();
			};
			
			if (/^search=/.test(elt)) {
				//console.log('search match');
				to_search = elt.replace(/^search=/, '');
				hash_info.search_str = to_search;
				hash_info.search = to_search.split('+').join(' ');
				//console.log('search query', hash_info.search);
				$('#search').val(hash_info.search);
				check_search_box();
			};
			});
			
		};
	
	
	//Filter based on show/hide textboxes
	$('#hide-abstract').change(function () {
		$('.grid .abstract').toggleClass('no-display');
		$('.grid').isotope('layout');
		hash_info.update_hide();
	});
	
	$('#hide-pictures').change(function () {
		$('.grid img').toggleClass('no-display');
		$('.grid').isotope('layout');
		hash_info.update_hide();
	});
	
	$('#hide-authors').change(function () {
		$('.grid .authors').toggleClass('no-display');
		$('.grid').isotope('layout');
		hash_info.update_hide();
	});
	
	$('#hide-links').change(function () {
		$('.grid .links').toggleClass('no-display');
		$('.grid').isotope('layout');
		hash_info.update_hide();
	});
	
	
	function filter() {
		//This function filters based on the selected checkboxes
		// map input values to an array
		var inclusives = [];
		// inclusive filters from checkboxes
		$('.select-topics input').each( function( i, elem ) {
				 // if checkbox, use value if checked
				if ( elem.checked ) {
					inclusives.push( elem.value ); 
				}
			});
		// combine inclusive filters
			console.log('inclusives', inclusives);
			var filterValue = inclusives.length ? inclusives.join(', ') : '*';
			$('.grid').isotope({ filter: filterValue })
			$('.grid').isotope('layout');
			hash_info.update_filter();
		};
	
	 // filter with selects and checkboxes
	var $checkboxes = $('.select-topics input');
	$checkboxes.change( function() {filter()});
	
	//Add a search box
	//Define a new function that delays an action until a certain event has stopped firing
	var delay = (function(){
		var timer = 0;
		return function(callback, ms){
		clearTimeout (timer);
		timer = setTimeout(callback, ms);
		};
	})();
	
	//Checks where to search
	$('#search-select input[type=radio]').change(function() {
		if ($('#search').val()) {check_search_box();};
	});

	//this checks the search box
	function check_search_box() {
		var location = $('input[name=search-option]:checked').val();
		console.log('location', location);
		$('.grid-item').css("display", "block");
		var content = $('#search').val();
		var $toHide = $();
		if (location == '') {
			$toHide = $(".grid-item").not(":contains('" + content + "')");
		}
		else {
			$toHide = $(".grid-item " + location).not(":contains('" + content + "')").parent(".grid-item");
		}
		$toHide.css("display", "none");
		$('.grid').isotope('layout');
		hash_info.update_search();
	}
	
	//This binds the search function to the search box
	$('#search').bind('change keypress  keyup change', function () {
		delay(function(){
			check_search_box();
	}, 500 );
	});

});