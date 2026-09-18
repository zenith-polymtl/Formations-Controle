#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL
from enum import Enum
from rclpy.qos import qos_profile_sensor_data

class FlightState(Enum):
    IDLE = 1
    ARMING = 2
    TAKEOFF = 3
    NAVIGATION = 4
    MISSION = 5
    LANDING = 6

class FlightManagerNode(Node):
    def __init__(self):
        super().__init__('flight_manager_node')
        self.current_state = FlightState.IDLE
        self.mavros_state = State()
        self.current_altitude = 0.0
        self.current_x = 0.0
        self.current_y = 0.0
        self.target_takeoff_altitude = 50
        self.target_arrive_x = 10
        self.target_arrive_y = 20

        self.declare_parameter('kp', 0.5)  # Proportional gain for position control
        self.kp = self.get_parameter('kp').value
        self.max_vel = 2.0
        self.safe_distance = 2.0
        

        self.state_sub = self.create_subscription(State, '/mavros/state', self.state_cb, qos_profile=qos_profile_sensor_data)
        self.pose_sub = self.create_subscription(PoseStamped, '/mavros/local_position/pose', self.pose_cb, qos_profile=qos_profile_sensor_data)
        self.ballon_pose_sub = self.create_subscription(PoseStamped,'/Ballon_pose', self.ballon_pose_cb, 10)


        self.vel_pub = self.create_publisher(TwistStamped, '/mavros/setpoint_velocity/cmd_vel',10)
        self.arrive_pub = self.create_publisher(String, '/arrival', 10)

        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
        self.timer = self.create_timer(0.1, self.control_loop)
        self.rtl_timer = None

    def state_cb(self, msg):
        self.mavros_state = msg

    def pose_cb(self, msg):
        self.current_x = msg.pose.position.x
        self.current_y = msg.pose.position.y
        self.current_altitude = msg.pose.position.z

    def ballon_pose_cb(self, msg):
        self.current_ballon_x = msg.pose.position.x
        self.current_ballon_y = msg.pose.position.y
        self.current_ballon_z = msg.pose.position.z

    def control_loop(self):
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = "map"

        if self.current_state == FlightState.IDLE:
            cmd.twist.linear.x = 0.0
            cmd.twist.linear.y = 0.0
            cmd.twist.linear.z = 0.0

            if self.mavros_state.connected:
                self.get_logger().info("Connexion Mavros réussie. Passage à l'armement.")
                if self.mavros_state.mode != "GUIDED":
                    self.get_logger().info("Mode actuel différent de GUIDED.")
                    if self.set_mode_client.wait_for_service(timeout_sec=0.5):
                        req = SetMode.Request()
                        req.custom_mode = "GUIDED"
                        self.set_mode_client.call_async(req)
                        self.get_logger().info("Mode GUIDED activé.")
                else:
                    self.get_logger().info("Prêt pour le vol. Demande d'armement")
                    self.request_arm(True)
                    self.current_state = FlightState.ARMING
                    self.get_logger().info("Demande d'armement envoyée. En attente de l'armement...")
            if not self.mavros_state.connected:
                self.get_logger().info("En attente de la connexion avec MAVROS...", throttle_duration_sec=2.0)

        elif self.current_state == FlightState.ARMING:
            if not self.mavros_state.armed:
                self.get_logger().info("En attente de l'armement...", throttle_duration_sec=2.0)
                self.request_arm(True)
            else:
                self.get_logger().info("Drone armé ! Envoi de l'ordre de décollage.")
                self.request_takeoff(self.target_takeoff_altitude)
                self.current_state = FlightState.TAKEOFF

            if self.mavros_state.armed:
                self.get_logger().info("Drone armé! Début de décollage.")
                self.current_state = FlightState.TAKEOFF


        elif self.current_state == FlightState.TAKEOFF:
            cmd.twist.linear.x = 0.0
            cmd.twist.linear.y = 0.0
            cmd.twist.linear.z = 2.0

            if self.current_altitude >= self.target_takeoff_altitude:
                self.get_logger().info("Altitude atteinte. Passage en Navigation.")
                self.current_state = FlightState.NAVIGATION

        elif self.current_state == FlightState.NAVIGATION:
            cmd.twist.linear.x = 0.0
            cmd.twist.linear.y = 2.0
            cmd.twist.linear.z = 0.0

            if self.current_y >= 20 :
                cmd.twist.linear.x = 2.0
                cmd.twist.linear.y = 0.0
                cmd.twist.linear.z = 0.0
                if self.current_x >= 10 :
                    cmd.twist.linear.x = 0.0
                    cmd.twist.linear.y = 0.0
                    cmd.twist.linear.z = 0.0
                    status_msg = String()
                    status_msg.data = 'Nour'
                    self.arrive_pub.publish(status_msg)
                    self.get_logger().info("Message d'arrivé publié avec succès.")
                    self.rtl_timer = self.create_timer(125.0, self.rtl_callback)
                    self.get_logger().info("Chronomètre RTL de 125 secondes démarré !")
                    self.current_state = FlightState.MISSION

        elif self.current_state == FlightState.MISSION:
            error_x = self.current_ballon_x - self.current_x
            error_y = self.current_ballon_y - self.current_y
            error_z = self.current_ballon_z - self.current_altitude
            distance = (error_x**2 + error_y**2 + error_z**2)**0.5
            if distance > self.safe_distance:
                cmd.twist.linear.x = self.kp * error_x
                cmd.twist.linear.y = self.kp * error_y
                cmd.twist.linear.z = self.kp * error_z
                self.get_logger().info(f"Distance au ballon: {distance:.2f} m. Commande de vitesse calculée.")
                self.get_logger().info(f"distance en : x={error_x:.2f}, y={error_y:.2f}, z={error_z:.2f}")
                

                cmd.twist.linear.x = max(-self.max_vel, min(cmd.twist.linear.x, self.max_vel))
                cmd.twist.linear.y = max(-self.max_vel, min(cmd.twist.linear.y, self.max_vel))
                cmd.twist.linear.z = max(-self.max_vel, min(cmd.twist.linear.z, self.max_vel))
                if self.current_altitude < 1.0:
                    cmd.twist.linear.z = 0.0
            else:
                cmd.twist.linear.x = 0.0
                cmd.twist.linear.y = 0.0
                cmd.twist.linear.z = 0.0
                self.get_logger().info("Drone à proximité du ballon. Maintien de la position.")

        elif self.current_state == FlightState.LANDING:
            if self.current_altitude == 0.0:
                self.get_logger().info("Drone a attéri.")
                self.current_state = FlightState.IDLE
                self.request_arm(False)
                self.get_logger().info("Drone désarmé.")
        if self.current_state in [FlightState.NAVIGATION, FlightState.MISSION]:
            self.vel_pub.publish(cmd)

    def request_arm(self, state):
        if self.arming_client.wait_for_service(timeout_sec=0.5):
            req = CommandBool.Request()
            req.value = state
            self.arming_client.call_async(req)

    def request_takeoff(self, altitude):
        if self.takeoff_client.wait_for_service(timeout_sec=0.5):
            req = CommandTOL.Request()
            req.altitude = float(altitude)
            self.takeoff_client.call_async(req)
            self.get_logger().info(f"Ordre de décollage envoyé à l'altitude {altitude} m.")

    def rtl_callback(self):
        self.destroy_timer(self.rtl_timer)
        
        if self.mavros_state.mode != "RTL":
            if self.set_mode_client.wait_for_service(timeout_sec=0.5):
                req = SetMode.Request()
                req.custom_mode = "RTL"
                self.set_mode_client.call_async(req)
                self.get_logger().info("Mode RTL activé.")
                self.current_state = FlightState.LANDING
                

def main(args=None):
    rclpy.init(args=args)
    node = FlightManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()





        

        
