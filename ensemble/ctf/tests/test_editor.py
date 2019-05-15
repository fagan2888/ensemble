from __future__ import unicode_literals
import unittest

from enable.testing import EnableTestAssistant
from traits_enaml.testing.enaml_test_assistant import EnamlTestAssistant

from ensemble.ctf.api import (CtfEditor, ColorNode, OpacityNode,
                              WindowColorNode, WindowOpacityNode,
                              WindowComponent)
from ensemble.ctf.window_function_component import WindowTypeAction


def get_color(starting_color=None):
    if starting_color:
        return starting_color
    return (0.0, 1.0, 0.0)


class TestEditor(EnamlTestAssistant, EnableTestAssistant, unittest.TestCase):

    def setUp(self):
        EnamlTestAssistant.setUp(self)

        enaml_source = b"""
from enaml.widgets.api import MainWindow
from traits_enaml.widgets.enable_canvas import EnableCanvas

enamldef MainView(MainWindow):
    attr editor

    initial_size = (400, 100)

    EnableCanvas:
        component << editor
"""

        editor = CtfEditor(bounds=(400, 100),
                           prompt_color_selection=get_color)

        function = editor.function.copy()
        function.color.insert(ColorNode(center=0.25, color=(1.0, 0.0, 0.0)))
        function.opacity.insert(OpacityNode(center=0.5, opacity=0.5))
        window_col = WindowColorNode(center=0.75, color=(0.0, 1.0, 1.0))
        window_op = WindowOpacityNode(center=0.75, opacity=0.5,
                                      window_type='hanning')
        function.add_linked_nodes(window_col, window_op)
        editor.function = function

        self.editor = editor
        self.view, _ = self.parse_and_create(enaml_source, editor=self.editor)

        with self.event_loop():
            self.view.show()

    def tearDown(self):
        self.editor = None
        self.view = None

        EnamlTestAssistant.tearDown(self)

    def test_mouse_drag_alpha(self):
        editor = self.editor

        # Grab the second opacity node and compute its screen position.
        node = editor.function.opacity.node_at(1)
        initial_center, initial_opacity = node.center, node.opacity
        w, h = editor.width, editor.height
        pos = (w * initial_center, h * initial_opacity)

        initial_pos = (pos[0] + editor.padding_left,
                       pos[1] + editor.padding_bottom)
        middle_pos = (initial_pos[0] + 20, initial_pos[1])
        final_pos = (initial_pos[0] + 40, initial_pos[1])

        # Move the opacity node around.
        with self.assertTraitChanges(node, 'center'), \
             self.assertTraitChanges(node, 'opacity'):  # noqa
                self.press_move_release(editor,
                                        [initial_pos, middle_pos, final_pos])

        # Ask for a redraw to test re-drawing.
        with self.event_loop():
            editor.request_redraw()

    def test_mouse_drag_color(self):
        editor = self.editor

        # Grab the second color node and compute its screen position.
        node = editor.function.color.node_at(1)
        initial_center = node.center
        w, h = editor.width, editor.height
        pos = (w * initial_center, h // 2)

        initial_pos = (pos[0] + editor.padding_left,
                       pos[1] + editor.padding_bottom)
        middle_pos = (initial_pos[0] + 20, initial_pos[1])
        final_pos = (initial_pos[0] + 40, initial_pos[1])

        # Move the color node around.
        with self.assertTraitChanges(node, 'center'):
            self.press_move_release(editor,
                                    [initial_pos, middle_pos, final_pos])

        # Ask for a redraw to test re-drawing.
        with self.event_loop():
            editor.request_redraw()

    def test_set_window_type(self):
        editor = self.editor
        function = editor.function
        component = [com for com in editor.components
                     if isinstance(com, WindowComponent)][0]
        node = function.opacity.node_at(2)
        action = WindowTypeAction(name='Trapezoid', function=function,
                                  component=component)

        # change the window_type
        with self.assertTraitChanges(node, 'window_type'):
            action.perform(None)


if __name__ == '__main__':
    unittest.main()
