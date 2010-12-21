control = {

  apiUrl: '',
  blocks: {},
  current_block: 1, //  The current highest block that we know about
  reading_block: 1, //  The block that we are currently reading
  target_block: 1,  //  The block we want to scroll too
  paused: false,    //  shows if we don't want to automatically scroll the screen
  myScroll: null,
  

  init: function() {
    this.current_block = current_block;
    this.apiUrl = apiUrl;
    this.blocks = blocks;
    
  
    if (this.apiUrl != '') {
      $.each(this.blocks, function(index, block) {
        control.add_block(block);
      })
    }
    
    control.util.move_top();
    if (this.apiUrl == '') {
      $('footer').css('display', 'none');
      return;
    }

    control.util.resize_window();


    $(window).resize(function() {
      control.util.resize_window();
    });
    
    document.addEventListener('touchmove', function (e) { e.preventDefault(); }, false);
    window.addEventListener('onorientationchange' in window ? 'orientationchange' : 'resize', control.util.resize_window, false);
    
    
    control.myScroll = new iScroll('container', {desktopCompatibility:true, snap:true, vScrollbar: false, scrollbarColorH: 'rgba(255,255,255,0.5)'});
    setTimeout(control.get_data, 60000);

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
            control.util.resize_window();
            control.myScroll = new iScroll('container', {desktopCompatibility:true, snap:true, vScrollbar: false, scrollbarColorH: 'rgba(255,255,255,0.5)'});
            control.myScroll.scrollToPage('last',null,null);
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

      control.util.resize_window();
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
      var window_less_width_of_column = 0;
      $('section#container').css('width', ($('section#container article').length * width_of_colum) + window_less_width_of_column);
    },
    
    set_max_height: function() {
    
      var header_height = $('section#controls').height()+$('header#bunting').height()+20;
      var footer_height = $('footer').outerHeight();
      var new_height = $(window).height() - header_height - footer_height;
      $('section#main').css('height', new_height);
      
    },
    
    move_top: function() {
      $('section#main').css('margin-top',$('section#controls').height()+$('header#bunting').height()+20)
    },
    
    resize_window: function() {
      control.util.move_top();
      control.util.set_max_width();
      control.util.set_max_height();
    }
  }

}
