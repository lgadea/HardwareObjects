#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""
Qt4_GraphicsManager keeps track of the current shapes the user has created. 
All shapes (graphics items) are based on Qt native QGraphicsLib.GraphicsItem objects.
QGraphicsScene and QGraphicsView are used to display objects

example xml:

<object class="Qt4_GraphicsManager">
   <object href="/Qt4_mini-diff-mockup" role="diffractometer"/>
   <object href="/beam-info" role="beam_info"/>
</object>
"""

import os
import tempfile
import logging
import numpy as np
from scipy import ndimage

from PyQt4 import QtGui, QtCore

try:
  import lucid2 as lucid
except ImportError:
  try:
      import lucid
  except ImportError:
      logging.warning("Could not find autocentring library, automatic centring is disabled")

import Qt4_GraphicsLib as GraphicsLib
import queue_model_objects_v1 as queue_model_objects
from HardwareRepository.BaseHardwareObjects import HardwareObject


class Qt4_GraphicsManager(HardwareObject):
    """
    Descript. : Keeps track of the current shapes the user has created. The
                Diffractometer and BeamInfo hardware objects are mandotary
    """
    def __init__(self, name):
        """
        :param name: name
        :type name: str
        """
        HardwareObject.__init__(self, name)

        self.diffractometer_hwobj = None
        self.camera_hwobj = None
        self.beam_info_hwobj = None
     
        self.pixels_per_mm = [0, 0]
        self.beam_position = [0, 0]
        self.beam_info_dict = {}
        self.graphics_scene_size = [0, 0]
        self.mouse_position = [0, 0]
        self.image_scale = None 
        self.image_scale_list = []

        self.omega_axis_info_dict = {}
        self.in_centring_state = None
        self.in_grid_drawing_state = None
        self.in_measure_distance_state = None
        self.in_measure_angle_state = None
        self.in_measure_area_state = None
        self.in_move_beam_mark_state = None
        self.in_select_items_state = None
        self.in_beam_define_state = None
        self.wait_grid_drawing_click = None
        self.wait_measure_distance_click = None
        self.wait_measure_angle_click = None
        self.wait_measure_area_click = None
        self.wait_beam_define_click = None
        self.current_centring_method = None
        self.point_count = 0
        self.line_count = 0
        self.grid_count = 0
        self.shape_dict = {}

        self.graphics_view = None
        self.graphics_camera_frame = None
        self.graphics_beam_item = None
        self.graphics_scale_item = None
        self.graphics_omega_reference_item = None
        self.graphics_centring_lines_item = None
        self.graphics_grid_draw_item = None
        self.graphics_measure_distance_item = None
        self.graphics_measure_angle_item = None
        self.graphics_measure_area_item = None
        self.graphics_move_beam_mark_item = None
        self.graphics_select_tool_item = None
        self.graphics_beam_define_item = None
 
    def init(self):
        """Main init function. Initiates all graphics items, hwobjs and 
           connects all qt signals to slots.
        """

        self.graphics_view = GraphicsLib.GraphicsView()
        self.graphics_camera_frame = GraphicsLib.GraphicsCameraFrame()
        self.graphics_scale_item = GraphicsLib.GraphicsItemScale(self)
        self.graphics_omega_reference_item = \
             GraphicsLib.GraphicsItemOmegaReference(self)
        self.graphics_beam_item = GraphicsLib.GraphicsItemBeam(self)
        self.graphics_move_beam_mark_item = \
             GraphicsLib.GraphicsItemMoveBeamMark(self)
        self.graphics_move_beam_mark_item.hide()
        self.graphics_centring_lines_item = \
             GraphicsLib.GraphicsItemCentringLines(self)
        self.graphics_centring_lines_item.hide()
        self.graphics_measure_distance_item = \
             GraphicsLib.GraphicsItemMeasureDistance(self)
        self.graphics_measure_distance_item.hide()
        self.graphics_measure_angle_item = \
             GraphicsLib.GraphicsItemMeasureAngle(self)
        self.graphics_measure_angle_item.hide()
        self.graphics_measure_area_item = \
             GraphicsLib.GraphicsItemMeasureArea(self)
        self.graphics_measure_area_item.hide()
        self.graphics_select_tool_item = GraphicsLib.GraphicsSelectTool(self)
        self.graphics_select_tool_item.hide()
        self.graphics_beam_define_item = GraphicsLib.GraphicsItemBeamDefine(self)
        self.graphics_beam_define_item.hide()
         
        self.graphics_view.graphics_scene.addItem(self.graphics_camera_frame) 
        self.graphics_view.graphics_scene.addItem(self.graphics_omega_reference_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_beam_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_move_beam_mark_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_centring_lines_item) 
        self.graphics_view.graphics_scene.addItem(self.graphics_scale_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_measure_distance_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_measure_angle_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_measure_area_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_select_tool_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_beam_define_item)

        self.graphics_view.scene().mouseClickedSignal.connect(\
             self.mouse_clicked)
        self.graphics_view.scene().mouseDoubleClickedSignal.connect(\
             self.mouse_double_clicked)
        self.graphics_view.scene().mouseReleasedSignal.connect(\
             self.mouse_released)
        self.graphics_view.scene().itemClickedSignal.connect(\
             self.item_clicked)
        self.graphics_view.scene().itemDoubleClickedSignal.connect(\
             self.item_double_clicked)
        self.graphics_view.mouseMovedSignal.connect(self.mouse_moved)
        self.graphics_view.keyPressedSignal.connect(self.key_pressed)

        self.diffractometer_hwobj = self.getObjectByRole("diffractometer")
        if self.diffractometer_hwobj:
            pixels_per_mm = self.diffractometer_hwobj.\
                 get_pixels_per_mm()
            self.diffractometer_pixels_per_mm_changed(pixels_per_mm)             
            GraphicsLib.GraphicsItemGrid.set_grid_direction(self.diffractometer_hwobj.\
                 get_grid_direction())
            self.connect(self.diffractometer_hwobj, "stateChanged", 
                         self.diffractometer_changed)
            self.connect(self.diffractometer_hwobj, "centringStarted",
                         self.diffractometer_centring_started)
            self.connect(self.diffractometer_hwobj, "centringAccepted", 
                         self.diffractometer_centring_accepted)
            self.connect(self.diffractometer_hwobj, "centringSuccessful", 
                         self.diffractometer_centring_successful)
            self.connect(self.diffractometer_hwobj, "centringFailed", 
                         self.diffractometer_centring_failed)
            self.connect(self.diffractometer_hwobj, "pixelsPerMmChanged", 
                         self.diffractometer_pixels_per_mm_changed) 
            self.connect(self.diffractometer_hwobj, "omegaReferenceChanged", 
                         self.diffractometer_omega_reference_changed)
            self.connect(self.diffractometer_hwobj, "phiMotorMoved",
                         self.diffractometer_phi_motor_moved)
        else:
            logging.getLogger("HWR").error("GraphicsManager: Diffractometer hwobj not defined")

        self.beam_info_hwobj = self.getObjectByRole("beam_info")
        if self.beam_info_hwobj:
            self.beam_info_dict = self.beam_info_hwobj.get_beam_info()
            self.connect(self.beam_info_hwobj, 
                         "beamPositionChanged", 
                         self.beam_position_changed)
            self.connect(self.beam_info_hwobj, 
                         "beamInfoChanged",
                         self.beam_info_changed)

            self.beam_info_changed(self.beam_info_dict)
            self.beam_position_changed(self.beam_info_hwobj.get_beam_position())
        else:
            logging.getLogger("HWR").error("GraphicsManager: BeamInfo hwobj not defined")

        self.camera_hwobj = self.getObjectByRole("camera")
        if self.camera_hwobj:
            self.graphics_scene_size = self.camera_hwobj.get_image_dimensions()
            self.set_graphics_scene_size(self.graphics_scene_size, False)
            self.camera_hwobj.start_camera()
            self.connect(self.camera_hwobj, 
                         "imageReceived", 
                         self.camera_image_received) 
        else:         
            logging.getLogger("HWR").error("GraphicsManager: Camera hwobj not defined")

        try:
            self.image_scale_list = eval(self.getProperty("imageScaleList"))
            if len(self.image_scale_list) > 0:
                self.image_scale = self.getProperty("defaultImageScale") 
                self.set_image_scale(self.image_scale, self.image_scale is not None)
        except:
            pass

    def camera_image_received(self, pixmap_image):
        """Method called when a frame from camera arrives.
           Slot to signal 'imageReceived'

        :param pixmap_image: frame from camera
        :type pixmap_image: QtGui.QPixmapImage
        """
        if self.image_scale:
            pixmap_image = pixmap_image.scaled(QtCore.QSize(\
               pixmap_image.width() * self.image_scale,
               pixmap_image.height() * self.image_scale))
        self.graphics_camera_frame.setPixmap(pixmap_image) 

    def beam_position_changed(self, position):
        """Method called when beam position on the screen changed.

        :param position: beam position on a screen
        :type position: list of two int
        """
        if position:
            self.beam_position = position
            self.graphics_beam_item.set_start_position(\
                 self.beam_position[0],
                 self.beam_position[1])

    def beam_info_changed(self, beam_info):
        """Method called when beam info changed

        :param beam_info: information about the beam shape
        :type beam_info: dict with beam info parameters
        """
        if beam_info:
            self.graphics_beam_item.set_beam_info(beam_info)
            self.graphics_view.graphics_scene.update()

    def diffractometer_changed(self, *args):
        """Method called when diffractometer state changed.
           Updates point screen coordinates and grid coorner coordinates.
           If diffractometer not ready then hides all shapes.
        """
        if self.diffractometer_hwobj.isReady():
            for shape in self.get_shapes():
                if isinstance(shape, GraphicsLib.GraphicsItemPoint):
                    cpos =  shape.get_centred_position()
                    new_x, new_y = self.diffractometer_hwobj.\
                        motor_positions_to_screen(cpos.as_dict())
                    shape.set_start_position(new_x, new_y)
                elif isinstance(shape, GraphicsLib.GraphicsItemGrid):
                    corner_coord = []
                    for motor_pos in shape.get_motor_pos_corner():
                        corner_coord.append((self.diffractometer_hwobj.\
                            motor_positions_to_screen(motor_pos)))
                    shape.set_corner_coord(corner_coord) 
            for shape in self.get_shapes():
                shape.show()
            self.graphics_view.graphics_scene.update()
        else:
            for shape in self.get_shapes():
                shape.hide()

    def diffractometer_centring_started(self, centring_method, flexible):
        """Method called when centring started as a reply from diffractometer

        :param centring_method: centring method
        :type centring_method: str
        :param flexible: flexible bit
        :type flexible: bool
        :emits: centringStarted
        """
        self.current_centring_method = centring_method
        self.emit("centringStarted")  

    def diffractometer_centring_accepted(self, centring_state, centring_status):
        """Creates a new centring position and adds it to graphics point.

        :param centring_state: 
        :type centring_state: str
        :param centring_status: dictionary with motor pos and etc
        :type centring_status: dict
        :emits: centringInProgress
        """
        p_dict = {}

        if 'motors' in centring_status and \
                'extraMotors' in centring_status:

            p_dict = dict(centring_status['motors'],
                          **centring_status['extraMotors'])
        elif 'motors' in centring_status:
            p_dict = dict(centring_status['motors'])

        if p_dict:
            cpos = queue_model_objects.CentredPosition(p_dict)
            screen_pos = self.diffractometer_hwobj.\
                    motor_positions_to_screen(cpos.as_dict())
            point = GraphicsLib.GraphicsItemPoint(cpos, True, 
                    screen_pos[0], screen_pos[1])
            if point:
                self.add_shape(point)
                cpos.set_index(point.index)
        self.emit("centringInProgress", False)

    def diffractometer_centring_successful(self, method, centring_status):
        """Last stage in centring procedure

        :param method: method name
        :type method: str
        :param centring_status: centring status
        :type centring_status: dict
        :emits: - centringSuccessful 
                - infoMsg
        """
        self.set_centring_state(False)
        self.emit("infoMsg", "Click Save to store new centring point!")
        self.emit("centringSuccessful", method, centring_status)

    def diffractometer_centring_failed(self, method, centring_status):
        """CleanUp method after centring failed

        :param method: method name
        :type method: str
        :param centring_status: centring status
        :type centring_status: dict
        :emits: - centringFailed
                - infoMsg
        """
        self.set_centring_state(False) 
        self.emit("centringFailed", method, centring_status)
        self.emit("infoMsg", "")

    def diffractometer_pixels_per_mm_changed(self, pixels_per_mm):
        """Updates graphics scale when zoom changed

        :param pixels_per_mm: two floats for scaling
        :type pixels_per_mm: list with two floats
        """
        if type(pixels_per_mm) in (list, tuple):
            if pixels_per_mm != self.pixels_per_mm:
                self.pixels_per_mm = pixels_per_mm
                for item in self.graphics_view.graphics_scene.items():
                    if isinstance(item, GraphicsLib.GraphicsItem):
                        item.set_pixels_per_mm(self.pixels_per_mm)
                self.graphics_view.graphics_scene.update()

    def diffractometer_omega_reference_changed(self, omega_reference):
        """Method called when omega reference changed

        :param omega_reference: omega reference values
        :type omega_reference: list of two coordinated
        """
        self.graphics_omega_reference_item.set_reference(omega_reference)

    def diffractometer_phi_motor_moved(self, position):
        """Method when phi motor changed. Updates omega reference by
           redrawing phi angle
       
        :param position: phi rotation value
        :type position: float
        """
        self.graphics_omega_reference_item.set_phi_position(position)
        
    def mouse_clicked(self, pos_x, pos_y, left_click=True):
        """Method when mouse clicked on GraphicsScene

        :param pos_x: screen coordinate X
        :type pos_x: int
        :param pos_y: screen coordinate Y
        :type pos_y: int
        :param left_click: left button clicked
        :type left_click: bool
        :emits: - shapeSelected
                - pointSelected
                - infoMsg
        """
        if self.in_centring_state:
            self.graphics_centring_lines_item.set_start_position(pos_x, pos_y)
            self.diffractometer_hwobj.image_clicked(pos_x, pos_y)
        elif self.wait_grid_drawing_click:
            self.in_grid_drawing_state = True
            self.graphics_grid_draw_item.set_draw_mode(True)
            self.graphics_grid_draw_item.set_draw_start_position(pos_x, pos_y)
            self.graphics_grid_draw_item.show()
        elif self.wait_measure_distance_click:
            self.start_graphics_item(self.graphics_measure_distance_item)
            self.in_measure_distance_state = True
            self.wait_measure_distance_click = False
        elif self.wait_measure_angle_click:
            self.start_graphics_item(self.graphics_measure_angle_item)
            self.in_measure_angle_state = True
            self.wait_measure_angle_click = False
        elif self.wait_measure_area_click:
            self.start_graphics_item(self.graphics_measure_area_item)
            self.in_measure_area_state = True
            self.wait_measure_area_click = False
        elif self.wait_beam_define_click:
            self.start_graphics_item(self.graphics_beam_define_item)
            self.in_beam_define_state = True
            self.wait_beam_define_click = False
        elif self.in_measure_distance_state:
            self.graphics_measure_distance_item.store_coord(pos_x, pos_y)
        elif self.in_measure_angle_state:
            self.graphics_measure_angle_item.store_coord(pos_x, pos_y)
        elif self.in_measure_area_state:
            self.graphics_measure_area_item.store_coord()
        elif self.in_move_beam_mark_state:
            self.stop_move_beam_mark()
        elif self.in_beam_define_state:
            self.stop_beam_define()
            #self.graphics_beam_define_item.store_coord(pos_x, pos_y)
        else:
            if left_click: 
                self.graphics_select_tool_item.set_start_position(pos_x, pos_y)
                self.graphics_select_tool_item.set_end_position(pos_x, pos_y)
                self.graphics_select_tool_item.show()
                self.in_select_items_state = True
            for graphics_item in self.graphics_view.scene().items():
                graphics_item.setSelected(False)
                if type(graphics_item) in [GraphicsLib.GraphicsItemPoint, 
                                           GraphicsLib.GraphicsItemLine, 
                                           GraphicsLib.GraphicsItemGrid]:
                    self.emit("shapeSelected", graphics_item, False)  
            self.emit("pointSelected", None)
            self.emit("infoMsg", "")

    def mouse_double_clicked(self, pos_x, pos_y):
        """If in one of the measuring states, then stops measuring.
           Otherwise moves to screen coordinate

        :param pos_x: screen coordinate X
        :type pos_x: int
        :param pos_y: screen coordinate Y
        :type pos_y: int
        """
        if self.in_measure_distance_state:
            self.stop_measure_distance()
        elif self.in_measure_angle_state:
            self.stop_measure_angle()
        elif self.in_measure_area_state:
            self.stop_measure_area()
        elif self.in_beam_define_state:
            self.stop_beam_define()
        else: 
            self.diffractometer_hwobj.move_to_coord(pos_x, pos_y)

    def mouse_released(self, pos_x, pos_y):
        """Mouse release method. Used to finish grid drawing and item 
           selection with selection rectangle

        :param pos_x: screen coordinate X
        :type pos_x: int
        :param pos_y: screen coordinate Y
        :type pos_y: int
        :emits: shapeCreated
        """
        if self.in_grid_drawing_state:
            self.graphics_grid_draw_item.set_draw_mode(False)
            self.graphics_grid_draw_item.fix_grid_position()
            self.wait_grid_drawing_click = False
            self.in_grid_drawing_state = False
            self.de_select_all()
            self.emit("shapeCreated", self.graphics_grid_draw_item, "Grid")
            self.graphics_grid_draw_item.setSelected(True) 
            self.shape_dict[self.graphics_grid_draw_item.get_display_name()] = \
                 self.graphics_grid_draw_item
        elif self.in_beam_define_state:
            print "set positon and slit size"
            self.stop_beam_define()
        elif self.in_select_items_state:
            self.graphics_select_tool_item.hide()
            self.in_select_items_state = False
           
    def mouse_moved(self, pos_x, pos_y):
        """Executed when mouse moved. Used in all measure methods, centring
           procedure and item selection procedure.

        :param pos_x: screen coordinate X
        :type pos_x: int
        :param pos_y: screen coordinate Y
        :type pos_y: int
        :emits: mouseMoved
        """
        self.emit("mouseMoved", pos_x, pos_y)
        self.mouse_position[0] = pos_x
        self.mouse_position[1] = pos_y
        if self.in_centring_state:
            self.graphics_centring_lines_item.set_start_position(pos_x, pos_y)
        elif self.in_grid_drawing_state:
            if self.graphics_grid_draw_item.is_draw_mode():
                self.graphics_grid_draw_item.set_draw_end_position(pos_x, pos_y)
        elif self.in_measure_distance_state:
            self.graphics_measure_distance_item.set_coord(self.mouse_position)
        elif self.in_measure_angle_state:
            self.graphics_measure_angle_item.set_coord(self.mouse_position)
        elif self.in_measure_area_state:
            self.graphics_measure_area_item.set_coord(self.mouse_position)
        elif self.in_move_beam_mark_state:
            self.graphics_move_beam_mark_item.set_end_position(\
                self.mouse_position[0], self.mouse_position[1])
        elif self.in_beam_define_state:
            self.graphics_beam_define_item.set_end_position(\
                self.mouse_position[0], self.mouse_position[1])
        elif self.in_select_items_state:
             
            self.graphics_select_tool_item.set_end_position(pos_x, pos_y)
            select_start_x = self.graphics_select_tool_item.start_coord[0]
            select_start_y = self.graphics_select_tool_item.start_coord[1]
            if abs(select_start_x - pos_x) > 5 and \
               abs(select_start_y - pos_y) > 5:
                painter_path = QtGui.QPainterPath()
                painter_path.addRect(min(select_start_x, pos_x),
                                     min(select_start_y, pos_y),
                                     abs(select_start_x - pos_x),
                                     abs(select_start_y - pos_y))
                self.graphics_view.graphics_scene.setSelectionArea(painter_path)
                self.select_lines_and_grids()

    def key_pressed(self, key_event):
        """Method when key on GraphicsView pressed.
           - Deletes selected shapes if Delete pressed
           - Cancels measurement action if Escape pressed

        :param key_event: key event type
        :type key_event: str
        """
        if key_event == "Delete":
            for item in self.graphics_view.graphics_scene.items():
                if item.isSelected():
                    self.delete_shape(item)
        elif key_event == "Escape":
            self.stop_measure_distance()
            self.stop_measure_angle()
            self.stop_measure_area()  
            self.stop_beam_define()
 
    def item_clicked(self, item, state):
        """Item clicked event

        :param item: clicked item
        :type item: QGraphicsLib.GraphicsItem
        :param state: selection state
        :type state: bool 
        :emits: - pointsSelected
                - infoMsg
        """
        # state here is inverted
        if type(item) in [GraphicsLib.GraphicsItemPoint, 
                          GraphicsLib.GraphicsItemLine, 
                          GraphicsLib.GraphicsItemGrid]: 
            self.emit("shapeSelected", item, not state)
            if isinstance(item, GraphicsLib.GraphicsItemPoint):
                if not state:
                    self.emit("pointSelected", item)
                    self.emit("infoMsg", item.get_full_name() + " selected")

    def item_double_clicked(self, item):
        """Item double clicked method.
           If centring point double clicked then moves motors to the 
           centring position

        :param item: double clicked item
        :type item: QGraphicsLib.GraphicsItem
        """ 
        if isinstance(item, GraphicsLib.GraphicsItemPoint):
            self.diffractometer_hwobj.move_to_centred_position(\
                 item.get_centred_position())
    
    def get_graphics_view(self):
        """Rturns current GraphicsView
     
        :returns: QGraphicsView
        """
        return self.graphics_view

    def get_graphics_camera_frame(self):
        """Rturns current CameraFrame
     
        :returns: GraphicsCameraFrame
        """
        return self.graphics_camera_frame 

    def set_graphics_scene_size(self, size, fixed):
        """Sets fixed size of scene

        :param size: scene size
        :type size: list
        :param fixed: fixed bit
        :type fixed: bool
        """
        if not self.graphics_scene_size or fixed:
            self.graphics_scene_size = size
            self.graphics_scale_item.set_start_position(size[0], size[1])
            self.graphics_view.scene().setSceneRect(0, 0, size[0], size[1])
            #self.graphics_view.setFixedSize(size[0] + 2, size[1] + 2)

    def set_centring_state(self, state):
        """Sets centrin state
 
        :param state: centring state
        :type state: bool
        """
        self.in_centring_state = state
        self.graphics_centring_lines_item.set_visible(state)

    def get_shapes(self):
        """Returns currently handled shapes.

        :returns: list with shapes
        """
        shapes_list = []
        for shape in self.graphics_view.graphics_scene.items():
            if type(shape) in (GraphicsLib.GraphicsItemPoint, 
                               GraphicsLib.GraphicsItemLine, 
                               GraphicsLib.GraphicsItemGrid):
                shapes_list.append(shape)                 
        return shapes_list

    def get_points(self):
        """Returns all points

        :returns: list with GraphicsLib.GraphicsItemPoint
        """
        current_points = []

        for shape in self.get_shapes():
            if isinstance(shape, GraphicsLib.GraphicsItemPoint):
                current_points.append(shape)

        return current_points
        
    def add_shape(self, shape):
        """Adds the shape <shape> to the list of handled objects.

        :param shape: Shape to add.
        :type shape: Shape object.
        :emits: shapeSelected
        """
        self.de_select_all()
        if isinstance(shape, GraphicsLib.GraphicsItemPoint):
            self.point_count += 1
            shape.index = self.point_count
            self.emit("shapeCreated", shape, "Point")
            self.emit("pointSelected", shape)
            self.emit("infoMsg", "Centring %s created" % shape.get_full_name())
        elif isinstance(shape, GraphicsLib.GraphicsItemLine):
            self.line_count += 1
            shape.index = self.line_count
            self.emit("shapeCreated", shape, "Line")
            self.emit("infoMsg", "%s created" % shape.get_full_name())
        self.shape_dict[shape.get_display_name()] = shape
        self.graphics_view.graphics_scene.addItem(shape)
        shape.setSelected(True)
        self.emit("shapeSelected", shape, True)

    def delete_shape(self, shape):
        """Removes the shape <shape> from the list of handled shapes.

        :param shape: The shape to remove
        :type shape: GraphicsLib.GraphicsItem object
        :emits: shapeDeleted
        """
        if isinstance(shape, GraphicsLib.GraphicsItemPoint):
            for s in self.get_shapes():
                if isinstance(s, GraphicsLib.GraphicsItemLine):
                    if shape in s.get_graphics_points():
                        self._delete_shape(s)
                        break
        shape_type = ""
        if isinstance(shape, GraphicsLib.GraphicsItemPoint):
            shape_type = "Point"
        elif isinstance(shape, GraphicsLib.GraphicsItemLine):
            shape_type = "Line"
        elif isinstance(shape, GraphicsLib.GraphicsItemGrid):
            shape_type = "Grid"

        self.emit("shapeDeleted", shape, shape_type)
        self.graphics_view.graphics_scene.removeItem(shape)
        self.graphics_view.graphics_scene.update()

    def get_shape_by_name(self, shape_name):
        """Returns shape by name

        :param shape_name: name of the shape
        :type shape_name: str
        :returns: GraphicsLib.GraphicsItem
        """
        return self.shape_dict.get(shape_name)            

    def clear_all(self):
        """Clear the shape history, remove all contents.
        """

        self.point_count = 0
        self.line_count = 0
        self.grid_count = 0

        for shape in self.get_shapes():
            self.delete_shape(shape)
        self.graphics_view.graphics_scene.update()

    def de_select_all(self):
        """Deselects all shapes
        """

        self.graphics_view.graphics_scene.clearSelection()

    def select_line(self, line):
        """Selects shape"""
        line.setSelected(True)
        self.graphics_view.graphics_scene.update()

    def select_all_points(self):
        """Selects all points
        """

        self.de_select_all()
        for shape in self.get_points():
            shape.setSelected(True) 
        self.graphics_view.graphics_scene.update()

    def select_shape_with_cpos(self, cpos):
        """Selects all points with centred position
        """

        self.de_select_all()
        for shape in self.get_points():
            if shape.get_centred_position() == cpos:
                shape.setSelected(True)
        self.graphics_view.graphics_scene.update()

    def get_selected_shapes(self):
        """Returns selected shapes

        :returns: list with GraphicsLib.GraphicsItem
        """

        selected_shapes = []
        for item in self.graphics_view.graphics_scene.items():
            if (type(item) in (GraphicsLib.GraphicsItemPoint, 
                               GraphicsLib.GraphicsItemLine,
                               GraphicsLib.GraphicsItemGrid) and
                item.isSelected()):
                selected_shapes.append(item) 
        return selected_shapes

    def get_selected_points(self):
        """Returns selected points

        :returns: list with GraphicsLib.GraphicsItemPoint
        """

        selected_points = []
        selected_shapes = self.get_selected_shapes()
        for shape in selected_shapes:
            if isinstance(shape, GraphicsLib.GraphicsItemPoint):
                selected_points.append(shape)
        return sorted(selected_points, key = lambda x : x.index, reverse = False)

    def add_new_centring_point(self, state, centring_status, beam_info):
        """Adds new centring point to the scene

        :param state: state
        :type state: bool
        :param centring_status: centring status with motor positions
        :type centring_statues: dict
        :param beam_info: information about beam mark
        :type beam_info: dict
        """

        new_point = GraphicsLib.GraphicsItemPoint(self)
        self.centring_points.append(new_point)
        self.graphics_view.graphics_scene.addItem(new_point)        

    def get_snapshot(self, shape=None, bw=None, return_as_array=None):
        """Takes a snapshot of the scene

        :param shape: shape that needs to be selected
        :type shape: GraphicsLib.GraphicsItem
        :returns: QImage
        """

        if shape:
            self.de_select_all()
            shape.setSelected(True)

        image = QtGui.QImage(self.graphics_view.graphics_scene.sceneRect().\
            size().toSize(), QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)
        image_painter = QtGui.QPainter(image)
        self.graphics_view.render(image_painter)
        image_painter.end()
        if return_as_array:
            pass         
        else:
           
            return image

    def save_snapshot(self, file_name):
        """Method to save snapshot
        
        :param file_name: file name
        :type file_name: str 
        """

        logging.getLogger("user_level_log").info("Saving snapshot in %s" % file_name)
        snapshot = self.get_snapshot()
        snapshot.save(file_name)

    def start_measure_distance(self, wait_click=False):
        """Distance measuring method

        :param wait_click: wait for first click to start
        :type wait_click: bool
        :emits: infoMsg
        """ 

        self.camera_hwobj.save_snapshot("/tmp/test_01.png")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        if wait_click:
            logging.getLogger("user_level_log").info("Click to start " + \
                    "distance  measuring (Double click stops)")  
            self.wait_measure_distance_click = True
            self.emit("infoMsg", "Distance measurement")
        else:
            self.wait_measure_distance_click = False
            self.in_measure_distance_state = True
            self.start_graphics_item(self.graphics_measure_distance_item)

    def start_measure_angle(self, wait_click = False):
        """Angle measuring method

        :param wait_click: wait for first click to start
        :type wait_click: bool
        :emits: infoMsg
        """

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        if wait_click:
            logging.getLogger("user_level_log").info("Click to start " + \
                 "angle measuring (Double click stops)")
            self.wait_measure_angle_click = True
            self.emit("infoMsg", "Angle measurement")
        else:
            self.wait_measure_angle_click = False
            self.in_measure_angle_state = True
            self.start_graphics_item(self.graphics_measure_angle_item)
            
    def start_measure_area(self, wait_click = False):
        """Area measuring method

        :param wait_click: wait for first click to start
        :type wait_click: bool
        :emits: infoMsg
        """

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        if wait_click:
            logging.getLogger("user_level_log").info("Click to start area " + \
                    "measuring (Double click stops)")
            self.wait_measure_area_click = True
            self.emit("infoMsg", "Area measurement")
        else:
            self.wait_measure_area_click = False
            self.in_measure_area_state = True
            self.start_graphics_item(self.graphics_measure_area_item)

    def start_move_beam_mark(self):
        """Method to move beam mark

        :emits: infoMsg
        """

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        self.emit("infoMsg", "Move beam mark")
        self.in_move_beam_mark_state = True
        self.start_graphics_item(\
             self.graphics_move_beam_mark_item,
             start_pos = self.graphics_beam_item.start_coord)
        self.graphics_move_beam_mark_item.set_beam_mark(\
             self.beam_info_dict, self.pixels_per_mm) 

    def start_define_beam(self):
        """Method to define beam size. 
           User 

        :emits: infoMsg
        """

        QtGui.QApplication.setOverrideCursor(\
              QtGui.QCursor(QtCore.Qt.BusyCursor))
        logging.getLogger("user_level_log").info("Select an area to " + \
                 "define beam size")
        self.wait_beam_define_click = True
        self.emit("infoMsg", "Define beam size")

    def start_graphics_item(self, item, start_pos=None, end_pos=None):
        """Updates item on the scene

        :param item: item
        :type item: GraphicsLib.GraphicsItem
        :param start_pos: draw start position
        :type start_pos: list with x and y coordinates
        :param end_pos: draw end position
        :type end_pos: list with x and y coordinates
        """

        if not start_pos:
            start_pos = self.mouse_position
        if not end_pos:
            end_pos = self.mouse_position
        item.set_start_position(start_pos[0], start_pos[1])
        item.set_end_position(end_pos[0], end_pos[1])
        item.show()
        self.graphics_view.graphics_scene.update()

    def stop_measure_distance(self):
        """Stops distance measurement

        :emits: infoMsg
        """

        QtGui.QApplication.restoreOverrideCursor()
        self.in_measure_distance_state = False
        self.wait_measure_distance_click = False
        self.graphics_measure_distance_item.hide()
        self.graphics_view.graphics_scene.update()
        self.emit("infoMsg", "")

    def stop_measure_angle(self):
        """Stops angle measurement

        :emits: infoMsg
        """

        QtGui.QApplication.restoreOverrideCursor()
        self.in_measure_angle_state = False
        self.wait_measure_angle_click = False
        self.graphics_measure_angle_item.hide()
        self.graphics_view.graphics_scene.update()
        self.emit("infoMsg", "")

    def stop_measure_area(self):
        """Stops area measurement

        :emits: infoMsg
        """

        QtGui.QApplication.restoreOverrideCursor()
        self.in_measure_area_state = False
        self.wait_measure_area_click = False
        self.graphics_measure_area_item.hide()
        self.graphics_view.graphics_scene.update()
        self.emit("infoMsg", "")

    def stop_move_beam_mark(self):
        """Stops to move beam mark

        :emits: infoMsg
        """

        QtGui.QApplication.restoreOverrideCursor()
        self.in_move_beam_mark_state = False
        self.graphics_move_beam_mark_item.hide()
        self.graphics_view.graphics_scene.update()
        self.beam_info_hwobj.set_beam_position(\
             self.graphics_move_beam_mark_item.end_coord[0],
             self.graphics_move_beam_mark_item.end_coord[1])
        self.emit("infoMsg", "")

    def stop_beam_define(self):
        """Stops beam define

        :emits: infoMsg
        """

        QtGui.QApplication.restoreOverrideCursor()
        self.in_beam_define_state = False
        self.wait_beam_define_click = False
        self.graphics_beam_define_item.hide()
        self.graphics_view.graphics_scene.update()
        self.emit("infoMsg", "")
        #self.beam_info_hwobj.set_slits_size(\
        #     self.graphics_beam_define_item.width_microns,
        #     self.graphics_beam_define_item.height_microns)
        self.diffractometer_hwobj.move_to_coord(\
             self.graphics_beam_define_item.center_coord[0],
             self.graphics_beam_define_item.center_coord[1])

    def start_centring(self, tree_click=None):
        """Starts centring procedure
 
        :param tree_click: centring with 3 clicks
        :type tree_click: bool
        :emits: - centringInProgress
                - infoMsg
        """ 
        self.emit("centringInProgress", True)
        if tree_click:
            self.set_centring_state(True) 
            self.diffractometer_hwobj.start_centring_method(\
                 self.diffractometer_hwobj.MANUAL3CLICK_MODE)
            self.emit("infoMsg", "3 click centring")
        else:
            self.diffractometer_hwobj.start_2D_centring(\
                 self.beam_position[0], self.beam_position[1])

    def accept_centring(self):
        """Accepts centring
        """

        self.diffractometer_hwobj.accept_centring()

    def reject_centring(self):
        """Rejects centring
        """ 

        self.diffractometer_hwobj.reject_centring()  

    def cancel_centring(self, reject=False): 
        """Cancels centring

        :param reject: reject position
        :type reject: bool
        """

        self.diffractometer_hwobj.cancel_centring_method(reject = reject)

    def start_visual_align(self):
        """Starts visual align procedure when two centring points are selected
           Orientates two points along the osc axes

        :emits: infoMsg
        """

        selected_points = self.get_selected_points()
        if len(selected_points) == 2:
            self.diffractometer_hwobj.visual_align(\
                 selected_points[0].get_centred_position(),
                 selected_points[1].get_centred_position())
            self.emit("infoMsg", "Visual align")
        else:
            msg = "Select two centred position (CTRL click) to continue"
            logging.getLogger("user_level_log").error(msg)  

    def create_line(self):
        """Creates helical line if two centring points selected
        """

        selected_points = self.get_selected_points()
        if len(selected_points) > 1:
            line = GraphicsLib.GraphicsItemLine(selected_points[0],
                                    selected_points[1])
            self.add_shape(line)
        else:
            msg = "Please select two points (with same kappa and phi) " + \
                  "to create a helical line"
            logging.getLogger("user_level_log").error(msg)

    def create_grid(self, spacing=(0, 0)):
        """Creates grid

        :param spacing: spacing between beams
        :type spacing: list with two floats (can be negative)        
        """ 

        self.graphics_grid_draw_item = GraphicsLib.GraphicsItemGrid(self, 
             self.beam_info_dict, spacing, self.pixels_per_mm)
        self.graphics_grid_draw_item.set_draw_mode(True) 
        self.graphics_grid_draw_item.index = self.grid_count
        self.grid_count += 1
        self.graphics_view.graphics_scene.addItem(self.graphics_grid_draw_item)
        self.wait_grid_drawing_click = True 

    def create_automatic_grid(self):
        """Creates automatic grid
        """ 
        
        auto_grid = GraphicsLib.GraphicsItemGrid(self, self.beam_info_dict,
             (0, 0), self.pixels_per_mm)
        auto_grid.index = self.grid_count
        auto_grid.set_draw_mode(True)
        self.grid_count += 1
        self.graphics_view.graphics_scene.addItem(auto_grid)
        shape_corner_coord = self.detect_shape_coord()
        #auto_grid.set_automatic_size(self.beam_position)
        auto_grid.set_automatic_size(shape_corner_coord)
        return auto_grid

    def refresh_camera(self):
        """To be deleted
        """

        self.beam_info_dict = self.beam_info_hwobj.get_beam_info()
        self.beam_info_changed(self.beam_info_dict) 

    def select_lines_and_grids(self):
        """Selects all lines and grids that are in the rectangle of
           item selection tool
        """

        select_start_coord = self.graphics_select_tool_item.start_coord
        select_end_coord = self.graphics_select_tool_item.end_coord
        select_middle_x = (select_start_coord[0] + select_end_coord[0]) / 2.0
        select_middle_y = (select_start_coord[1] + select_end_coord[1]) / 2.0
 
        for shape in self.shape_dict.values():
            if isinstance(shape, GraphicsLib.GraphicsItemLine):
                (start_point, end_point) = shape.get_graphics_points()
                if min(start_point.start_coord[0], end_point.start_coord[0]) < select_middle_x  < \
                   max(start_point.start_coord[0], end_point.start_coord[0]) and \
                   min(start_point.start_coord[1], end_point.start_coord[1]) < select_middle_y < \
                   max(start_point.start_coord[1], end_point.start_coord[1]):
                    shape.setSelected(True)

    def get_image_scale_list(self):
        """Returns list with available image scales

        :returns: list with floats
        """ 

        return self.image_scale_list

    def set_image_scale(self, image_scale, use_scale=False):
        """Scales scene
        
        :param image_scale: image scale
        :type image_scale: float 0 - 1.0 
        :param use_scale: enables/disables image scale
        :type use_scale: bool
        :emits: imageScaleChanged
        """
        scene_size = self.graphics_scene_size
        if image_scale == 1:
            use_scale = False
        if use_scale:
            self.image_scale = image_scale
            scene_size = [scene_size[0] * image_scale,
                          scene_size[1] * image_scale]
        else: 
            self.image_scale = None

        self.graphics_view.scene().setSceneRect(0, 0, \
             scene_size[0] - 10, scene_size[1] - 10)
        self.graphics_view.toggle_scrollbars_enable(self.image_scale > 1)
        self.emit('imageScaleChanged', self.image_scale)

    def get_image_scale(self):
        """Returns current scale factor of image
     
        :returns: float
        """

        return self.image_scale

    def auto_focus(self):
        """Starts auto focus
        """

        self.diffractometer_hwobj.start_auto_focus()

    def start_auto_centring(self):
        """Starts auto centring
        """
        self.emit("centringInProgress", True)
        self.diffractometer_hwobj.start_centring_method(\
             self.diffractometer_hwobj.C3D_MODE)
        self.emit("infoMsg", "Automatic centring")

    def set_display_beam_shapes(self, display_state):
        """Enables or disables beam shape drawing for graphics scene
           items (lines and grids)

        """
        for item in self.graphics_view.graphics_scene.items():
            if isinstance(item, GraphicsLib.GraphicsItem):
                item.set_display_beam_shape(display_state)
                self.graphics_view.graphics_scene.update()

    def detect_shape_coord(self):
        snapshot = self.camera_hwobj.get_frame(bw=True, return_as_array=False)
        snapshot_filename = os.path.join(tempfile.gettempdir(), "mxcube_sample_snapshot.png")
        snapshot.save(snapshot_filename)
        info, x, y = lucid.find_loop(snapshot_filename)
        surface_info = self.get_surface_info(self.camera_hwobj.get_frame(\
              bw=True, return_as_array=True))
        return ((50, 50), (400, 400))

    def get_surface_info(self, image_array):
        """
        hor_sum = image_array.sum(axis=0)
        ver_sum = image_array.sum(axis=1)
       
        half_max = hor_sum.max() / 2.0
        s = splrep(np.linspace(0, hor_sum.size, hor_sum.size), hor_sum - half_max)
        hor_roots = sproot(s)

        half_max = ver_sum.max() / 2.0
        s = splrep(np.linspace(0, ver_sum.size, ver_sum.size), ver_sum - half_max)
        ver_roots = sproot(s)
        """
        return

    def display_grid(self, state):
        self.graphics_scale_item.set_display_grid(state) 

    def take_scene_snapshots(self, filename):
        logging.getLogger("HWR").debug("Saving scene snapshot: %s" % filename)
        snapshot = self.get_snapshot()
        snapshot.save(filename)

    def display_radiation_damage(self, state):
        test = "Radiation dose per sample: "
        if state:
            self.graphics_scale_item.set_radiation_dose_info(test)
        else:
            self.graphics_scale_item.set_radiation_dose_info(None)
