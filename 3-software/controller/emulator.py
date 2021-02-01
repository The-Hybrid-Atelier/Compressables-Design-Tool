# HAWS Metadata
# uri = "ws://162.243.120.86:3001"
from haws import *
uri = "ws://192.168.1.4:3001"
jws = JSONWebSocketClient("interaction-app", uri)
jws.connect()
jws.send({"event": "pid", "action": "set_setpoint", "value": 132})
# blow = {"api":{"command":"BLOW","params":{}}}
# jws.send(blow)
# jws.send({"api":{"command":"PUMP_ON","params":{"pumpNumber":2, "PWM": 0}}})
# jws.send({"api":{"command":"ALL_PUMP_OFF","params":{"pumpNumber":2, "PWM": 0}}})
# while(True):
# 	pass
jws.close()