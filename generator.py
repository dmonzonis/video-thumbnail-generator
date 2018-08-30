import argparse
import cv2
import datetime
from PIL import Image


def cv2_to_img(array):
    """Convert an image in array format for cv2 to a Pillow image and return it."""
    img = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)


def time_to_text(time):
    """Convert the input time in ms to a string with the hours, minutes and seconds."""
    seconds = int(time // 1000)
    return str(datetime.timedelta(0, seconds))


def extract_frame_images(path, image_count=10):
    vc = cv2.VideoCapture(path)
    frame = 0  # Initial frame
    count = 0
    images = []

    # Get total number of frames
    total = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
    step = total // image_count

    while vc.isOpened() and count < image_count:
        vc.set(cv2.CAP_PROP_POS_FRAMES, frame)
        # Get the timestamp in ms
        timestamp = time_to_text(vc.get(cv2.CAP_PROP_POS_MSEC))
        success, image = vc.read()
        if not success:
            break
        images.append((cv2_to_img(image), timestamp))
        frame += step
        count += 1

    vc.release()
    return images


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help="video file to parse")

    args = parser.parse_args()

    images = extract_frame_images(args.path)
    print(images)


if __name__ == "__main__":
    main()
