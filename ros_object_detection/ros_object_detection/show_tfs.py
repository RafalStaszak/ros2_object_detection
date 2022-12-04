#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import tf2_ros
from ros_object_detection_msgs.msg import BoundingBoxes


class ShowTfsNode(Node):
    def __init__(self):
        super().__init__('show_tfs')
        self.boxes = None
        self.pcl_subscriber = self.create_subscription(BoundingBoxes, "/bounding_box", self.box_callback)

    def box_callback(self, data):
        self.boxes = data
        for i, box in enumerate(self.boxes.data):
            pass


def main(args=None):
    rclpy.init(args=args)
    node = ShowTfsNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
