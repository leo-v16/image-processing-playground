import dearpygui.dearpygui as dpg
from core import WINDOW_WIDTH, WINDOW_HEIGHT, FILTER_REGISTRY

class UIMixin:
    def setup_ui(self):
        # 1. File Dialogs
        with dpg.file_dialog(directory_selector=False, show=False, callback=self.file_dialog_callback, tag="image_selector", width=700, height=450, modal=True, default_path="images"):
            dpg.add_file_extension("Image Files{.png,.jpg,.jpeg,.bmp,.webp}")
        with dpg.file_dialog(directory_selector=False, show=False, callback=self.save_image_callback, tag="image_saver", width=700, height=450, modal=True, default_path="images", default_filename="processed_image.png"):
            dpg.add_file_extension("PNG (*.png){.png}"); dpg.add_file_extension("JPEG (*.jpg){.jpg,.jpeg}")
        
        # 2. Modals
        with dpg.window(label="Save Pipeline", tag="save_pipeline_modal", modal=True, show=False, autosize=True):
            dpg.add_input_text(tag="pipeline_name_input", width=200); dpg.add_button(label="Save", callback=self.save_pipeline)
        with dpg.window(label="Delete Pipeline", tag="delete_pipeline_modal", modal=True, show=False, autosize=True):
            dpg.add_combo(tag="delete_pipeline_combo", width=200); dpg.add_button(label="Delete", callback=self.delete_pipeline_callback)
        
        # 3. Dynamic Menu Builder helper
        def build_dynamic_menus(parent_tag, from_context=False):
            categories = {}
            for name, info in FILTER_REGISTRY.items():
                cat = info["category"]
                if cat not in categories: categories[cat] = []
                categories[cat].append(name)
            
            for cat, filters in categories.items():
                with dpg.menu(label=cat, parent=parent_tag):
                    for f in filters:
                        cb = lambda s, a, u: self.add_filter_node(u, dpg.get_item_pos(parent_tag) if from_context else [400, 300])
                        dpg.add_menu_item(label=f, user_data=f, callback=cb)

        # 4. Context Menu
        with dpg.window(tag="context_menu", show=False, no_title_bar=True, autosize=True):
            build_dynamic_menus("context_menu", from_context=True)
            with dpg.menu(label="Arithmetic"):
                for ar in ["Add Images", "Sub Images"]: dpg.add_menu_item(label=ar, user_data=ar, callback=lambda s,a,u: self.add_arithmetic_node(u, dpg.get_item_pos("context_menu")))
            with dpg.menu(label="Your Pipelines", tag="your_pipelines_context_menu"): pass
            dpg.add_separator()
            dpg.add_menu_item(label="Delete Selected", callback=self.delete_selected)
        
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=lambda: dpg.configure_item("context_menu", show=dpg.is_item_hovered("node_editor"), pos=dpg.get_mouse_pos(local=False)))
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=lambda: dpg.configure_item("context_menu", show=False))
            dpg.add_key_press_handler(key=dpg.mvKey_Delete, callback=self.delete_selected)

        # 5. Main Window
        with dpg.window(label="IIP(Image Processing Playground)", width=WINDOW_WIDTH, height=WINDOW_HEIGHT, no_move=True, no_close=True, no_collapse=True):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open Image...", callback=lambda: dpg.show_item("image_selector"))
                    dpg.add_menu_item(label="Save Result...", callback=lambda: dpg.show_item("image_saver"))
                with dpg.menu(label="Pipelines", tag="pipelines_menu"):
                    dpg.add_menu_item(label="Save Current Pipeline...", callback=lambda: dpg.show_item("save_pipeline_modal"))
                    dpg.add_menu_item(label="Delete Pipeline...", callback=lambda: dpg.show_item("delete_pipeline_modal"))
                with dpg.menu(label="Add Node", tag="add_node_menu"):
                    build_dynamic_menus("add_node_menu")
                    with dpg.menu(label="Arithmetic"):
                        for ar in ["Add Images", "Sub Images"]: dpg.add_menu_item(label=ar, user_data=ar, callback=lambda s,a,u: self.add_arithmetic_node(u))
                    with dpg.menu(label="Your Pipelines", tag="your_pipelines_menu"): pass
                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(label="Delete Selected", callback=self.delete_selected)
                    dpg.add_menu_item(label="Clear Connections", callback=lambda: [dpg.delete_item(l) for l in dpg.get_item_children("node_editor", 0)])
                    dpg.add_menu_item(label="Reset Editor", callback=self.clear_editor)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="PROCESS PIPELINE", callback=self.process_pipeline, width=200)
                dpg.add_button(label="SAVE RESULT", callback=lambda: dpg.show_item("image_saver"), width=150)
                dpg.add_button(label="DELETE SELECTED", callback=self.delete_selected, width=150)
                dpg.add_button(label="CLEAR", callback=self.clear_editor, width=100)
            
            with dpg.node_editor(tag="node_editor", callback=self.link_callback, delink_callback=self.delink_callback):
                with dpg.node(label="SOURCE IMAGE", pos=[20, 50]):
                    with dpg.node_attribute(tag="source_pin", attribute_type=dpg.mvNode_Attr_Output):
                        dpg.add_image(texture_tag="blank_tex", tag="input_image_widget")
                        dpg.add_button(label="Select New Image...", tag="select_image_button", width=255, callback=lambda: dpg.show_item("image_selector"))
                with dpg.node(label="RESULT IMAGE", pos=[900, 50]):
                    with dpg.node_attribute(tag="result_pin", attribute_type=dpg.mvNode_Attr_Input):
                        dpg.add_image(texture_tag="blank_tex", tag="output_image_widget")

    def file_dialog_callback(self, sender, app_data):
        if app_data.get('file_path_name'): self._update_texture_from_file(app_data['file_path_name'], "input_tex", "input_image_widget")

    def save_image_callback(self, sender, app_data):
        if app_data.get('file_path_name') and self.output_image:
            (self.output_image if app_data['file_path_name'].lower().endswith(".png") else self.output_image.convert("RGB")).save(app_data['file_path_name'])
