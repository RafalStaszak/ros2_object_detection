#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from ros_object_detection_msgs.msg import BoundingBoxes, BoundingBox
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from .point_cloud2 import read_points, create_cloud
import threading

class ShowOnPclNode(Node):
    def __init__(self):
        super().__init__('show_on_pcl')
        self.pcl = None
        self.boxes = None
        self.new_pcl = False
        self.new_boxes = False

        self.pcl_subscriber = self.create_subscription(PointCloud2, "/point_cloud", self.pcl_callback,
                                                       qos_profile=qos_profile_sensor_data)
        self.bb_subscriber = self.create_subscription(BoundingBoxes, "/bounding_box", self.box_callback)
        self.pcl_publisher = self.create_publisher(PointCloud2, '/point_cloud_detection', 5)

    def pcl_callback(self, data):
        self.pcl = data
        self.new_pcl = True

    def box_callback(self, data):
        self.boxes = data
        self.new_boxes = True

    def process(self):
        if self.new_pcl and self.new_boxes:
            self.new_pcl = False
            self.new_boxes = False

            data = read_points(self.pcl, skip_nans=True, field_names=['x', 'y', 'z', 'rgba'])

            points = list()

            for point in data:
                x, y, z, rgba = point
                points.append([x, y, z, rgba])

            fields = [PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                      PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                      PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
                      PointField(name='rgba', offset=12, datatype=PointField.UINT32, count=1),
                      ]

            header = Header()
            header.frame_id = "map"
            pc2 = create_cloud(header, fields, points)
            self.pcl_pub.publish(pc2)


def main(args=None):
    rclpy.init(args=args)

    node = ShowOnPclNode()
    rate = node.create_rate(100)

    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    while rclpy.ok():
        node.process()
        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
