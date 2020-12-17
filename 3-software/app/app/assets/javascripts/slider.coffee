$ ->

  $('slider').on "touchmove", (e)->
    
    # Calculate relative y position; 0-100; 10 step
    rect = e.currentTarget.getBoundingClientRect()
    yPos = e.originalEvent.touches[0].pageY
    y = (yPos - rect.y)/rect.height
    y = if y > 1 then 1 else y
    y = if y < 0 then 0 else y
    y = 1 - y
    y = parseInt(y * 10) * 10

    
    $(this).parent().find("input").val(y)
    $('slider').trigger("update")
  $('.ui-slider button').click (e)->
    v = $(this).attr('value')
    $(this).parent().find('input').val(0)
    $('slider').trigger("update")
  $('slider').on 'update', (e)->
    y = $(this).parent().find("input").val()
    h = $(this).height()
    border = 3 # from CSS
    $(this).find("island").height((h * (y/100)) - border*2)
  
  $('slider').trigger('update')
