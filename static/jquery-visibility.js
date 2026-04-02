var _____WB$wombat$assign$function_____ = function(name) {return (self._wb_wombat && self._wb_wombat.local_init && self._wb_wombat.local_init(name)) || self[name]; };
if (!self.__WB_pmw) { self.__WB_pmw = function(obj) { this.__WB_source = obj; return this; } }
{
  let window = _____WB$wombat$assign$function_____("window");
  let self = _____WB$wombat$assign$function_____("self");
  let document = _____WB$wombat$assign$function_____("document");
  let location = _____WB$wombat$assign$function_____("location");
  let top = _____WB$wombat$assign$function_____("top");
  let parent = _____WB$wombat$assign$function_____("parent");
  let frames = _____WB$wombat$assign$function_____("frames");
  let opener = _____WB$wombat$assign$function_____("opener");

/*! http://mths.be/visibility v1.0.5 by @mathias */
;(function(window, document, $, undefined) {

	var prefix,
	    property,
	    // In Opera, `'onfocusin' in document == true`, hence the extra `hasFocus` check to detect IE-like behavior
	    eventName = 'onfocusin' in document && 'hasFocus' in document ? 'focusin focusout' : 'focus blur',
	    prefixes = ['', 'moz', 'ms', 'o', 'webkit'],
	    $support = $.support,
	    $event = $.event;

	while ((property = prefix = prefixes.pop()) != undefined) {
		property = (prefix ? prefix + 'H': 'h') + 'idden';
		//if ($support.pageVisibility = typeof document[property] == 'boolean') {
		//	eventName = prefix + 'visibilitychange';
		//	break;
		//}
	}

	$(/blur$/.test(eventName) ? window : document).on(eventName, function(event) {
		var type = event.type,
		    originalEvent = event.originalEvent,
		    toElement = originalEvent && originalEvent.toElement;
		// To avoid errors from triggered events for which originalEvent is not available.    
		if(!originalEvent){
			return;
		}    
		// If itâ€™s a `{focusin,focusout}` event (IE), `fromElement` and `toElement` should both be `null` or `undefined`;
		// else, the page visibility hasnâ€™t changed, but the user just clicked somewhere in the doc.
		// In IE9, we need to check the `relatedTarget` property instead.
		if (!/^focus./.test(type) || (toElement == undefined && originalEvent.fromElement == undefined && originalEvent.relatedTarget == undefined)) {
			$event.trigger((property && document[property] || /^(?:blur|focusout)$/.test(type) ? 'hide' : 'show') + '.visibility');
		}
	});

}(this, document, jQuery));


}
/*
     FILE ARCHIVED ON 06:05:10 Dec 31, 2014 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 01:25:42 Sep 24, 2025.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  captures_list: 1.441
  exclusion.robots: 0.025
  exclusion.robots.policy: 0.011
  esindex: 0.012
  cdx.remote: 17.763
  LoadShardBlock: 180.153 (3)
  PetaboxLoader3.datanode: 71.198 (4)
  PetaboxLoader3.resolve: 115.104 (3)
  load_resource: 33.912
*/