function jqesc( myid ) {
  return "#" + myid.replace( /(:|\.|\[|\]|,|=|@)/g, "\\$1" );
};

function supportsImports() {
  return 'import' in document.createElement('link');
}

(function() {
  if ('registerElement' in document
      && 'import' in document.createElement('link')
      && 'content' in document.createElement('template')) {
    // platform is good!
  } else {
    // polyfill the platform!
    var e = document.createElement('script');
    e.src = 'https://cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/0.7.24/webcomponents-lite.min.js';
    document.body.appendChild(e);
  }
})();

var importQueue = {};

function interpTaa(root, macroContext) {
  $(root).find("[taa\\:content]").each(function(){
    var commandTag = $(this);
    var val = commandTag.attr("taa:content");
    var url;
    var resource;

    if (val.indexOf(":")>-1) {
      if (/^(f|ht)tps?:\/\//i.test(val)) {
        // Suppose it is whole specification already
      } else {
        var pref = val.split(":");
        // Find prefix attr containing foo: substring.
        var pref_tag = commandTag.closest(`[prefix*=${pref[0]}:]`);
        var s = pref_tag.attr("prefix");
        s = s.split(`${pref[0]}: `)[1].trim().split(" ")[0].trim();
        val=s+pref[1];
      }
    };
    if (val.indexOf("#")>-1) {
      var res = val.split("#");
      url=res[0];
      resource=res[1];
    } else {
      url=val;
      resource="";
    }

    function commandFunction() {
      var imp = this;
      var import_ = imp.import;
      var contents;
      if (import_ != undefined) {
        contents = $(import_);
      } else {
        contents = macroContext;
      }

      if (resource=="competence-list") {
        console.log("Here");

      };

      var rc = contents.find(`${jqesc( resource )}`).clone();

      if (rc.length>0) {
        console.log("Importing " + resource);
        commandTag.empty();
        console.log(rc);
        commandTag.append(rc);
        commandTag.removeAttr("taa:content");
        commandTag.attr("taa:content-expanded", val);
        interpTaa(commandTag, macroContext); // Try to find in calling context
        interpTaa(commandTag, contents);     // Try to find local
      } else {
        console.log("Not Found in import ", resource, url);
      }
    }

    if (url=="") {
      macroContext.each(commandFunction);
    } else {
      var _imp = importQueue[url];

      if (_imp == undefined) {

        console.log("Loading "+ url);

        var link = document.createElement('link');
        link.rel = 'import';
        link.href = url;
        link.setAttribute('async', ''); // make it async!
        document.head.appendChild(link);

        var import_link = link;

        importQueue[url] = {imp:import_link, queue:[function(imp) {
          console.log("Continuation main ", val, imp);
          $(imp).each(commandFunction);
        }]};

        import_link.onload=(function(){
          var imp=$(this);
          var qe = importQueue[url];
          if (qe != undefined) {
            qe.queue.forEach(function(item){
              console.log("Imp-watch", item, this);
              item(this);
            }, qe.imp);
            qe.queue=[];
          };
        });

        import_link.onerror=(function(event){
          console.log('Error loading import: ' + event.target.href);
        });

      } else {
        var import_old = _imp.imp;
        var q = _imp.queue;
        if (q.length>0 ) { // Still loading
          q.push(function(imp) {
            console.log("Continuation waiting "+ val);
            $(import_old).each(commandFunction);
          });
        } else { // Already loaded
          console.log("Immediate "+ val);
          $(import_old).each(commandFunction);
        };
      }
    }
  });
};
function generateTableOfContents() {
  var Contents,
      contents,
      newHeading;

  Contents = gajus.Contents;
  contents = Contents({
    articles: $('main').find('h2').not('.nocount').get()
  });

  // Append the generated list element (table of contents) to the container.
  document.querySelector('#tableOfContents').appendChild(contents.list());

  // Attach event listeners:
  contents.eventEmitter().on('change', function () {
    // console.log('User has navigated to <a href=""></a> new section of the page.');
  });

  // Firing the "resize" event will regenerate the table of contents.
  contents.eventEmitter().trigger('resize');
};

function downloadInnerHtml(filename, selector, mimeType) {
  // var elHtml = $(selector)[0].innerHTML;
  var elHtml = document.documentElement.innerHTML;
  var link = document.createElement('a');
  mimeType = mimeType || 'text/html';

  link.setAttribute('download', filename);
  link.setAttribute('href', 'data:' + mimeType + ';charset=utf-8,' + encodeURIComponent(elHtml));
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

var fileName =  'Export.html'; // You can use the .txt extension if you want

// ------------------------  Main function -------
function LODmain(macroButton) {
  $("body").append(`
            <button class="noprint" id="button-medium-editor-switch"><span class="fa fa-editor">Edit</class></button>
                <button class="noprint" id="button-macro-switch"><span class="fa fa-editor">Macro</class></button>
                <button class="noprint" id="button-export-page"><span class="fa fa-editor">Export</class></button>
                    `);
  $("#button-medium-editor-switch").click(function(){
    $("head").append(`
                    <link rel="stylesheet" media="all" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" />
                    <link rel="stylesheet"
                          href="https://cdn.jsdelivr.net/medium-editor/latest/css/medium-editor.min.css"
                          type="text/css" media="screen" charset="utf-8">
                    <!-- FIXME: Add theme reference. -->
                    `);
    var editor = new MediumEditor('.editable');
  });
  $("#button-export-page").on("click", function() {
    downloadInnerHtml(fileName, '.exportable', 'text/html');
  });
  var root = $("html");
  function runMacros() {
      interpTaa(root, root);
      // FIXME: Should I mark non-expanded macros
      generateTableOfContents();
  }
  if (macroButton) {
    $("#button-macro-switch").click(runMacros);
  } else {
    $("#button-macro-switch").addClass("hidden");
    runMacros();
  }
};
