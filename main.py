#!/usr/bin/env python3

import os
from random import choice
from time import sleep

import vizdoom as vzd


if __name__ == "__main__":
    # Create DoomGame instance.
    game = vzd.DoomGame()
    
    # load_config
    game.load_config("scenarios/basic.cfg")

    # Sets path to additional resources wad file which is basically your scenario wad.
    game.set_doom_scenario_path(os.path.join(vzd.scenarios_path, "basic.wad"))
    # game.set_doom_scenario_path(os.path.join(vzd.scenarios_path, "simpler_basic.wad"))


    game.set_automap_buffer_enabled(True)

    # Sets config env. (override the parameter values set by the config file).
    # game.set_doom_map("map01")
    # game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
    # game.set_screen_format(vzd.ScreenFormat.RGB24)
    # game.set_depth_buffer_enabled(True)
    # game.set_labels_buffer_enabled(True)
    # game.set_automap_buffer_enabled(True)
    # game.set_objects_info_enabled(True)
    # game.set_sectors_info_enabled(True)
    # game.set_render_hud(False)
    # game.set_render_minimal_hud(False)  # If hud is enabled
    # game.set_render_crosshair(False)
    # game.set_render_weapon(True)
    # game.set_render_decals(False)  # Bullet holes and blood on the walls
    # game.set_render_particles(False)
    # game.set_render_effects_sprites(False)  # Like smoke and blood
    # game.set_render_messages(False)  # In-game text messages
    # game.set_render_corpses(False)
    # game.set_render_screen_flashes(
    #     True
    # )  # Effect upon taking damage or picking up items
    # game.set_episode_timeout(200)
    # game.set_episode_start_time(10)
    # game.set_window_visible(True)
    # game.set_sound_enabled(True)
    # game.set_audio_buffer_enabled(True)
    # game.set_console_enabled(True)


    # Adds buttons that will be allowed to use.
    # game.clear_available_buttons()
    game.set_available_buttons([
        vzd.Button.MOVE_LEFT, 
        vzd.Button.MOVE_RIGHT,
        vzd.Button.MOVE_FORWARD,
        vzd.Button.MOVE_BACKWARD, 
        vzd.Button.ATTACK
    ])
    print("Available buttons:", [b.name for b in game.get_available_buttons()])

    # Adds game variables that will be included in state.
    # game.clear_available_game_variables()
    game.set_available_game_variables([vzd.GameVariable.AMMO2])
    print("Available game variables:",[v.name for v in game.get_available_game_variables()])
    
    
    # Sets the living reward (for each move) to -1
    game.set_living_reward(-1)

    # Sets ViZDoom mode (PLAYER, ASYNC_PLAYER, SPECTATOR, ASYNC_SPECTATOR, PLAYER mode is default)
    game.set_mode(vzd.Mode.PLAYER)

    # Initialize the game. Further configuration won't take any effect from now on.
    game.init()

    # Define some actions. Each list entry corresponds to declared buttons (Identity matrix)
    actions = [[i == j for i in range(len(game.get_available_buttons()))] for j in range(len(game.get_available_buttons()))]
    print(actions)
    
    # Run this many episodes
    episodes = 10
    # Sets time that will pause the engine after each action (in seconds)
    sleep_time = 1.0 / vzd.DEFAULT_TICRATE  # = 0.028

    for i in range(episodes):
        print(f"Episode #{i + 1}")

        # Starts a new episode. It is not needed right after init() but it doesn't cost much. At least the loop is nicer.
        game.new_episode()

        while not game.is_episode_finished():

            # Gets the state
            state = game.get_state()
            assert state is not None

            # Which consists of:
            n = state.number
            vars = state.game_variables

            # Different buffers (screens, depth, labels, automap, audio)
            # Expect of screen buffer some may be None if not first enabled.
            screen_buf = state.screen_buffer
            depth_buf = state.depth_buffer
            labels_buf = state.labels_buffer
            automap_buf = state.automap_buffer
            audio_buf = state.audio_buffer

            # List of labeled objects visible in the frame, may be None if not first enabled.
            labels = state.labels

            # List of all objects (enemies, pickups, etc.) present in the current episode, may be None if not first enabled
            objects = state.objects

            # List of all sectors (map geometry), may be None if not first enabled.
            sectors = state.sectors

            # Games variables can be also accessed via
            # (including the ones that were not added as available to a game state):
            # game.get_game_variable(GameVariable.AMMO2)

            # Makes an action (here random one) and returns a reward.
            r = game.make_action(choice(actions))

            # Makes a "prolonged" action and skip frames:
            # skiprate = 4
            # r = game.make_action(choice(actions), skiprate)

            # The same could be achieved with:
            # game.set_action(choice(actions))
            # game.advance_action(skiprate)
            # r = game.get_last_reward()

            # Prints state's game variables and reward.
            print(f"State #{n} | Game variables: {vars} | Reward: {r}")

            if sleep_time > 0:
                sleep(sleep_time)

        # Check how the episode went.
        print("Episode finished.")
        print("Total reward:", game.get_total_reward())
        print("************************")
        print("************************")



    # It will be done automatically anyway but sometimes you need to do it in the middle of the program...
    game.close()



