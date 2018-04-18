from PIL import Image
from core.utils import resize_image
import os

def main():
    splits = ['train', 'val']
    for split in splits:
        folder = './image/%s2014' %split
        resized_folder = './image/%s2014_resized/' %split
        if not os.path.exists(resized_folder):
            os.makedirs(resized_folder)
        print('Start resizing %s images.' %split)
        image_files = os.listdir(folder)
        num_images = len(image_files)
        for i, image_file in enumerate(image_files):
            with open(os.path.join(folder, image_file), 'r+b') as f:
                with Image.open(f) as image:
                    image = resize_image(image)
                    image.save(os.path.join(resized_folder, image_file), image.format)
            if i % 100 == 0:
                print( 'Resized images: %d/%d' %(i, num_images))          
            
if __name__ == '__main__':
    main()
