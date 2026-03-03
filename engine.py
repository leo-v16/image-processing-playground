import dearpygui.dearpygui as dpg
import ctypes
from core import process_lib, DLL_LOADED, FILTER_REGISTRY

class EngineMixin:
    def get_node_output(self, pin_id, link_map, node_cache, w, h, source_override=None):
        if pin_id not in link_map: return None
        out_pin = link_map[pin_id]
        if out_pin == "source_pin" or dpg.get_item_alias(out_pin) == "source_pin":
            return bytearray(source_override) if source_override is not None else bytearray(self.input_image.copy().convert("RGBA").tobytes())
        
        node = dpg.get_item_parent(out_pin)
        if node in node_cache: return bytearray(node_cache[node])
            
        label = dpg.get_item_label(node)
        node_type = dpg.get_item_user_data(node) or label
        attrs = [c for c in dpg.get_item_children(node, 1) if dpg.get_item_configuration(c)["attribute_type"] == dpg.mvNode_Attr_Input]
        
        res = None
        if node_type == "Pipeline Node":
            p_name = self.node_params[node]["pipeline_name"]
            b_in = self.get_node_output(attrs[0], link_map, node_cache, w, h, source_override)
            if b_in:
                all_p = self._load_pipelines_json()
                if p_name in all_p: res = self.evaluate_sub_graph(all_p[p_name], b_in, w, h)
        elif node_type in ["Add Images", "Sub Images"]:
            b_a = self.get_node_output(attrs[0], link_map, node_cache, w, h, source_override)
            b_b = self.get_node_output(attrs[1], link_map, node_cache, w, h, source_override)
            if b_a and b_b:
                res = bytearray(b_a)
                c_a, c_b = (ctypes.c_ubyte * len(res)).from_buffer(res), (ctypes.c_ubyte * len(b_b)).from_buffer(b_b)
                if node_type == "Add Images": process_lib.add_images(c_a, c_b, w, h, 4)
                else: process_lib.sub_images(c_a, c_b, w, h, 4)
            else: res = b_a or b_b or bytearray(w*h*4)
        elif node_type in FILTER_REGISTRY:
            b_in = self.get_node_output(attrs[0], link_map, node_cache, w, h, source_override)
            if b_in:
                res = bytearray(b_in)
                info = FILTER_REGISTRY[node_type]
                args = [(ctypes.c_ubyte * len(res)).from_buffer(res), w, h, 4]
                for p in info["params"]:
                    val = dpg.get_value(self.node_params[node][p["name"]])
                    args.append(val)
                getattr(process_lib, info["func"])(*args)
            else: res = bytearray(w*h*4)
                
        node_cache[node] = bytearray(res) if res else None
        return res

    def evaluate_sub_graph(self, data, input_bytes, w, h):
        nodes, links, cache = data["nodes"], data["links"], {}
        def eval_node(idx):
            if idx == "SOURCE IMAGE": return bytearray(input_bytes)
            if idx in cache: return bytearray(cache[idx])
            n_d = nodes[idx]
            label, params = n_d["label"], n_d.get("params", {})
            user_data = n_d.get("user_data", label)
            ins = sorted([l for l in links if l["node2"] == idx], key=lambda x: x["pin2_idx"])
            res = None
            if user_data in ["Add Images", "Sub Images"]:
                b_a, b_b = eval_node(ins[0]["node1"]) if len(ins) > 0 else None, eval_node(ins[1]["node1"]) if len(ins) > 1 else None
                if b_a and b_b:
                    res = bytearray(b_a)
                    c_a, c_b = (ctypes.c_ubyte * len(res)).from_buffer(res), (ctypes.c_ubyte * len(b_b)).from_buffer(b_b)
                    if user_data == "Add Images": process_lib.add_images(c_a, c_b, w, h, 4)
                    else: process_lib.sub_images(c_a, c_b, w, h, 4)
                else: res = b_a or b_b or bytearray(w*h*4)
            elif "pipeline_name" in params:
                b_in = eval_node(ins[0]["node1"]) if ins else None
                if b_in:
                    all_p = self._load_pipelines_json()
                    if params["pipeline_name"] in all_p: res = self.evaluate_sub_graph(all_p[params["pipeline_name"]], b_in, w, h)
            elif user_data in FILTER_REGISTRY:
                b_in = eval_node(ins[0]["node1"]) if ins else None
                if b_in:
                    res = bytearray(b_in)
                    info = FILTER_REGISTRY[user_data]
                    args = [(ctypes.c_ubyte * len(res)).from_buffer(res), w, h, 4]
                    for p in info["params"]: args.append(params.get(p["name"], p["default"]))
                    getattr(process_lib, info["func"])(*args)
                else: res = bytearray(w*h*4)
            res = res or bytearray(w*h*4)
            cache[idx] = bytearray(res)
            return res
        final = next((l for l in links if l["node2"] == "RESULT IMAGE"), None)
        return eval_node(final["node1"]) if final else bytearray(w * h * 4)

    def process_pipeline(self, sender=None, app_data=None, user_data=None):
        if not self.input_image or not DLL_LOADED: return
        w, h = self.input_image.size
        links = dpg.get_item_children("node_editor", 0)
        link_map = {dpg.get_item_configuration(l)["attr_2"]: dpg.get_item_configuration(l)["attr_1"] for l in links}
        final_bytes = self.get_node_output(dpg.get_alias_id("result_pin"), link_map, {}, w, h)
        if final_bytes:
            from PIL import Image
            self.output_image = Image.frombytes("RGBA", (w, h), bytes(final_bytes))
            self._update_texture_from_image(self.output_image, "output_tex", "output_image_widget")
