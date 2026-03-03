import dearpygui.dearpygui as dpg

class NodeManagerMixin:
    def add_pipeline_node(self, name="Custom Pipeline", p_name="", pos=[400, 300]):
        # We store the pipeline type/name in user_data for 100% reliability
        node = dpg.add_node(
            label=name, 
            parent="node_editor", 
            pos=pos, 
            user_data="Pipeline Node"
        )
        
        with dpg.node_attribute(label="In", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input Image")
        
        # Store the specific pipeline to run in node_params
        self.node_params[node] = {"pipeline_name": p_name}
        
        with dpg.node_attribute(label="Out", attribute_type=dpg.mvNode_Attr_Output, parent=node):
            dpg.add_text("Pipeline Result")
            
        dpg.configure_item(node, label=name)

    def link_callback(self, sender, app_data):
        target_input = app_data[1]
        all_links = dpg.get_item_children(sender, 0)
        if all_links:
            for link in all_links:
                if dpg.get_item_configuration(link).get("attr_2") == target_input:
                    dpg.delete_item(link)
        
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    def delink_callback(self, sender, app_data):
        if dpg.does_item_exist(app_data):
            dpg.delete_item(app_data)

    def add_filter_node(self, name="New Filter", pos=[400, 300]):
        # Store the filter name in user_data so the engine doesn't rely on the label
        node = dpg.add_node(
            label=name, 
            parent="node_editor", 
            pos=pos, 
            user_data=name
        )
        
        with dpg.node_attribute(label="In", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input Data")
        
        self.node_params[node] = {}
        if name == "Threshold":
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=node):
                self.node_params[node]["threshold"] = dpg.add_slider_int(
                    label="Val", default_value=128, min_value=0, max_value=255, width=100
                )
        elif name == "Log Transform":
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=node):
                self.node_params[node]["c"] = dpg.add_input_int(
                    label="C", default_value=30, width=100
                )
        elif name == "Power Transform":
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=node):
                self.node_params[node]["c"] = dpg.add_input_int(
                    label="C", default_value=1, width=100
                )
                self.node_params[node]["gamma"] = dpg.add_input_float(
                    label="G", default_value=1.2, width=100
                )
        elif name in ["Blur Filter", "Max Filter", "Min Filter", "Median Filter", "Mode Filter"]:
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=node):
                self.node_params[node]["radius"] = dpg.add_slider_int(
                    label="Radius", default_value=1, min_value=1, max_value=20, width=100
                )
        elif name == "Multiply":
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=node):
                self.node_params[node]["factor"] = dpg.add_slider_float(
                    label="Factor", default_value=1.0, min_value=0.0, max_value=10.0, width=100
                )
        
        with dpg.node_attribute(label="Out", attribute_type=dpg.mvNode_Attr_Output, parent=node):
            dpg.add_text("Filtered Result")
            
        dpg.configure_item(node, label=name)

    def add_arithmetic_node(self, name="Add Images", pos=[400, 300]):
        node = dpg.add_node(
            label=name, 
            parent="node_editor", 
            pos=pos, 
            user_data=name
        )
        
        with dpg.node_attribute(label="In A", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input A")
        with dpg.node_attribute(label="In B", attribute_type=dpg.mvNode_Attr_Input, parent=node):
            dpg.add_text("Input B")
        with dpg.node_attribute(label="Out", attribute_type=dpg.mvNode_Attr_Output, parent=node):
            dpg.add_text("Result")
            
        dpg.configure_item(node, label=name)

    def delete_selected(self, sender=None, app_data=None, user_data=None):
        if not dpg.does_item_exist("node_editor"):
            return
            
        for link in dpg.get_selected_links("node_editor"):
            if dpg.does_item_exist(link):
                dpg.delete_item(link)
            
        for node in dpg.get_selected_nodes("node_editor"):
            if dpg.does_item_exist(node):
                node_type = dpg.get_item_user_data(node)
                if not node_type:
                    node_type = dpg.get_item_label(node)
                    
                if node_type not in ["SOURCE IMAGE", "RESULT IMAGE"]:
                    pins = dpg.get_item_children(node, 1)
                    all_links = dpg.get_item_children("node_editor", 0)
                    for link in all_links:
                        cfg = dpg.get_item_configuration(link)
                        if cfg["attr_1"] in pins or cfg["attr_2"] in pins:
                            dpg.delete_item(link)
                    
                    dpg.delete_item(node)
                    if node in self.node_params:
                        del self.node_params[node]

    def clear_editor(self, sender=None, app_data=None, user_data=None):
        links = dpg.get_item_children("node_editor", 0)
        for link in links:
            dpg.delete_item(link)
            
        nodes = dpg.get_item_children("node_editor", 1)
        for node in nodes:
            node_type = dpg.get_item_user_data(node)
            if not node_type:
                node_type = dpg.get_item_label(node)
                
            if node_type not in ["SOURCE IMAGE", "RESULT IMAGE"]:
                dpg.delete_item(node)
                if node in self.node_params:
                    del self.node_params[node]
