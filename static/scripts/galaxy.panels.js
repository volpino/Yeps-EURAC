function ensure_dd_helper() {
    // Insert div that covers everything when dragging the borders
    if ( $( "#DD-helper" ).length == 0 ) {
        $( "<div id='DD-helper'/>" ).css( {
            background: 'white', opacity: 0, zIndex: 9000,
            position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' 
        } ).appendTo( "body" ).hide();
    }
}

function make_left_panel( panel_el, center_el, border_el ) {
    var hidden = false;
    var saved_size = null;
    // Functions for managing panel
    var resize = function( x ) {
        var oldx = x;
        if ( x < 0 ) x = 0;
        $( panel_el ).css( "width", x );
        $( border_el ).css( "left", oldx );
        $( center_el ).css( "left", x+7 );
        // ie7-recalc.js
        if ( document.recalc ) { document.recalc() };
    };
    var toggle = function() {
        if ( hidden ) {
            $( border_el ).removeClass( "hover" );
            $( border_el).animate( {left: saved_size }, "fast" );
            $( panel_el ).css( "left", - saved_size ).show().animate( { "left": 0 }, "fast", function () {
                resize( saved_size );
                $( border_el ).removeClass( "hidden" );
            });
            hidden = false;
        } else {
            saved_size = $( border_el ).position().left;
            // Move center
            $( center_el ).css( "left", $(border_el).innerWidth() );
            if ( document.recalc ) { document.recalc() };
            $( border_el).removeClass( "hover" );
            $( panel_el ).animate( { left: - saved_size }, "fast" );
            $( border_el ).animate( { left: -1 }, "fast", function() {
                $( this ).addClass( "hidden" );
            });
            hidden = true;
        }
    };
    // Connect to elements
    $( border_el ).hover( 
        function() { $( this ).addClass( "hover" ) },
        function() { $( this ).removeClass( "hover" ) }
    ).bind( "dragstart", function( e ) {
        $( '#DD-helper' ).show();
    }).bind( "dragend", function( e ) {
        $( '#DD-helper' ).hide();
    }).bind( "drag", function( e ) {
        x = e.offsetX;
        // Limit range
        x = Math.min( 400, Math.max( 100, x ) );
        // Resize
        if ( hidden ) {
            $( panel_el ).css( "left", 0 );
            $( border_el ).removeClass( "hidden" );
            hidden = false;
        }
        resize( x );
    }).bind( "dragclickonly", function( e ) {
        toggle();
    }).find( "div" ).show();
    var force_panel = function( op ) {
        if ( ( hidden && op == 'show' ) || ( ! hidden && op == 'hide' ) ) { 
            toggle();
        }
    }
    return { force_panel: force_panel };
};

function make_right_panel( panel_el, center_el, border_el ) {
    var hidden = false;
    var hidden_by_tool = false;
    var saved_size = null;    
    var resize = function( x ) {
        $( panel_el ).css( "width", x );
        $( center_el ).css( "right", x+9 );
        $( border_el ).css( "right", x ).css( "left", "" )
        // ie7-recalc.js
        if ( document.recalc ) { document.recalc() };
    };
    var toggle = function() {
        if ( hidden ) {
            $( border_el).removeClass( "hover" );
            $( border_el ).animate( { right: saved_size }, "fast" );
            $( panel_el ).css( "right", - saved_size ).show().animate( { "right": 0 }, "fast", function () {
                resize( saved_size );
                $( border_el ).removeClass( "hidden" )
            });
            hidden = false;
        }
        else
        {
            saved_size = $(document).width() - $( border_el ).position().left - $(border_el).outerWidth();
            // Move center
            $( center_el ).css( "right", $(border_el).innerWidth() + 1 );
            if ( document.recalc ) { document.recalc() };
            // Hide border
            $( border_el ).removeClass( "hover" );
            $( panel_el ).animate( { right: - saved_size }, "fast" );
            $(  border_el ).animate( { right: -1 }, "fast", function() {
                $( this ).addClass( "hidden" )
            });
            hidden = true;
        }
        hidden_by_tool = false;
    };
    var handle_minwidth_hint = function( x ) {
        var space = $( center_el ).width() - ( hidden ? saved_size : 0 );
        if ( space < x )
        {
            if ( ! hidden ) {
                toggle();
                hidden_by_tool = true
            }
        } else {
            if ( hidden_by_tool ) {
                toggle();
                hidden_by_tool = false;
            }
        }
    };
    $( border_el ).hover( 
        function() { $( this ).addClass( "hover" ) },
        function() { $( this ).removeClass( "hover" ) }
    ).bind( "dragstart", function( e ) {
        $( '#DD-helper' ).show();
    }).bind( "dragend", function( e ) {  
        $( '#DD-helper' ).hide();
    }).bind( "drag", function( e ) {
        x = e.offsetX;
        w = $(window).width(); 
        // Limit range
        x = Math.min( w - 100, x );
        x = Math.max( w - 400, x );
        // Resize
        if ( hidden ) {
            $( panel_el ).css( "right", 0 );
            $( border_el ).removeClass( "hidden" );
            hidden = false;
        }
        resize( w - x - $(this).outerWidth() );
    }).bind( "dragclickonly", function( e ) {
        toggle();
    }).find( "div" ).show();
    var force_panel = function( op ) {
        if ( ( hidden && op == 'show' ) || ( ! hidden && op == 'hide' ) ) { 
            toggle();
        }
    }
    return { handle_minwidth_hint: handle_minwidth_hint, force_panel: force_panel };
};

// Modal dialog boxes

function hide_modal() {
    $(".dialog-box-container" ).fadeOut( function() {
        $("#overlay").hide();
        $( ".dialog-box" ).find( ".body" ).children().remove();
    } );
};

function show_modal( title, body, buttons, extra_buttons ) {
    if ( title ) {
        $( ".dialog-box" ).find( ".title" ).html( title );
        $( ".dialog-box" ).find( ".unified-panel-header" ).show(); 
    } else {
        $( ".dialog-box" ).find( ".unified-panel-header" ).hide();   
    }
    var b = $( ".dialog-box" ).find( ".buttons" ).html( "" );
    if ( buttons ) {
        $.each( buttons, function( name, value ) {
            b.append( $( '<button/>' ).text( name ).click( value ) );
            b.append( " " );
        });
        b.show();
    } else {
        b.hide();
    }
    var b = $( ".dialog-box" ).find( ".extra_buttons" ).html( "" );
    if ( extra_buttons ) {
        $.each( extra_buttons, function( name, value ) {
            b.append( $( '<button/>' ).text( name ).click( value ) );
            b.append( " " );
        });
        b.show();
    } else {
        b.hide();
    }
    if ( body == "progress" ) {
        body = $( "<img src='../images/yui/rel_interstitial_loading.gif')' />" );
    }
    $( ".dialog-box" ).find( ".body" ).html( body );
    if ( ! $(".dialog-box-container").is( ":visible" ) ) {
        $("#overlay").show();
        $(".dialog-box-container").fadeIn()
    }
};
    
function show_in_overlay( options ) {
    var width = options.width || '600';
    var height = options.height || '400';
    var scroll = options.scroll || 'auto';
    $("#overlay-background").bind( "click.overlay", function() {
        hide_modal();
        $("#overlay-background").unbind( "click.overlay" );
    });
    show_modal( null, $("<div style='margin: -5px;'><iframe style='margin: 0; padding: 0;' src='" + options.url + "' width='" + width + "' height='" + height + "' scrolling='" + scroll + "' frameborder='0'></iframe></div>" ) );
}
    
// Tab management
	
$(function() {
    $(".tab").each( function() {
        var submenu = $(this).children( ".submenu" );
        if ( submenu.length > 0 ) {
            if ( $.browser.msie ) {
                // Vile IE iframe hack -- even IE7 needs this
                submenu.prepend( "<iframe style=\"position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; filter:Alpha(Opacity='0');\"></iframe>" );
            }
            $(this).hover( function() { submenu.show(); }, function() { submenu.hide(); } );
            submenu.click( function() { submenu.hide(); } );
        }
    });
});

function user_changed( user_email, is_admin ) {
    if ( user_email ) {
        $(".loggedin-only").show();
        $(".loggedout-only").hide();
        $("#user-email").text( user_email );
        if ( is_admin ) {
            $(".admin-only").show();
        }
    } else {
        $(".loggedin-only").hide();
        $(".loggedout-only").show();
        $(".admin-only").hide();
    }
}