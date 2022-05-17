#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application.
GUI and event loop.

Adam Ferencz
VUT FIT 2022
"""

from __future__ import print_function

import pygame_gui

from pygame.locals import *
from pygame_gui.core.utility import create_resource_path
from pygame_gui.windows import UIFileDialog

from AirSimDroneModel import *
from Corrector import *
from Logger import *
from Path import *

if __name__ == "__main__":
    enable_assistant = False
    enable_video = False
    VISUALISER = False

    pygame.init()
    pygame.joystick.init()

    # GUI elements.
    manager = pygame_gui.UIManager((800, 800), 'data/themes/theme.json')
    save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 50), (-1, -1)),
                                               text='Save path',
                                               manager=manager)
    load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 90), (-1, -1)),
                                               text='Load path',
                                               manager=manager)
    delete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 130), (-1, -1)),
                                               text='Delete path',
                                               manager=manager)
    assistant_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 170), (-1, -1)),
                                                    text='Assistant OFF',
                                                    manager=manager)
    log_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 210), (-1, -1)),
                                              text='Logging OFF',
                                              manager=manager)
    file_dialog = None

    # Connect Xbox controller.
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        print(joystick.get_name())

    # PyGame setup.
    dis_width = 800
    dis_height = 800
    zoom = 0.04
    dis = pygame.display.set_mode((dis_width, dis_width))
    pygame.display.set_caption('Pygame visualization')
    app_over = False
    clock = pygame.time.Clock()

    joystick = [0, 0, 0, 0]

    # Define center of the word in simulator.
    center_latlon = [47.6434827, 15.5918024]

    # Encapsulates transformations.
    transformer = Transformer(dis_width, dis_height, zoom, center_latlon)

    # Create and connect drone.
    drone = AirSimDroneModel(dis, transformer)
    drone.connect()

    # Update center of transformations by drones home position.
    transformer = drone.transform
    center_latlon = transformer.center_latlon

    # Init corrector, path and logger.
    corrector = Corrector(dis, transformer)
    path = Path(transformer)
    logger = Logger(corrector.free_range, corrector.warning_range)


    def switch_logging():
        """ Enables and disables logging. Saves dhe logs."""
        if logger.is_logging is True:
            logger.save(drone)
            logger.is_logging = False
            log_button.set_text("Logging OFF")
        else:
            logger.is_logging = True
            log_button.set_text("Logging ON")
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
            drone.log_folder = "logs/" + dt_string
            os.mkdir(drone.log_folder)
            os.mkdir(drone.log_folder + "/photos")

    getTicksLastFrame = 0

    while not app_over:
        time_delta = clock.tick(60) / 1000.0
        dis.fill((255, 255, 255))

        # Get mouse position.
        mouseX, mouseY = pygame.mouse.get_pos()
        mouse = [mouseX, mouseY]

        # Dispatch all events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    app_over = True
                elif event.key == pygame.K_SPACE:
                    drone.land()
                    if TELLO:
                        print('landing')
                        drone.me.land()
                        drone.in_air = False
                elif event.key == pygame.K_e:
                    drone.takeoff()
                    if TELLO:
                        print('takeoff')
                        drone.me.takeoff()
                        drone.in_air = True

                elif event.key == pygame.K_p:
                    zoom *= 1.2
                    transformer = Transformer(dis_width, dis_height, zoom, center_latlon)
                    drone.transform = transformer
                    corrector.transform = transformer
                    path.transformer = transformer
                    for wp in path.waypoints:
                        wp.transformer = transformer
                    carrot.transform = transformer
                elif event.key == pygame.K_m:
                    zoom *= 0.8
                    transformer = Transformer(dis_width, dis_height, zoom, center_latlon)
                    drone.transform = transformer
                    corrector.transform = transformer
                    path.transformer = transformer
                    for wp in path.waypoints:
                        wp.transformer = transformer
                    carrot.transform = transformer

            if event.type == JOYBUTTONDOWN:
                if event.button == 0:  # A
                    enable_assistant = not enable_assistant
                    if enable_assistant:
                        assistant_button.set_text("Assistant ON")
                    else:
                        assistant_button.set_text("Assistant OFF")
                if event.button == 1:  # B
                    enable_assistant = False
                    assistant_button.set_text("Assistant OFF")
                    drone.land()
                if event.button == 2:  # X
                    print("X")
                    VISUALISER = not VISUALISER

                    print("corrector.is_pid")
                if event.button == 3:  # Y
                    drone.takeoff()

                if event.button == 4:  # L front
                    drone.take_photo()

                if event.button == 5:  # R Front
                    drone.take_photo()

                if event.button == 6:  # OO
                    enable_video = not enable_video

                if event.button == 7:  # ==
                    switch_logging()

            if event.type == JOYAXISMOTION:
                if event.axis < 4:
                    joystick[event.axis] = event.value

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Add new waypoints.
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    visual_yx = (mouseX, mouseY)
                    display_size = (dis_width, dis_height)

                    path.add_waypoint_by_pixel(mouse)

                if path.selected_wp is not None:
                    path.selected_wp_locked = True

            if event.type == pygame.MOUSEBUTTONUP:
                path.selected_wp_locked = False

            elif event.type == pygame.MOUSEWHEEL:
                # Change waypoint height.
                if path.selected_wp is not None:
                    path.selected_wp.metres_z += event.y/10
                else:
                    path.actual_height += event.y/10

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == save_button:
                    path.save_path_json()

                if event.ui_element == load_button:
                    file_dialog = UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                               manager,
                                               window_title='Load Path Json...',
                                               initial_file_path='missions/',
                                               allow_picking_directories=False,
                                               allow_existing_files_only=True)
                    load_button.disable()

                if event.ui_element == delete_button:
                    path.delete_path()

                if event.ui_element == assistant_button:
                    enable_assistant = not enable_assistant
                    if enable_assistant:
                        assistant_button.set_text("Assistant ON")
                    else:
                        assistant_button.set_text("Assistant OFF")

                if event.ui_element == log_button:
                    switch_logging()

            # Load path from file.
            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                try:
                    image_path = create_resource_path(event.text)
                    f = open(image_path, "r")
                    data = json.loads(f.read())
                    path.delete_path()
                    width = data[0]["transformer.width"]
                    height = data[0]["transformer.height"]
                    zoom = data[0]["transformer.zoom"]
                    center_latlon = data[0]["transformer.center_latlon"]
                    transformer = Transformer(width, height, zoom, center_latlon)
                    path.load_path_json(data)
                    drone.transform = transformer
                    corrector.transform = transformer
                    path.transformer = transformer
                    carrot.transform = transformer


                except pygame.error:
                    pass

            if (event.type == pygame_gui.UI_WINDOW_CLOSE
                and event.ui_element == file_dialog):
                load_button.enable()
                file_dialog = None

            manager.process_events(event)

        manager.update(time_delta)
        text(dis, str(int(clock.get_fps())) + ' FPS', 30, [200, 700])
        path.update(mouse)
        path.display(surface=dis)

        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0  # deltaTime in seconds.
        getTicksLastFrame = t

        """ UPDATE PHASE """
        drone.update()

        # Draws squares.
        visualise_metrics(dis, dis_width, dis_height, zoom)

        visualise_joystick(dis, [600, 700], 50, joystick)

        # Get pilot command.
        left_right, fwd_back, up_down, yaw = drone.map_joystick_to_speed(joystick)

        """ ROTATION """
        left_right, fwd_back = drone.rotate_command_by_yaw([left_right, fwd_back])
        original_command = [left_right, fwd_back, up_down, yaw]

        """ CORRECTOR PHASE """

        command_speed = np.array([left_right, fwd_back, up_down])

        velocity = drone.speed
        location = drone.position

        # Compute block.
        if len(path.waypoints) > 1:
            save_command_speed = corrector.adjust_command(location, velocity, command_speed, path)
            save_command_speed = np.array([save_command_speed[0], save_command_speed[1], save_command_speed[2]])
        else:
            save_command_speed = command_speed

        """ SEND COMMAND """
        if not enable_assistant:
            left_right, fwd_back, up_down, yaw = original_command
        else:
            _, _, _, yaw = original_command
            left_right, fwd_back, up_down = map_vec3_to_int_list(save_command_speed)

        command = left_right, fwd_back, up_down, yaw

        text(dis, "original_command :" + str(trunc(np.array(original_command))), 25, (450, 175))
        text(dis, "safe_command :" + str(trunc(np.array(command))), 25, (450, 200))

        # Send command to drone.
        drone.move(command, deltaTime)

        drone.display()

        # Displays path in AirSim.
        if VISUALISER:
            drone.plot_to_airsim(path, mouse)

        # Logging.
        logger.log(drone, corrector)

        # Video to the GUI.
        if enable_video:
            drone.display_video()

        clock.tick(60)

        manager.draw_ui(dis)
        pygame.display.update()


    pygame.quit()
    quit()
    sys.exit()
