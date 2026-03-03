import dearpygui.dearpygui as dpg
import os
import json
from core import PIPELINES_FILE

class PersistenceMixin:
    def _load_pipelines_json(self):
        if not os.path.exists(PIPELINES_FILE):
            return {}
        try:
            with open(PIPELINES_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception as e:
            print(f"[PERSISTENCE] Error loading {PIPELINES_FILE}: {e}")
            return {}

    def save_pipeline(self, sender, app_data, user_data):
        name = dpg.get_value("pipeline_name_input")
        if not name:
            return
            
        nodes_data = []
        links_data = []
        all_nodes = dpg.get_item_children("node_editor", 1)
        id_to_idx = {}
        
        # 1. Capture Nodes
        for i, node in enumerate(all_nodes):
            label = dpg.get_item_label(node)
            if label in ["SOURCE IMAGE", "RESULT IMAGE"]:
                id_to_idx[node] = label
                continue
                
            pos = dpg.get_item_pos(node)
            params = {}
            if node in self.node_params:
                for p_name, p_tag in self.node_params[node].items():
                    if dpg.does_item_exist(p_tag):
                        params[p_name] = dpg.get_value(p_tag)
                    else:
                        params[p_name] = p_tag
            
            nodes_data.append({
                "label": label,
                "pos": pos,
                "params": params,
                "user_data": dpg.get_item_user_data(node)
            })
            id_to_idx[node] = len(nodes_data) - 1
            
        # 2. Capture Links
        all_links = dpg.get_item_children("node_editor", 0)
        for link in all_links:
            cfg = dpg.get_item_configuration(link)
            p1, p2 = cfg["attr_1"], cfg["attr_2"]
            n1, n2 = dpg.get_item_parent(p1), dpg.get_item_parent(p2)
            
            l_data = {
                "node1": id_to_idx[n1],
                "pin1_idx": dpg.get_item_children(n1, 1).index(p1),
                "node2": id_to_idx[n2],
                "pin2_idx": dpg.get_item_children(n2, 1).index(p2)
            }
            links_data.append(l_data)
            
        all_p = self._load_pipelines_json()
        all_p[name] = {"nodes": nodes_data, "links": links_data}
        
        with open(PIPELINES_FILE, "w") as f:
            json.dump(all_p, f, indent=4)
            
        dpg.configure_item("save_pipeline_modal", show=False)
        self.update_pipeline_menu()

    def load_pipeline(self, sender, app_data, user_data):
        all_p = self._load_pipelines_json()
        if user_data not in all_p:
            return
            
        data = all_p[user_data]
        self.clear_editor()
        
        created_nodes = {}
        source_id = None
        result_id = None
        
        all_runtime_nodes = dpg.get_item_children("node_editor", 1)
        for n in all_runtime_nodes:
            lbl = dpg.get_item_label(n)
            if lbl == "SOURCE IMAGE":
                source_id = n
            elif lbl == "RESULT IMAGE":
                result_id = n
                
        # 1. Recreate Nodes
        for i, n_d in enumerate(data["nodes"]):
            label = n_d["label"]
            pos = n_d["pos"]
            params = n_d.get("params", {})
            stored_user_data = n_d.get("user_data")
            
            if label in ["Add Images", "Sub Images"] or stored_user_data in ["Add Images", "Sub Images"]:
                self.add_arithmetic_node(label, pos)
            elif "pipeline_name" in params:
                self.add_pipeline_node(label, params["pipeline_name"], pos)
            else:
                self.add_filter_node(label, pos)
                
            new_node = dpg.get_item_children("node_editor", 1)[-1]
            created_nodes[i] = new_node
            
            if stored_user_data:
                dpg.configure_item(new_node, user_data=stored_user_data)
            
            if new_node in self.node_params:
                for p_n, val in params.items():
                    p_tag = self.node_params[new_node].get(p_n)
                    if p_tag and dpg.does_item_exist(p_tag):
                        dpg.set_value(p_tag, val)
                            
        # 2. Recreate Links
        id_map = created_nodes.copy()
        id_map["SOURCE IMAGE"] = source_id
        id_map["RESULT IMAGE"] = result_id
        
        for l_d in data["links"]:
            n1 = id_map.get(l_d["node1"])
            n2 = id_map.get(l_d["node2"])
            if n1 and n2:
                p1 = dpg.get_item_children(n1, 1)[l_d["pin1_idx"]]
                p2 = dpg.get_item_children(n2, 1)[l_d["pin2_idx"]]
                dpg.add_node_link(p1, p2, parent="node_editor")

    def update_pipeline_menu(self):
        if not dpg.does_item_exist("pipelines_menu"):
            return
            
        items = dpg.get_item_children("pipelines_menu", 1)
        for item in items:
            if dpg.get_item_label(item) not in ["Save Current Pipeline...", "Delete Pipeline..."]:
                dpg.delete_item(item)
                
        for menu in ["your_pipelines_menu", "your_pipelines_context_menu"]:
            if dpg.does_item_exist(menu):
                for child in dpg.get_item_children(menu, 1):
                    dpg.delete_item(child)
                    
        all_p = self._load_pipelines_json()
        
        # Populate the Delete Pipeline Combo Box with current names
        pipeline_names = list(all_p.keys())
        if dpg.does_item_exist("delete_pipeline_combo"):
            dpg.configure_item("delete_pipeline_combo", items=pipeline_names)
            if pipeline_names:
                dpg.set_value("delete_pipeline_combo", pipeline_names[0])
            else:
                dpg.set_value("delete_pipeline_combo", "")

        if all_p:
            dpg.add_separator(parent="pipelines_menu")
            for name in all_p.keys():
                dpg.add_menu_item(label=f"Load {name}", callback=self.load_pipeline, user_data=name, parent="pipelines_menu")
                dpg.add_menu_item(label=name, user_data=name, callback=lambda s, a, u: self.add_pipeline_node(u, u), parent="your_pipelines_menu")
                dpg.add_menu_item(label=name, user_data=name, callback=lambda s, a, u: self.add_pipeline_node(u, u, dpg.get_item_pos("context_menu")), parent="your_pipelines_context_menu")

    def delete_pipeline_callback(self, sender, app_data, user_data):
        # Read from the combo box instead of an input field
        name = dpg.get_value("delete_pipeline_combo")
        if not name:
            return
            
        all_p = self._load_pipelines_json()
        if name in all_p:
            del all_p[name]
            with open(PIPELINES_FILE, "w") as f:
                json.dump(all_p, f, indent=4)
            print(f"[PERSISTENCE] Pipeline '{name}' deleted.")
            self.update_pipeline_menu()
            dpg.configure_item("delete_pipeline_modal", show=False)
