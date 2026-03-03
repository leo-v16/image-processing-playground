import dearpygui.dearpygui as dpg
from core import WINDOW_WIDTH, WINDOW_HEIGHT
from image_utils import ImageUtilsMixin
from engine import EngineMixin
from persistence import PersistenceMixin
from node_manager import NodeManagerMixin
from ui_manager import UIMixin

class ImageNodeApp(ImageUtilsMixin, EngineMixin, PersistenceMixin, NodeManagerMixin, UIMixin):
    def __init__(self):
        dpg.create_context()
        
        # Core State
        self.current_textures = {"input_tex": None, "output_tex": None}
        self.input_image = None 
        self.output_image = None 
        self.node_params = {} 
        
        # 1. Texture Registry
        dpg.add_texture_registry(tag="tex_registry")
        dpg.add_static_texture(
            width=1, height=1, default_value=[0, 0, 0, 1], 
            tag="blank_tex", parent="tex_registry"
        )
            
        # 2. Setup UI Components
        self.setup_ui()
        self.update_pipeline_menu()
        
        # 3. Load Initial Demo Images
        self._update_texture_from_file("images/sky.png", "input_tex", "input_image_widget")
        self._update_texture_from_file("images/sky.png", "output_tex", "output_image_widget")
        
        # 4. Viewport Configuration - Updated Title
        dpg.create_viewport(
            title="IIP(Image Processing Playground)", 
            width=WINDOW_WIDTH, height=WINDOW_HEIGHT, 
            resizable=False
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def run(self):
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = ImageNodeApp()
    app.run()
