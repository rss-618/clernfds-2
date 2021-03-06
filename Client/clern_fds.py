"""
clern_fds.py
Author: Ryan Schildknecht

SRS cross-reference:
Functional Requirement 3.1.1 - The client software must capture video from a user feed.
Functional Requirement 3.1.3 - The client software must communicate to server software.
Non-Functional Requirement 3.2.1 - The CLERN Client shall send video frames to the FDS Server, at most, once per second.
Non-Functional Requirement 3.2.3 - The FDS Client shall be configurable to change video feed source.
SDD cross-reference: Implements Section 3.2 (The CLERN Client)

"""

import os
import shutil
import time
import cv2
from archive import Archive
from tcp_client import TCPClient
from tkinter_gui import CLERNFDS
from concurrent.futures import ThreadPoolExecutor


def main():
    # Ensure proper directories exist
    if not (os.path.exists('Frames')):
        os.mkdir('Frames')
    # Start The ClientGUI
    gui = CLERNFDS()
    # Init the Client being used to submit files
    client = TCPClient()
    # Get the frame deliverance loop started
    t = ThreadPoolExecutor()
    t.submit(frame_processes, gui, client)
    # Run the mainloop

    gui.loop()
    t.shutdown()
    clear_frames()
    print("Program Closed")


def clear_frames() -> None:
    """ Clear all frames in the ./Frames folder"""
    if os.path.exists("./Frames"):
        for filename in os.listdir("./Frames"):
            file_path = os.path.join("./Frames", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def frame_processes(gui, frame_client) -> None:
    """
    This loop only runs when the gui is running, gets the camera index from the gui configuration
    SRS:
    F.R. 3.1.1
    F.R. 3.1.3
    N.F.R 3.2.1
    N.F.R 3.2.3
    :param gui: The Client Interface
    :param frame_client: The TCP_Client object to deliver files to the server
    :return:
    """
    while not gui.is_running:
        pass
    # Frame Deliverance
    while gui.is_running:
        print("New Index")
        index = int(gui.selected_index)

        cap = cv2.VideoCapture(index)
        # doesn't work on a webcam
        cap.set(cv2.CAP_PROP_FPS, 30)

        frame_count = 0
        archive_count = 0
        frames = []
        # open the cap (throwaway values)
        ret, frame = cap.read()
        cv2.imwrite("mask.jpg", frame)
        frame_client.send_file("mask.jpg")
        it = time.time()
        while index == int(gui.selected_index) and cap.isOpened() and gui.is_running:
            ret, frame = cap.read()
            frame_count += 1
            if frame_count % 3 == 0:
                file_name = 'Frames/' + str(time.time()) + '.jpg'
                cv2.imwrite(file_name, frame)
                frames.append(file_name)
                print(f'{file_name} saved')
            if frame_count == 30:
                archive_count += 1
                deliver(frames, archive_count, frame_client)
                frames.clear()
                if archive_count == 10:
                    archive_count = 0
                frame_count = 0
                print(f"{time.time() - it} seconds to collect and deliver archive.")
                it = time.time()
        cap.release()
        clear_frames()


def deliver(frames, archive_num, client) -> None:
    """
    Creates an Archive of Collected Frames.
    Sends that Archive
    :param frames: Collection of frames being passed
    :param archive_num: The number of the archive being passed (1-10)
    :param client: The CLERN FDS client
    :return:
    """
    img_zip = Archive(str(archive_num) + ".zip")
    file_name = img_zip.file_name
    for frame in frames:
        img_zip.add(frame)
        print(f"{frame} added")
        # deleting files once added to zip
        if os.path.exists(frame):
            os.remove(frame)
        else:
            print(f"{frame} does not exist")
    # sending frames to server
    img_zip.close()
    client.send_file(img_zip.file_name)
    os.remove(file_name)


if __name__ == "__main__":
    main()
