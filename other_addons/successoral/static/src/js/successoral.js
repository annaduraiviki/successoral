odoo.define('successoral.datetime', function (require) {
	'use strict';
	var website = require('website.website');

	website.if_dom_contains('.datetimepicker', function() {
		$('.datetimepicker').datetimepicker({
			format: 'DD-MM-YYYY',
		});
	});
});