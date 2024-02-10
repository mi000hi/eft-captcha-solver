from utils import network

import cv2
import pandas as pd
import numpy as np
import requests
import shutil
import os

from icecream import ic
from tqdm.auto import tqdm

class EFT_Items:


    def __init__(self, grid_icons_directory:str, verbose:bool=False):

        self.verbose = verbose
        self.GRID_ICONS_DIRECTORY = grid_icons_directory
        self.GRID_ICON_FILENAME_ENDING = '-grid-image.jpg'

        self.API_URL = 'https://api.tarkov.dev/graphql'

        self.all_items_df = self.get_all_item_prices()
        self.icons = self.load_icons_from_disk(verbose=self.verbose)

    def get_all_item_prices(self):
        query_all_items_prices = """
        {
            items {
                shortName
                name
                id
                width
                height
                avg24hPrice
                changeLast48hPercent
                basePrice
                sellFor {
                    price
                    source
                }
            }
        }
        """
        result = network.run_json_query(self.API_URL, query_all_items_prices)
        all_items = result['data']['items']

        # pack data into pandas dataframe
        all_items_df = pd.DataFrame(columns=['name', 'short_name', 'id', 'width', 'height', 'flea_avg48', 'flea_ch48percent', 'prapor', 'therapist', 'fence', 'skier', 'peacekeeper', 'mechanic', 'ragman', 'jaeger', 'basePrice'], index=range(len(all_items)))
        for index in range(len(all_items)):
            entry = all_items[index]
            all_items_df.at[index, 'name'] = entry.get('name')
            all_items_df.at[index, 'short_name'] = entry.get('shortName')
            all_items_df.at[index, 'id'] = entry.get('id')
            all_items_df.at[index, 'width'] = entry.get('width')
            all_items_df.at[index, 'height'] = entry.get('height')
            all_items_df.at[index, 'flea_avg48'] = entry.get('avg24hPrice')
            all_items_df.at[index, 'flea_ch48percent'] = entry.get('changeLast48hPercent')
            all_items_df.at[index, 'basePrice'] = entry.get('basePrice')

            # iterate over all traders that can buy the item
            for offer in entry.get('sellFor'):
                trader = offer.get('source')
                price  = offer.get('price')
                all_items_df.at[index, trader] = price

        return all_items_df

    def load_icons_from_disk(self, verbose=False):
        icons = []
        for index,item in self.all_items_df.iterrows():
            filename = self.GRID_ICONS_DIRECTORY + item['id'] + self.GRID_ICON_FILENAME_ENDING
            if not os.path.exists(filename):
                icons.append(None)
                if verbose:
                    print(f"File {filename} does not exist.")
            else:
                # width_in_slots = item.loc['width']
                # height_in_slots = item.loc['height']
                icon_bgr = cv2.imread(filename)
                icon_rgb = cv2.cvtColor(icon_bgr, cv2.COLOR_BGR2RGB)
                # icon = scale_image(icon, width=(int) (width_in_slots*slot_size)
                #         , height=(int) (height_in_slots*slot_size))
                icons.append(icon_rgb)

        return icons
    
    def download_grid_icons(self, delete_old_images:bool=True, verbose:bool=True):
        get_all_items = """
        {
            items {
                id
                gridImageLink
            }
        }
        """
        query_result = network.run_json_query(self.API_URL, get_all_items)['data']['items']

        # create directory
        if not os.path.exists(self.GRID_ICONS_DIRECTORY):
            os.makedirs(self.GRID_ICONS_DIRECTORY)

        # delete old images
        if delete_old_images:
            old_images = os.listdir(self.GRID_ICONS_DIRECTORY)
            for file in old_images:
                os.remove(f"{self.GRID_ICONS_DIRECTORY}/{file}")

        # Set up the image URL and filename
        for item in tqdm(query_result):
            item_id = item['id']
            image_url = item['gridImageLink']
            filename = image_url.split("/")[-1]
            filename_jpg = f"{os.path.splitext(filename)[0]}.jpg"

            # Open the url image, set stream to True, this will return the stream content.
            r = requests.get(image_url, stream = True)

            STATUS_SUCCESS = 200
            if r.status_code != STATUS_SUCCESS:
                print('Image Couldn\'t be retreived')

            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            filepath = f"{self.GRID_ICONS_DIRECTORY}/{filename_jpg}"
            with open(filepath,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                
    def get_image_from_item_name(self, item_name:str):
        item_df_index = self.all_items_df[self.all_items_df['name'] == item_name].index[0]
        icon_image = self.icons[item_df_index]
        return icon_image

    def get(self, identifier:str, key):
        matching_items = self.all_items_df[self.all_items_df[identifier] == key]
        if len(matching_items) == 0:
            print(f"ERROR: Item not found. Searched under '{identifier}' with key '{key}'.")
            return None
        if len(matching_items) > 1:
            print(f"WARNING: Multiple matching items found:\n"
                  f"         {matching_items}"
                  f"         Using first item.")
        item_entry = matching_items.iloc[0]
        return item_entry
