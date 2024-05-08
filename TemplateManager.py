import os
from PyQt6.QtCore import pyqtSignal, QObject

class FileManager(QObject):
    templateChanged = pyqtSignal(str)  # define signal for template change
    partSelected = pyqtSignal(str, str)  # define signal for part change

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def get_template_names(self):
        template_names = []
        if os.path.exists(self.folder_path) and os.path.isdir(self.folder_path):
            all_templates = os.listdir(self.folder_path)
            template_folders = [
                file_name 
                for file_name in all_templates 
                if os.path.isdir(os.path.join(self.folder_path, file_name))]
            template_names = sorted(template_folders)
        return template_names

    def get_part_names_for_template(self, template_name):
        part_names = []
        template_folder_path = os.path.join(self.folder_path, template_name)
        all_assets =os.listdir(template_folder_path)
        if os.path.exists(template_folder_path) and os.path.isdir(template_folder_path):
            part_folders = [
                file_name for file_name in all_assets 
                if os.path.isdir(os.path.join(template_folder_path, file_name))]
            part_names = sorted(part_folders)
        return part_names
    
    def get_styles_for_part(self, template_name, part_name):
        styles = [] 
        part_folder_path = os.path.join(self.folder_path, template_name, part_name)
        if os.path.exists(part_folder_path) and os.path.isdir(part_folder_path):
            styles = [ f for f in os.listdir(part_folder_path) if os.path.isfile(os.path.join(part_folder_path, f))] 
        styles.insert(0,"None")
        return styles
    
    def remove_dosign(self, template_name, part_name):
        styles = self.get_styles_for_part(template_name, part_name)
        styles_no_dosign = [style for style in styles if "$" not in style]
        return styles_no_dosign
                

    def get_paths_for_style(self, template_name, part_name):
        paths = {}
        part_folder_path = os.path.join(self.folder_path, template_name, part_name)
        if os.path.exists(part_folder_path) and os.path.isdir(part_folder_path):
            styles = self.get_styles_for_part(template_name, part_name)
            for style in styles:
                if style == "None":
                    paths[style] = ["None"]
                elif style[-1] == "$":
                    real_style = style[:-1]
                    paths[real_style].append(os.fsencode(os.path.join(part_folder_path, style)))
                else:
                    paths[style] = [os.fsencode(os.path.join(part_folder_path, style))] 
        return paths