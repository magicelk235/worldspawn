def worldspawn():
    import pygame,gui,server,client,default
    pygame.init()
    pygame.display.set_mode((800, 400), pygame.SCALED | pygame.RESIZABLE)
    camera_group = gui.CameraGroup()
    host_or_join = gui.game_type_gui((2000,2000),camera_group)
    world_menu = None
    world_menu_selector = None
    pygame.display.set_caption("WorldSpawn")
    pygame.display.set_icon(pygame.image.load(default.resource_path("assets/gui/world_icon.png")))
    game_type = None
    main_gui = host_or_join
    path = None
    while path == None:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        camera_group.server_draw(main_gui, False, True)

        if game_type != None:
            path = world_menu_selector.updator(event_list, world_menu, camera_group)
        else:
            game_type = host_or_join.updator(event_list)
            if game_type != None:
                world_menu = gui.world_menu((2000, 2000), camera_group, game_type)
                world_menu_selector = gui.world_menu_selector((2000, 2000),"world", camera_group)
                main_gui = world_menu
                camera_group.remove(host_or_join)

        pygame.display.flip()
    del camera_group
    del host_or_join
    del world_menu
    del world_menu_selector

    pygame.quit()

    if game_type == "host":
        server.server(path).main()
    else:
        client.client(path).main()