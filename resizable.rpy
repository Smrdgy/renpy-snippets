"""
Args:
    resize_padding (int): A padding around the inner side of the Drag where you can resize the Drag instead of just dragging
    pos (int, int): Initial position of the Drag
    size (int, int): Initial size of the Drag
    min_size (int, int): Minimal size of the Drag

Usage example:
    screen example():
        use resizable(resize_padding=5, pos=(12, 5), size=(100, 120)):
            text "Hello world!"
"""
screen resizable(resize_padding=20, pos=(0, 0), size=(200, 150), min_size=(50, 50)):
    python:
        class DragController(renpy.ui.Action):
            def __init__(self, pos, size, min_size, resize_padding):
                self.min_size = min_size
                self.x = pos[0]
                self.y = pos[1]
                self.width = size[0]
                self.height = size[1]
                self.resize_padding = resize_padding

                self.drag_x = None
                self.drag_y = None
                self.drag_dir = None

            # A function that is called when the mouse is pressed down on the Drag.
            def handle_activated(self, drags):
                cursor_pos_x, cursor_pos_y = renpy.get_mouse_pos()
                d = drags[0]

                self.width = int(d.w)
                self.height = int(d.h)

                relative_x = cursor_pos_x - d.x
                relative_y = cursor_pos_y - d.y

                self.drag_dir = self._get_edge_at_point(relative_x, relative_y)
                
                self.drag_x = cursor_pos_x
                self.drag_y = cursor_pos_y

            # A function that is called when the Drag is being dragged.
            def handle_dragging(self, drags):
                cursor_pos_x, cursor_pos_y = renpy.get_mouse_pos()
                d = drags[0]

                # Check whether to resize or just drag the Drag.
                if self.drag_dir is not None:
                    # Resize

                    # Diff between the old cursor pos and a new one
                    dx = cursor_pos_x - self.drag_x
                    dy = cursor_pos_y - self.drag_y

                    if 'right' in self.drag_dir:
                        self.width = self.width + dx
                    elif 'left' in self.drag_dir:
                        self.width = self.width - dx
                        self.x += dx

                    if 'bottom' in self.drag_dir:
                        self.height = self.height + dy
                    elif 'top' in self.drag_dir:
                        self.height = self.height - dy
                        self.y += dy
                    
                    # Prevent Drag from moving while resizing
                    d.snap(self.x, self.y)

                    # Clamp the new size
                    self.width = int(max(self.min_size[0], self.width))
                    self.height = int(max(self.min_size[1], self.height))

                else:
                    # Drag

                    self.x = d.x
                    self.y = d.y

                self.drag_x = cursor_pos_x
                self.drag_y = cursor_pos_y

                renpy.restart_interaction()
                    
            # A function that is called when the Drag has been dragged.
            def handle_dragged(self, drags, drop):
                self.handle_dragging(drags)

                if not self.drag_dir:
                    d = drags[0]
                    self.x = d.x
                    self.y = d.y

                    return

                self.drag_x = None
                self.drag_y = None
                self.drag_dir = None

            # From relative X and Y coords, determine which edge or a corner is being dragged and can be used for resizing.
            # Possible return values: "top", "left", "right", "bottom", "top_left", "top_right", "bottom_left", "bottom_right", None
            def _get_edge_at_point(self, x, y):
                pad = self.resize_padding

                directions = []
                if x <= pad:
                    directions.append("left")
                elif x >= self.width - pad:
                    directions.append("right")

                if y <= pad:
                    directions.append("top")
                elif y >= self.height - pad:
                    directions.append("bottom")

                if directions:
                    return "_".join(directions)

                return None

    default drag_controller = DragController(pos=pos, size=size, min_size=min_size, resize_padding=resize_padding)

    drag:
        draggable True
        drag_handle (0, 0, 1.0, 1.0)
        droppable False
        pos (drag_controller.x, drag_controller.y)
        xsize drag_controller.width
        ysize drag_controller.height
        activated drag_controller.handle_activated
        dragging drag_controller.handle_dragging
        dragged drag_controller.handle_dragged

        # This frame is for visualization of the resize_padding and can be removed 
        frame:
            background "#fff"
            padding (drag_controller.resize_padding, drag_controller.resize_padding)

            # This frame can be also be removed, it's here only because it's very likely you will want to add some sort of background
            frame:
                viewport:
                    transclude
