import dearpygui.dearpygui as dpg
from PIL import Image
import os
import time
from core import MAX_DISPLAY_WIDTH

class ImageUtilsMixin:
    def _update_texture_from_file(self, path, tex_id, widget_tag):
        if not path or path == "." or path == "..":
            return False
            
        if not os.path.exists(path) or os.path.isdir(path):
            print(f"[IMAGE_UTILS] Invalid path or directory: {path}")
            return False
            
        try:
            img = Image.open(path).convert("RGBA")
            if widget_tag == "input_image_widget":
                self.input_image = img
            return self._update_texture_from_image(img, tex_id, widget_tag)
        except Exception as e:
            print(f"[IMAGE_UTILS] Error loading {path}: {e}")
            return False

    def _update_texture_from_image(self, img, tex_id, widget_tag):
        try:
            orig_w, orig_h = img.size
            display_w = min(orig_w, MAX_DISPLAY_WIDTH)
            ratio = display_w / float(orig_w)
            display_h = int(orig_h * ratio)
            
            img_resized = img.resize((display_w, display_h), Image.Resampling.LANCZOS)
            
            raw_data = img_resized.tobytes()
            data = []
            for b in raw_data:
                data.append(float(b) / 255.0)
            
            new_tex_tag = f"{tex_id}_{int(time.time() * 1000)}"
            dpg.add_dynamic_texture(
                width=display_w, height=display_h, default_value=data, 
                tag=new_tex_tag, parent="tex_registry"
            )
            
            if dpg.does_item_exist(widget_tag):
                dpg.configure_item(
                    widget_tag, texture_tag=new_tex_tag, 
                    width=display_w, height=display_h
                )
            
            # Sync button width with image width if updating the input image
            if widget_tag == "input_image_widget" and dpg.does_item_exist("select_image_button"):
                dpg.configure_item("select_image_button", width=display_w)
            
            old_tex = self.current_textures.get(tex_id)
            if old_tex and dpg.does_item_exist(old_tex):
                dpg.delete_item(old_tex)
            
            self.current_textures[tex_id] = new_tex_tag
            return True
        except Exception as e:
            print(f"[IMAGE_UTILS] Update failed: {e}")
            return False
