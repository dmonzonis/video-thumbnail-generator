import argparse
import cv2
import datetime
from math import ceil
import os
from PIL import Image, ImageDraw


def cv2_to_img(array):
    """Convert an image in array format for cv2 to a Pillow image and return it."""
    img = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)


def time_to_text(time):
    """Convert the input time in ms to a string with the hours, minutes and seconds."""
    seconds = int(time // 1000)
    return str(datetime.timedelta(0, seconds))


def get_video_duration(video_capture):
    """Get the total video duration in milliseconds."""
    frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    return 1000 * (frame_count // fps)


def get_filename(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0]


def generate_thumbnail(img, timestamp, thumbnail_size=256, text_color=(255, 255, 255),
                       text_position=(0, 0)):
    """Resizes the image to thumbnail size and draws the timestamp on top of the image."""
    # Even if the image is not square, the size of the longest dimension will be reduced to
    # the given thumbnail size, and the other will be changed so as to maintain the ratio
    size = (thumbnail_size, thumbnail_size)
    img.thumbnail(size)
    # Draw timestamp
    draw = ImageDraw.Draw(img)
    draw.text(text_position, timestamp, fill=text_color)
    return img


def extract_thumbnails_from_video(path, image_count, quiet=False):
    """Opens the video in the path and returns a list of thumbnails from some of its frames.

    The frames are equally separated, using the total video time and the image
    count to compute the time between each frame.
    """
    vc = cv2.VideoCapture(path)
    frame = 0  # Initial frame
    count = 1
    images = []

    # Get total number of frames
    total = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
    step = total // image_count

    while vc.isOpened() and count <= image_count:
        vc.set(cv2.CAP_PROP_POS_FRAMES, frame)
        # Get the timestamp in ms
        timestamp = time_to_text(vc.get(cv2.CAP_PROP_POS_MSEC))
        success, image = vc.read()
        if not success:
            break

        # Give some output
        if not quiet:
            print(f"Generating thumbnail {count} of {image_count} at frame {frame}")

        # Convert to image and add timestamp
        img = cv2_to_img(image)
        generate_thumbnail(img, timestamp)
        images.append(img)

        # Update variables
        frame += step
        count += 1

    vc.release()
    if not images:
        print("Error: File couldn't be processed")
        exit(1)
    return images


def create_thumbnail_grid(thumbnails, row_size, quiet=False):
    """Create an image consisting of all the thumbnails in order, in a grid."""
    if not quiet:
        print("Compositing the final image")
    # Get the size of one of the thumbnails as reference
    thumbnail_width, thumbnail_height = thumbnails[0].size
    column_count = ceil(len(thumbnails) / row_size)
    img = Image.new('RGB', (thumbnail_width * row_size, thumbnail_height * column_count))
    # TODO: Add video metadata on top of the image
    # Fill the grid with the thumbnails
    for i in range(len(thumbnails)):
        # Compute the top-left corner position where the next thumbnail has to go
        row = i % row_size
        column = i // row_size
        position = (thumbnail_width * row, thumbnail_height * column)
        img.paste(thumbnails[i], position)
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help="video file to parse")
    parser.add_argument('-c', '--count', type=int, default=32,
                        help="thumbnail count")
    parser.add_argument('-r', '--row-size', type=int, default=4,
                        help="number of columns per row")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="run in quiet mode")
    parser.add_argument('-o', '--output-name', type=str, default='',
                        help="specify output image filename")

    args = parser.parse_args()

    thumbnails = extract_thumbnails_from_video(args.path, image_count=args.count,
                                               quiet=args.quiet)
    composite = create_thumbnail_grid(thumbnails, args.row_size, args.quiet)

    if not args.output_name:
        # Name the file exactly like the original, but with jpg format
        filename = get_filename(args.path) + ".jpg"
    else:
        filename = args.output_name + ".jpg"

    composite.save(filename)


if __name__ == "__main__":
    main()
