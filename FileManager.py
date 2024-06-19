import os
import PySide6
from PySide6.QtCore import QObject
from Style import Style
from collections import defaultdict

class FileManager(QObject):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def update_folder_path(self, new_path):
        self.folder_path = new_path

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
                

    def create_object_for_style(self, template_name, part_name, s_style):
        new_styles = defaultdict(list)
        part_folder_path = os.path.join(self.folder_path, template_name, part_name)
        if os.path.exists(part_folder_path) and os.path.isdir(part_folder_path):
            styles = self.get_styles_for_part(template_name, part_name)
            do_style = s_style[:-4] + '$' + s_style[-4:]
            if s_style =='None':
                None_ident ='None'+ part_name
                new_style_none = Style(None, part_name, None_ident, real=0)
                new_styles[part_name].append(new_style_none)
            else:
                if do_style in styles:
                    path_do = os.fsencode(os.path.join(part_folder_path, do_style))
                    new_style_do = Style(path_do, part_name, do_style, real=2)
                    new_styles[part_name].append(new_style_do)
                path = os.fsencode(os.path.join(part_folder_path, s_style))
                new_style = Style(path, part_name, s_style, real=1)
                new_styles[part_name].append(new_style)
        return new_styles
