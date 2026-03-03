import dearpygui.dearpygui as dpg
import ctypes
from PIL import Image
from core import process_lib, DLL_LOADED

class EngineMixin:
    def get_node_output(self, pin_id, link_map, node_cache, w, h, source_override=None):
        if pin_id not in link_map:
            return None
            
        out_pin = link_map[pin_id]
        
        # Robust source pin identification
        is_source = False
        if out_pin == "source_pin":
            is_source = True
        else:
            try:
                if dpg.get_item_alias(out_pin) == "source_pin":
                    is_source = True
            except:
                pass
                
        if is_source:
            if source_override is not None:
                return bytearray(source_override)
            if self.input_image:
                return bytearray(self.input_image.copy().convert("RGBA").tobytes())
            return bytearray(w * h * 4)
        
        node = dpg.get_item_parent(out_pin)
        if node in node_cache:
            return bytearray(node_cache[node])
            
        # Determine node type from user_data (preferred) or label
        node_type = dpg.get_item_user_data(node)
        if not node_type or not isinstance(node_type, str):
            node_type = dpg.get_item_label(node)
            
        print(f"[ENGINE] Processing node type: {node_type} (ID: {node})")
        
        # Get input attributes
        children = dpg.get_item_children(node, 1)
        attrs = []
        for child in children:
            if dpg.get_item_configuration(child)["attribute_type"] == dpg.mvNode_Attr_Input:
                attrs.append(child)
        
        res = None
        
        # Pipeline Node Logic
        if node_type == "Pipeline Node":
            if node in self.node_params:
                p_name = self.node_params[node].get("pipeline_name")
                if p_name and attrs:
                    b_in = self.get_node_output(attrs[0], link_map, node_cache, w, h, source_override)
                    if b_in:
                        all_p = self._load_pipelines_json()
                        if p_name in all_p:
                            res = self.evaluate_sub_graph(all_p[p_name], b_in, w, h)
        
        # Arithmetic Node Logic
        elif node_type in ["Add Images", "Sub Images"]:
            if len(attrs) >= 2:
                b_a = self.get_node_output(attrs[0], link_map, node_cache, w, h, source_override)
                b_b = self.get_node_output(attrs[1], link_map, node_cache, w, h, source_override)
                if b_a and b_b:
                    res = bytearray(b_a)
                    c_a = (ctypes.c_ubyte * len(res)).from_buffer(res)
                    c_b = (ctypes.c_ubyte * len(b_b)).from_buffer(b_b)
                    if node_type == "Add Images":
                        process_lib.add_images(c_a, c_b, w, h, 4)
                    else:
                        process_lib.sub_images(c_a, c_b, w, h, 4)
                elif b_a:
                    res = bytearray(b_a)
                elif b_b:
                    res = bytearray(b_b)
        
        # Standard Filter Logic
        else:
            if attrs:
                b_in = self.get_node_output(attrs[0], link_map, node_cache, w, h, source_override)
                if b_in:
                    res = bytearray(b_in)
                    c_buf = (ctypes.c_ubyte * len(res)).from_buffer(res)
                    
                    if node_type == "Grayscale":
                        process_lib.gray_scale(c_buf, w, h, 4)
                    elif node_type == "Blur Filter":
                        rad = dpg.get_value(self.node_params[node]["radius"])
                        process_lib.blured(c_buf, w, h, 4, int(rad))
                    elif node_type == "Inverted":
                        process_lib.inverted(c_buf, w, h, 4)
                    elif node_type == "Max Filter":
                        rad = dpg.get_value(self.node_params[node]["radius"])
                        process_lib.max_filter(c_buf, w, h, 4, int(rad))
                    elif node_type == "Min Filter":
                        rad = dpg.get_value(self.node_params[node]["radius"])
                        process_lib.min_filter(c_buf, w, h, 4, int(rad))
                    elif node_type == "Median Filter":
                        rad = dpg.get_value(self.node_params[node]["radius"])
                        process_lib.median_filter(c_buf, w, h, 4, int(rad))
                    elif node_type == "Mode Filter":
                        rad = dpg.get_value(self.node_params[node]["radius"])
                        process_lib.mode_filter(c_buf, w, h, 4, int(rad))
                    elif node_type == "Threshold":
                        p_tag = self.node_params[node].get("threshold")
                        if p_tag:
                            res_val = dpg.get_value(p_tag)
                            process_lib.threshold(c_buf, w, h, 4, int(res_val))
                    elif node_type == "Log Transform":
                        p_tag = self.node_params[node].get("c")
                        if p_tag:
                            res_val = dpg.get_value(p_tag)
                            process_lib.log_transform(c_buf, w, h, 4, int(res_val))
                    elif node_type == "Power Transform":
                        p_tag_c = self.node_params[node].get("c")
                        p_tag_g = self.node_params[node].get("gamma")
                        if p_tag_c and p_tag_g:
                            val_c = dpg.get_value(p_tag_c)
                            val_g = dpg.get_value(p_tag_g)
                            process_lib.power_transform(c_buf, w, h, 4, int(val_c), float(val_g))
                    elif node_type == "1st X Derivative":
                        process_lib.first_derivative_x(c_buf, w, h, 4)
                    elif node_type == "1st Y Derivative":
                        process_lib.first_derivative_y(c_buf, w, h, 4)
                    elif node_type == "2nd X Derivative":
                        process_lib.second_derivative_x(c_buf, w, h, 4)
                    elif node_type == "2nd Y Derivative":
                        process_lib.second_derivative_y(c_buf, w, h, 4)
                    elif node_type == "Multiply":
                        p_tag = self.node_params[node].get("factor")
                        if p_tag:
                            factor = dpg.get_value(p_tag)
                            process_lib.multiply(c_buf, w, h, 4, float(factor))
                else:
                    res = bytearray(w * h * 4)
            else:
                res = bytearray(w * h * 4)
                
        if res is None:
            res = bytearray(w * h * 4)
            
        node_cache[node] = bytearray(res)
        return res

    def evaluate_sub_graph(self, data, input_bytes, w, h):
        nodes_data = data["nodes"]
        links_data = data["links"]
        cache = {}

        def eval_node(idx):
            if idx == "SOURCE IMAGE":
                return bytearray(input_bytes)
            if idx in cache:
                return bytearray(cache[idx])
            
            n_d = nodes_data[idx]
            label = n_d["label"] # For sub-graphs we still use stored label
            params = n_d.get("params", {})
            user_data = n_d.get("user_data")
            
            # Identify node type similarly to main graph
            node_type = user_data if user_data else label
            
            ins = []
            for l in links_data:
                if l["node2"] == idx:
                    ins.append(l)
            ins = sorted(ins, key=lambda x: x["pin2_idx"])
            
            res = None
            if node_type in ["Add Images", "Sub Images"]:
                b_a = eval_node(ins[0]["node1"]) if len(ins) > 0 else None
                b_b = eval_node(ins[1]["node1"]) if len(ins) > 1 else None
                if b_a and b_b:
                    res = bytearray(b_a)
                    c_a = (ctypes.c_ubyte * len(res)).from_buffer(res)
                    c_b = (ctypes.c_ubyte * len(b_b)).from_buffer(b_b)
                    if node_type == "Add Images":
                        process_lib.add_images(c_a, c_b, w, h, 4)
                    else:
                        process_lib.sub_images(c_a, c_b, w, h, 4)
                elif b_a:
                    res = bytearray(b_a)
                elif b_b:
                    res = bytearray(b_b)
            elif "pipeline_name" in params:
                b_in = eval_node(ins[0]["node1"]) if ins else None
                if b_in:
                    all_p = self._load_pipelines_json()
                    p_name = params["pipeline_name"]
                    if p_name in all_p:
                        res = self.evaluate_sub_graph(all_p[p_name], b_in, w, h)
            else:
                b_in = eval_node(ins[0]["node1"]) if ins else None
                if b_in:
                    res = bytearray(b_in)
                    c_buf = (ctypes.c_ubyte * len(res)).from_buffer(res)
                    if node_type == "Grayscale":
                        process_lib.gray_scale(c_buf, w, h, 4)
                    elif node_type == "Blur Filter":
                        process_lib.blured(c_buf, w, h, 4, int(params.get("radius", 1)))
                    elif node_type == "Inverted":
                        process_lib.inverted(c_buf, w, h, 4)
                    elif node_type == "Max Filter":
                        process_lib.max_filter(c_buf, w, h, 4, int(params.get("radius", 1)))
                    elif node_type == "Min Filter":
                        process_lib.min_filter(c_buf, w, h, 4, int(params.get("radius", 1)))
                    elif node_type == "Median Filter":
                        process_lib.median_filter(c_buf, w, h, 4, int(params.get("radius", 1)))
                    elif node_type == "Mode Filter":
                        process_lib.mode_filter(c_buf, w, h, 4, int(params.get("radius", 1)))
                    elif node_type == "Threshold":
                        process_lib.threshold(c_buf, w, h, 4, int(params.get("threshold", 128)))
                    elif node_type == "Log Transform":
                        process_lib.log_transform(c_buf, w, h, 4, int(params.get("c", 30)))
                    elif node_type == "Power Transform":
                        process_lib.power_transform(c_buf, w, h, 4, int(params.get("c", 1)), float(params.get("gamma", 1.2)))
                    elif node_type == "1st X Derivative":
                        process_lib.first_derivative_x(c_buf, w, h, 4)
                    elif node_type == "1st Y Derivative":
                        process_lib.first_derivative_y(c_buf, w, h, 4)
                    elif node_type == "2nd X Derivative":
                        process_lib.second_derivative_x(c_buf, w, h, 4)
                    elif node_type == "2nd Y Derivative":
                        process_lib.second_derivative_y(c_buf, w, h, 4)
                    elif node_type == "Multiply":
                        process_lib.multiply(c_buf, w, h, 4, float(params.get("factor", 1.0)))
            
            if res is None:
                res = bytearray(w * h * 4)
            cache[idx] = bytearray(res)
            return res

        final_link = None
        for l in links_data:
            if l["node2"] == "RESULT IMAGE":
                final_link = l
                break
        
        if final_link:
            return eval_node(final_link["node1"])
        return bytearray(w * h * 4)

    def process_pipeline(self, sender=None, app_data=None, user_data=None):
        if not self.input_image or not DLL_LOADED:
            print("[ENGINE] Aborted: Missing image or DLL not loaded.")
            return
            
        w, h = self.input_image.size
        # Map Input Pin -> Output Pin
        links = dpg.get_item_children("node_editor", 0)
        link_map = {}
        for l in links:
            config = dpg.get_item_configuration(l)
            link_map[config["attr_2"]] = config["attr_1"]
        
        print("[ENGINE] Evaluating Graph...")
        # Get result pin reliably
        res_pin_id = dpg.get_alias_id("result_pin")
        if not res_pin_id:
            res_pin_id = "result_pin"
            
        final_bytes = self.get_node_output(res_pin_id, link_map, {}, w, h)
        
        if final_bytes:
            self.output_image = Image.frombytes("RGBA", (w, h), bytes(final_bytes))
            self._update_texture_from_image(self.output_image, "output_tex", "output_image_widget")
            print("[ENGINE] Pipeline processed successfully.")
        else:
            print("[ENGINE] Pipeline evaluation returned no data.")
