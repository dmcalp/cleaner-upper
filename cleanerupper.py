import os
import shutil
import reverse_geocoder as rg
import pycountry
from tkinter import Tk
from tkinter.filedialog import askdirectory
from exif import Image

Tk().withdraw()
image_dir_path = askdirectory(title="Select the folder containing the images you'd like to organise")
desired_location = askdirectory(title="Select the destination in which you would like to store the images")

images_dir = os.listdir(image_dir_path)
images = [im for im in images_dir if im.endswith('jpg')]

def dms_coords_to_dd_coords(coords, coords_ref):
    decimal_degrees = coords[0] + \
                      coords[1] / 60 + \
                      coords[2] / 3600
    
    if coords_ref == "S" or coords_ref == "W":
        decimal_degrees = -decimal_degrees    
    
    return decimal_degrees

def create_dir(dir_name):
  if not os.path.isdir(dir_name):
    os.mkdir(dir_name)
    print(f'Creating {dir_name} folder')

for i in range(len(images)):
  with open(os.path.join(image_dir_path, images[i]), "rb") as img_file:
    img = Image(img_file)

    if img.has_exif:
      
      if hasattr(img, 'datetime_original'):
        year = img.datetime_original.split(" ")[0].split(":")[0]      
        month = img.datetime_original.split(" ")[0].split(":")[1]
      else:
        print(f'Image {i+1} has no datetime information, skipping image.')
        continue
      
      if hasattr(img, 'gps_latitude'):  
        decimal_lat = dms_coords_to_dd_coords(img.gps_latitude, img.gps_latitude_ref)
        decimal_lng = dms_coords_to_dd_coords(img.gps_longitude, img.gps_longitude_ref)
        coords = (decimal_lat, decimal_lng)
        location = rg.search(coords, mode=1, verbose=False)[0]
        location['country'] = pycountry.countries.get(alpha_2=location['cc'])
        city = location['name']
        country = location['country'].name
      else:
        print(f'Image {i+1} has no location information, skipping image.')
        continue
      
      year_path = os.path.join(desired_location, str(year))
      create_dir(year_path)
      country_path = os.path.join(year_path, country)
      create_dir(country_path)
      city_path = os.path.join(country_path, city)
      create_dir(city_path)
    
    else:
      print()
      print(f'Image {i+1} does not contain any EXIF information.')
      continue

  shutil.move(os.path.join(image_dir_path, images[i]), os.path.join(city_path, images[i]))



  
