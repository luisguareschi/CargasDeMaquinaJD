import os

packages_folder = os.path.dirname(__file__)
directory_folder = os.path.dirname(packages_folder)
resources_folder = r'\\fcefactory1\PROGRAMAS_DE_PRODUCCION\6.Planificacion\Cargas de Maquina JD\resources'
images_folder = os.path.join(resources_folder, 'images')
downloads_folder = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
