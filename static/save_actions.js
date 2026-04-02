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

"use strict";

function save_action(action, async) {
    return; // Added by sdg, October 2013

    //console.log(action['type']);
    if (typeof csrf !== 'undefined')
        action["csrfmiddlewaretoken"] = csrf //define csrf in the problem template

    if (async == undefined)
        async = true;
    $.ajax({
        type: "POST",
        url: "/log/",
        data: action,
        success: function() { "";}, //prevents dev ajax workaround from complaining
        async: async,
    });
}

function on_navigate_to(url) {
    var action = {
        type: "navigate_to",
        url: url
    };
    save_action(action);
}

function on_navigate_from(url,data) {
    var action = {
        type: "navigate_from",
        url: url,
        dat: JSON.stringify(data)
    };

    // Must be done synchronously to finish
    save_action(action, false);
}

function on_click_remixbar(fromUrl, toUrl, fromProject, toProject) {
    var action = {
        type: "click_remixbar",
        fromUrl: fromUrl,
        toUrl: toUrl,
        fromProject: fromProject,
        toProject: toProject
    };

    save_action(action, false);
}

function on_click_remixes(fromUrl, toUrl, project) {
    var action = {
        type: "click_remixes",
        fromUrl: fromUrl,
        toUrl: toUrl,
        project: project
    };
    save_action(action);
}

function on_click_projectbox(root, fromUrl, toUrl, project) {
    var action = {
        type: "click_projectbox",
        root: root,
        fromUrl: fromUrl,
        toUrl: toUrl,
        project: project
    };
    save_action(action, false);
}

function on_click_remixtree(root, fromUrl, toUrl, project) {
    var action = {
        type: "click_remixtree",
        root: root,
        fromUrl: fromUrl,
        toUrl: toUrl,
        project: project
    };
    save_action(action);
}


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
  captures_list: 0.655
  exclusion.robots: 0.022
  exclusion.robots.policy: 0.009
  esindex: 0.011
  cdx.remote: 8.139
  LoadShardBlock: 331.385 (3)
  PetaboxLoader3.resolve: 210.981 (4)
  PetaboxLoader3.datanode: 122.15 (4)
  load_resource: 75.39
*/