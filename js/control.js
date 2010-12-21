control = {

  apiUrl: '',
  blocks: {},
  current_block: 1, //  The current highest block that we know about
  reading_block: 1, //  The block that we are currently reading
  target_block: 1,  //  The block we want to scroll too
  paused: false,    //  shows if we don't want to automatically scroll the screen
  

  init: function() {
    this.current_block = current_block;
    this.apiUrl = apiUrl;
    this.blocks = blocks;
    
    $.each(this.blocks, function(index, block) {
      control.add_block(block);
    })
    
    control.util.set_max_width();
    control.util.move_top();

    $(window).resize(function() {
      control.util.resize_window();
    });

    $(window).scroll(function() {
      control.util.start_scroll();
    });

    $(window).mousedown(function() {
      control.util.set_mouse_down(true);
    });

    $(window).mouseup(function() {
      control.util.set_mouse_down(false);
    });

    setTimeout(control.get_data, 60000);


    if(navigator.platform == 'iPad' || navigator.platform == 'iPhone' || navigator.platform == 'iPod')
    {
         $("header#bunting").css("position", "static");
    };
  },
  
  get_data: function() {
    
    if (this.apiUrl == '') return;
    
    $.get('/api/gu.get.blocks' + this.apiUrl.replace('http://content.guardianapis.com','') + '/' + (control.current_block), function(json) {
      var min_block = 99999;
      var max_block = 0;
      var i_can_haz_blocks = false;
      
      $.each(json, function(index, value) {
        if (index > max_block) max_block = index;
        if (index < min_block) min_block = index;
        i_can_haz_blocks = true;
      })
      
      if (i_can_haz_blocks) {
        for (var n = min_block; n <= max_block; n++) {
          
          //  Note, there maybe blocks missing between the lowest and highest
          //  block, we can't assume that we have them all.
          if (n in json) {
            control.add_block(json[n]);
          }
        }

        //  If we got some new blocks then we need to move the current block
        //  to the highest value we have
        control.current_block = max_block;
        
        //  Also, if we are not paused, then we want to move onto the next
        //  valid block within the ones we have just been passed that's higher
        //  than the current reading block
        for (var n = min_block; n <= max_block; n++) {
          if (n in json && n > control.reading_block) {
            control.reading_block = n;
            control.util.scroll_to_block(control.reading_block);
          }
        }
  
      }
  
    })
    setTimeout(control.get_data, 60000);
  },
  
  add_block: function(block) {
    
    if (block.block_number != undefined) {
      //  Only add the block if it's not already there
      if ($('div#block_' + block.block_number).length == 0) {
  
        var d = $('<article>').attr('id','block_' + block.block_number);
        d.html(block.contents);
  
        if ('d' in block && block.d != '') {
          var t = $('<time>').attr('datetime', block.d).html(block.display_time);
          d.prepend(t);
        }
  
        $('section#container').append(d);
      }
  
      control.util.set_max_width();
    }
  },
  
  util: {
    
    is_scrolling: false,
    scroll_pos: 0,
    scroll_is_still_counter: 0,
    is_forced_scrolling: false,
    get_scroll_tmr: null,
    scroll_to_block_tmr: null,
    mouse_down: false,
    need_to_move_to_nearest_block: false,
    skip_next_scroll_start: false,
    
    set_max_width: function() {
      var width_of_colum = 460+(40*2);
      var window_less_width_of_column = $(window).width() - width_of_colum-120;
      $('section#container').css('width', ($('section#container article').length * width_of_colum) + window_less_width_of_column);
    },
    
    move_top: function() {
      $('section#main').css('margin-top',$('section#controls').height()+$('header#bunting').height()+20)
    },
    
    resize_window: function() {
      control.util.move_top();
      control.util.set_max_width();
    },





    scroll_to_block: function(block_number) {
     
      //  Say that we are forcing a scroll, and reset
      //  the scroll counter back to 0
      //  while we are forcing a scroll we ignore
      //  all other scoll effects
      control.util.is_forced_scrolling = true;
      control.util.scroll_is_still_counter = 0;


      clearTimeout(control.util.get_scroll_tmr);
      
      if (block_number == undefined) {
        block_number = control.target_block;
      } else {
        control.target_block = block_number;
        control.reading_block = block_number;
      }
    
      // first make sure the the block exists
      var blocks_a = $('section#container article');
      var counter = 0;
      for (var i = 0; i < blocks_a.length; i++) {
        if ($(blocks_a[i]).attr('id') == 'block_' + block_number) {
          var target_position = counter;
          var block_width = $(blocks_a[i]).outerWidth()
          break;
        }
        counter++;
      }
      
      if (target_position == undefined) {
        return;
      }
      
      //  Now get the current scroll position
      var target_position = target_position * block_width;
      var current_pos = $(window).scrollLeft();
      var new_pos = current_pos + ((target_position-current_pos)/20);
      
      if (new_pos > target_position) {
        new_pos = Math.floor(new_pos);
      } else {
        new_pos = Math.ceil(new_pos);
      }

      if (Math.floor(Math.abs(target_position-new_pos)) > 1) {
        $(window).scrollLeft(new_pos);
        clearTimeout(control.util.scroll_to_block_tmr);
        control.util.scroll_to_block_tmr = setTimeout("control.util.scroll_to_block()", 20);
      } else {
        $(window).scrollLeft(target_position);
        control.util.stop_scrolling();
      }

    },





    start_scroll: function() {
      
      //  If we are in the middle of a forced scroll then don't do anything else
      if (control.util.is_forced_scrolling) {
        return;
      }
      
      if (control.util.skip_next_scroll_start == true) {
        control.util.skip_next_scroll_start = false;
        return;
      }
      
      
      control.util.scroll_is_still_counter = 0;       //  <--- Reset the timer that counts how long the position hasn't changed for
      clearTimeout(control.util.scroll_to_block_tmr); //  <--- Turn the scroll to block off
      clearTimeout(control.util.get_scroll_tmr);      //  <--- Clear out the get scroll tmr, as we're about to kick it off again
      control.util.get_scroll_tmr = setTimeout('control.util.get_scroll_pos()', 100);

    },





    get_scroll_pos: function() {
    
      //  If we are in the middle of a forced scroll then don't do anything else
      if (control.util.is_forced_scrolling) {
        return;
      }

      if (parseInt($(window).scrollLeft()) == control.util.scroll_pos) {
        control.util.scroll_is_still_counter++;
      }
      
      //  record the current position, so we can compare it next time
      control.util.scroll_pos = $(window).scrollLeft();
        
      if (control.util.scroll_is_still_counter > 10) {
        control.util.need_to_move_to_nearest_block = true;
        if (control.util.mouse_down == false) {
          control.util.move_to_nearest_block();
        }
      } else {
        clearTimeout(control.util.get_scroll_tmr);
        control.util.get_scroll_tmr = setTimeout('control.util.get_scroll_pos()', 100);
      }

    },





    stop_scrolling: function() {
      
      control.util.skip_next_scroll_start         = true;
      control.util.is_forced_scrolling            = false;
      control.util.is_scrolling                   = false;
      control.util.scroll_is_still_counter        = 0;
      
      //  Stop the forced scroll timer (this should be stopped anyway)
      clearTimeout(control.util.scroll_to_block_tmr);
      clearTimeout(control.util.get_scroll_tmr);

    },





    set_mouse_down: function(is_down) {

      control.util.mouse_down = is_down;
      
      if (is_down) {
        control.util.stop_scrolling();
      }
      
      if (is_down == false && control.util.need_to_move_to_nearest_block) {
        control.util.move_to_nearest_block();
      }

    },





    move_to_nearest_block: function() {
      
      control.util.need_to_move_to_nearest_block = false;
      
      //  First of all we need to find out the width of a column
      //  and the current scroll position so we can work out which
      //  block we *should* be on for that position
      var column_width = $('section#container article').outerWidth();
      var current_pos = $(window).scrollLeft();
      var block_we_need = Math.ceil((current_pos-(column_width/2) - 120) / column_width);
      
      //  Now we know the block position lets grab it from the array thing
      try {
        var target_block = $($('section#container article')[block_we_need]).attr('id').split('_')[1];
        control.util.scroll_to_block(target_block);
      } catch(er) {
      }

    },
  }

}
