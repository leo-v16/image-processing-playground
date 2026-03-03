import dearpygui.dearpygui as dpg
from core import FILTER_REGISTRY

class NodeManagerMixin:
    def add_pipeline_node(self, name="Custom Pipeline", p_name="", pos=[400, 300]):
        node = dpg.add_node(label=name, parent="node_editor", pos=pos, user_data="Pipeline Node")
        with dpg.node_attribute(label="In", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input Image")
        self.node_params[node] = {"pipeline_name": p_name}
        with dpg.node_attribute(label="Out", attribute_type=dpg.mvNode_Attr_Output, parent=node):
            dpg.add_text("Pipeline Result")
        dpg.configure_item(node, label=name)

    def add_filter_node(self, name="New Filter", pos=[400, 300]):
        if name not in FILTER_REGISTRY: return
        info = FILTER_REGISTRY[name]
        
        node = dpg.add_node(label=name, parent="node_editor", pos=pos, user_data=name)
        with dpg.node_attribute(label="In", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input Data")
        
        self.node_params[node] = {}
        for p in info["params"]:
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=node):
                if p["type"] == "int":
                    self.node_params[node][p["name"]] = dpg.add_slider_int(
                        label=p["label"], default_value=p["default"], 
                        min_value=p.get("min", 0), max_value=p.get("max", 100), width=100
                    )
                elif p["type"] in ["float", "double"]:
                    self.node_params[node][p["name"]] = dpg.add_slider_float(
                        label=p["label"], default_value=p["default"], 
                        min_value=p.get("min", 0.0), max_value=p.get("max", 10.0), width=100
                    )
        
        with dpg.node_attribute(label="Out", attribute_type=dpg.mvNode_Attr_Output, parent=node):
            dpg.add_text("Filtered Result")
        dpg.configure_item(node, label=name)

    def add_arithmetic_node(self, name="Add Images", pos=[400, 300]):
        node = dpg.add_node(label=name, parent="node_editor", pos=pos, user_data=name)
        with dpg.node_attribute(label="In A", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input A")
        with dpg.node_attribute(label="In B", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input B")
        with dpg.node_attribute(label="Out", attribute_type=dpg.mvNode_Attr_Output, parent=node):
            dpg.add_text("Result")
        dpg.configure_item(node, label=name)

    def link_callback(self, sender, app_data):
        target = app_data[1]
        for link in dpg.get_item_children(sender, 0) or []:
            if dpg.get_item_configuration(link).get("attr_2") == target: dpg.delete_item(link)
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    def delink_callback(self, sender, app_data):
        if dpg.does_item_exist(app_data): dpg.delete_item(app_data)

    def delete_selected(self, sender=None, app_data=None, user_data=None):
        if not dpg.does_item_exist("node_editor"): return
        for link in dpg.get_selected_links("node_editor"): dpg.delete_item(link)
        for node in dpg.get_selected_nodes("node_editor"):
            if dpg.get_item_label(node) not in ["SOURCE IMAGE", "RESULT IMAGE"]:
                pins = dpg.get_item_children(node, 1)
                for link in dpg.get_item_children("node_editor", 0):
                    cfg = dpg.get_item_configuration(link)
                    if cfg["attr_1"] in pins or cfg["attr_2"] in pins: dpg.delete_item(link)
                dpg.delete_item(node)
                # Safely remove from node_params
                if node in self.node_params:
                    del self.node_params[node]

    def clear_editor(self, sender=None, app_data=None, user_data=None):
        for link in dpg.get_item_children("node_editor", 0): dpg.delete_item(link)
        for node in dpg.get_item_children("node_editor", 1):
            if dpg.get_item_label(node) not in ["SOURCE IMAGE", "RESULT IMAGE"]:
                dpg.delete_item(node)
                # Safely remove from node_params
                if node in self.node_params:
                    del self.node_params[node]
