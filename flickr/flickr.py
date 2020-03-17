"""Retrieve and Parse Biodiversity Heritage Library Images

Usage:
    bhl-images get-info [--filepath=<filepath>]
    bhl-images download <photolist> [--output-dir=<output_dir>]

"""


import requests
from requests_oauthlib import OAuth1Session
import xml.etree.ElementTree as ET
import gzip
import os
from dotenv import load_dotenv
import json
import pathlib
import docopt

load_dotenv()

oauth = OAuth1Session(
    os.getenv("FLICKR_KEY"),
    client_secret = os.getenv("FLICKR_SECRET"),
    resource_owner_key = os.getenv("FLICKR_RO_KEY"),
    resource_owner_secret = os.getenv("FLICKR_RO_SECRET")
)


def get_photo_info(filepath):
    lpage = True
    page = 1
    photolist = []
    while lpage:
        r = oauth.get(
            "https://www.flickr.com/services/rest/?method=flickr.people.getPhotos&user_id=biodivlibrary&per_page=500&page={page}" \
                .format(page=page)
        )

        root = ET.fromstring(r.content)
        pchild = [child for child in root][0]
        pages = int(pchild.attrib.get('pages'))

        for child in pchild:
            photolist.append(child.attrib)

        if page >= pages: lpage = False
        page += 1

    with gzip.open(filepath, "wt") as file:
        json.dump(photolist, file)

    return photolist


def download_photos(photolist, output_dir = "images"):

    if os.path.isfile(photolist):
        if '.gz' in pathlib.Path(photolist).suffixes:
            try:
                with gzip.open(photolist, "rt") as file:
                    photolist = json.load(file)
            except OSError:
                with open(photolist, "rt") as file:
                    photolist = json.load(file)
    else:
        json.loads(photolist)

    imgdir_list = os.listdir(output_dir)
    for photoatt in photolist:
        photocode = "{photo_id}_{secret}" \
            .format(photo_id=photoatt.get('id'),
                    secret=photoatt.get('secret'))

        if any(photocode in i for i in imgdir_list):
            continue

        photo_dl = "https://farm{farm}.staticflickr.com/{server}/{id}_{secret}_k.jpg" \
            .format(**photoatt)

        try:
            resp = requests.get(photo_dl)
        except:
            continue

        with gzip.open('{output_dir}/{photocode}.jpg.gz'.format(output_dir=output_dir,
                                                                photocode=photocode), 'wb') \
                as file:
            file.write(requests.get(photo_dl).content)


def main():
    args = docopt.docopt(__doc__)
    print(args)
    if args['get-info']:
        filepath = args['--filepath'] or "photo_info.json.gz"
        get_photo_info(filepath=filepath)
    if args['download']:
        photolist = args['<photolist>']
        output_dir = args['--output-dir'] or "images"
        download_photos(photolist=photolist, output_dir=output_dir)


if __name__ == "__main__":
    main()
