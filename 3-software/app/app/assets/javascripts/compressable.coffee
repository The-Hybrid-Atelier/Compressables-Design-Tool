class window.Compressable
    constructor: (socket)->
      console.log "Compressable"
      @_name = "Generic compressable"
      @_status = "ON"
      @_upper_limit = 255
      @_lower_limit = 0
      @_setpoint = 132
      @_next_setpoint = -1
      @_pressure = 0
      @socket = socket

    send: (event, parameters)->
      msg = {}
      if event
        msg.event = event
      if parameters
        msg.params = parameters
      console.log ">>", msg
      if @socket
        @socket.send msg
   

    Object.defineProperties @prototype, 
      name:
        get: -> @_name
        set: (value)-> 
          @_name = value
          console.log "Loading", @_name
      setpoint:
        get: -> @_setpoint
        set: (value)->
          @_setpoint = parseInt(value)
          if @_setpoint > @_upper_limit
            @_setpoint = @_upper_limit
          else if @_setpoint < @_lower_limit
            @_setpoint = @_lower_limit
          if @_status == "STOPPED"
            $('.setpoint').html("-")
          else
            $('.setpoint').html(@_setpoint.toFixed(0))
          @next_setpoint = 0
          @send "pid",
            set_setpoint: @_setpoint
      status:
        get: -> @_status
        set: (state)->
          if @_status == state then return
          @_status = state
          switch state 
            when "STOPPED"
              $("#controller").addClass("stopped")
              @pre_stop_sp = @_setpoint
              @send("emergency_stop")
              @setpoint = 0
              @next_setpoint = -1
            when "ON"
              $("#controller").removeClass("stopped")
              @setpoint = @pre_stop_sp 
              @send("restart")
          $('.status').html(@_status)
      upper_limit: 
        get: -> parseInt(@_upper_limit)
        set: (value)->
          if @_upper_limit == value then return
          @_upper_limit = if _.isNumber value then parseInt(value) else 255
          
          if @_upper_limit < @lower_limit
            @lower_limit = @_upper_limit

          if @setpoint > @_upper_limit
            @setpoint = @_upper_limit
          
          display = if @_upper_limit == 255 then "-" else @_upper_limit.toFixed(0)
          $('[action="set_ul"] .badge').html(display)
      next_setpoint: 
        get: -> @_next_setpoint
        set: (value)->
          if @_next_setpoint == value then return
          
          @_next_setpoint = parseInt(value)
          setpoint = parseInt(@_next_setpoint + @_setpoint)

          maxed = false
          mined = false
          

          if setpoint > @_upper_limit
            @_next_setpoint = @_upper_limit - @_setpoint
            maxed = true
          else if setpoint < @_lower_limit
            @_next_setpoint = @_lower_limit - @_setpoint
            mined = true

          # -5, 2, 218
          console.log "NSP", parseInt(value), @_next_setpoint, setpoint, @_setpoint
          if @_next_setpoint != 0
            prefix = if parseInt(@_next_setpoint) > 0 then "+ " else ""
            display = "(" + prefix + @_next_setpoint.toFixed(0) + ")"
            $('.next_setpoint').html(display)
          else
            if @_status == "STOPPED"
              $('.next_setpoint').html("-")
            else
              if mined 
                $('.next_setpoint').html("MIN")
              else if maxed
                $('.next_setpoint').html("MAX")
              else
                 $('.next_setpoint').html("-")
            
              

      lower_limit: 
        get: -> parseInt(@_lower_limit)
        set: (value)->
          if @_lower_limit == value then return
          @_lower_limit = if _.isNumber value then parseInt(value) else 0

          if @_lower_limit > @upper_limit
            @upper_limit = @_lower_limit

          if @setpoint < @_lower_limit
            @setpoint = @_lower_limit
          
          display = if @_lower_limit == 0 then "-" else @_lower_limit.toFixed(0)
          $('[action="set_ll"] .badge').html(display)
      pressure: 
        get: -> @_pressure
        set: (value)->
          if @_pressure == value then return
          @_pressure = if _.isNumber value then value else 0
          display = if @_pressure == 0 then "-" else @_pressure.toFixed(0)
          $('.process_value').html(display)