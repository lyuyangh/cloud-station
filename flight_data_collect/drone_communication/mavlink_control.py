from pymavlink import mavutil, mavwp
import socket
import json
from flight_data_collect.drone_communication.mavlink_constants import MAVLINK_MSG_ID_SET_MODE
from flightmonitor.consumers import send_message_to_clients

SERVER_IP = socket.gethostbyname(socket.gethostname())

def get_ack_msg(connect_address:int, mavlink, message_type):
    ack_msg = mavlink.recv_match(type=message_type, timeout=6, blocking=True)
    if ack_msg:
        ack_msg = ack_msg.to_dict()
        ack_msg["droneid"] = connect_address
        ack_msg['result_description'] = mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description
        send_message_to_clients(json.dumps(ack_msg))       
    return ack_msg  

def change_mode(connect_address:int, mode:str)->str:
    try:
        mavlink = mavutil.mavlink_connection(SERVER_IP+':'+connect_address)
        msg = mavlink.wait_heartbeat(timeout=6)
        connect_address = int(connect_address)
        if not msg:
            return {'ERROR': f'No heartbeat from {connect_address} (timeout 6s)', 'droneid':connect_address}
        if mode not in mavlink.mode_mapping():
            return {'ERROR': f'{mode} is not a valid mode. Try: {list(mavlink.mode_mapping().keys())}', 'droneid':connect_address}
        mavlink.set_mode(mode)
        ack_msg = mavlink.recv_match(type='COMMAND_ACK', condition=f'COMMAND_ACK.command=={MAVLINK_MSG_ID_SET_MODE}', 
                                        blocking=True, timeout=6)
        if ack_msg:
            ack_msg = ack_msg.to_dict()
            ack_msg['command'] = 'SET_MODE'
            ack_msg['result_description'] = mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description
            ack_msg['droneid'] = connect_address
            return ack_msg
        else:
            return {'ERROR': 'No ack_msg received (timeout 6s).', 'droneid': connect_address}
    except Exception as e:
        print(e)
        return {'ERROR': 'Set Mode command failed!', 'droneid':connect_address}
    

def set_waypoints(connect_address:int, waypoints:list)->bool:
    '''waypoints should be given in this form:
        [(lat0,lon10,alt0), (lat1,lon1,alt1), ...]'''
    try:
        mavlink = mavutil.mavlink_connection(SERVER_IP+':'+connect_address)
        mavlink.wait_heartbeat(timeout=6)
        wp = mavwp.MAVWPLoader()                                                    
        seq = 1
        frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        radius = 1
        for i, waypoint in enumerate(waypoints):                  
            wp.add(mavutil.mavlink.MAVLink_mission_item_message(mavlink.target_system,
                            mavlink.target_component,
                            seq,
                            frame,
                            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                            0, 0, 0, radius, 0, 0,
                            waypoint[0],waypoint[1],waypoint[2]))
            seq += 1                                                                       

        mavlink.waypoint_clear_all_send()
        ack_msg = get_ack_msg(connect_address, mavlink, ['MISSION_REQUEST_INT', 'WAYPOINT_REQUEST', 'MISSION_ACK', 'MISSION_REQUEST'])               
        mavlink.waypoint_count_send(wp.count())   
        for i in range(wp.count()):
            ack_msg = get_ack_msg(connect_address, mavlink, ['MISSION_REQUEST_INT', 'WAYPOINT_REQUEST', 'MISSION_ACK', 'MISSION_REQUEST'])        
            ack_msg.mav.send(wp.wp(ack_msg.seq))                                                                      
        ack_msg = get_ack_msg(connect_address, mavlink, ['MISSION_REQUEST_INT', 'WAYPOINT_REQUEST', 'MISSION_ACK', 'MISSION_REQUEST'])
        return ack_msg
    except Exception as e:
        print(e)
    return {'ERROR': 'Set waypoint failed!', 'droneid':connect_address}


def set_arm(connect_address:int, is_disarm=False):
    try:
        mavlink = mavutil.mavlink_connection(SERVER_IP+':'+connect_address)
        msg = mavlink.wait_heartbeat(timeout=6)
        connect_address = int(connect_address)
        if not msg:
            return {'ERROR': f'No heartbeat from {connect_address} (timeout 6s)', 'droneid':connect_address}
        print(mavlink.motors_armed)
        

