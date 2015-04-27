// odoo.define('successoral.datetime', function (require) {
// 	'use strict';
// 	var website = require('website.website');

// 	website.if_dom_contains('.datetimepicker', function() {
// 		$('.datetimepicker').datetimepicker({
// 			format: 'DD-MM-YYYY',
// 		});
// 	});
// });
(function () {
    'use strict';
    
    openerp.website.ready().done(function() {


		website.if_dom_contains('.datetimepicker', function() {
			$('.datetimepicker').datetimepicker({
				viewMode: 'years',
				format: 'DD-MM-YYYY',
			});
		});
	});
});