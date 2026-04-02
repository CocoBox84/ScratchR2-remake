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

var accountNavReady = document.createEvent('Event');
accountNavReady.initEvent('accountnavready', true, true);

function setAccountNav(context){
    var template = _.template($('#template-account-nav-logged-out').html());
    if(context['username']){
        // User is logged in
        template = _.template($('#template-account-nav-logged-in').html());
        $(function(){
            var create = $('#project-create');
            create.attr('href', create.attr('href').split('?')[0]);
        });
    }
    $('.account-nav').replaceWith(template(context));

    $(function(){document.dispatchEvent(accountNavReady);});
}
$.ajax({
    url: '/fragment/account-nav.json',
}).done(function (data_json) {
    accountNavContext = JSON.parse(data_json);
    setAccountNav(accountNavContext);
});


}
/*
     FILE ARCHIVED ON 06:05:13 Dec 31, 2014 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 01:12:20 Sep 24, 2025.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  captures_list: 0.878
  exclusion.robots: 0.016
  exclusion.robots.policy: 0.007
  esindex: 0.008
  cdx.remote: 30.999
  LoadShardBlock: 267.444 (3)
  PetaboxLoader3.resolve: 196.088 (3)
  PetaboxLoader3.datanode: 206.653 (4)
  load_resource: 151.28
*/