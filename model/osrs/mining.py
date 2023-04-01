import time
from typing import List
import utilities.api.item_ids as ids
import utilities.color as clr
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.geometry import Rectangle, RuneLiteObject


class OSRS_Mining(OSRSBot):
    def __init__(self):
        title = "Mining"
        description = (
            "This bot power-mines rocks. Equip a pickaxe, place your character between some rocks and mark "
            + "(Shift + Right-Click) the ones you want to mine."
        )
        super().__init__(bot_title=title, description=description)
        self.running_time = 360
        self.logout_on_friends = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_dropdown_option("logout_on_friends", "Logout when friends are nearby?", ["Yes", "No"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "logout_on_friends":
                self.logout_on_friends = options[option] == "Yes"
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f'Bot will {"" if self.logout_on_friends else "not"} logout when friends are nearby.')
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality
        # SETUP
        # api
        api = MorgHTTPSocket()

        # Constants
        self.items_to_drop = [
            ids.IRON_ORE,
            ids.UNCUT_SAPPHIRE,
            ids.UNCUT_EMERALD,
            ids.UNCUT_RUBY,
            ids.UNCUT_DIAMOND,
        ]

        # Variables
        self.mined = 0
        failed_searches = 0

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        # Drop all dropable items
        self.drop(api.get_inv_item_indices(self.items_to_drop))

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Check to drop inventory
            self.__drop_some(api) #why are we dropping every loop?

            # Check to logout
            if self.logout_on_friends and self.friends_nearby():
                self.__logout("Friends nearby. Logging out.")

            # Get the rocks
            iron_rocks: List[RuneLiteObject] = self.get_all_tagged_in_rect(
                self.win.game_view,
                clr.PINK,
            )
            if not rocks:
                failed_searches += 1
                self.__drop_all(api)
                if failed_searches > 5:
                    self.__logout("Failed to find a rock to mine. Logging out.")
                time.sleep(1)
                continue
            failed_searches = 0

            # Whack the rock
            rocks = sorted(iron_rocks, key=RuneLiteObject.distance_from_rect_center) #sorting list of rocks by distance from player
            rock = rocks[0]
            if not self.mouseover_text(contains="Iron"):
                self.mouse.move_to(
                    rock.random_point(),
                    mouseSpeed="fastest",
                )
            if not self.mouse.click(check_red_click=True):
                self.mouse.click()
            if iron_rocks:
                self.mouse.move_to(rock.random_point(), mouseSpeed="fastest")
            if not api.get_is_player_idle():
                api.wait_til_gained_xp(skill="Mining", timeout=3)

            self.log_msg(f"Rocks mined: {self.mined}")

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg: str):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def __drop_some(self, api: MorgHTTPSocket) -> None:
        "drop some ore/gems using StatusSocket API"
        slots = api.get_inv_item_indices(self.items_to_drop)
        if len(slots) < 3:
            return
        if not api.get_is_player_idle():
            api.wait_til_gained_xp(skill="Mining", timeout=2)
        slots = slots[:3]
        self.mined += 3
        self.drop(slots)

    def __drop_all(self, api: MorgHTTPSocket) -> None:
        "drop some ore/gems using StatusSocket API"
        slots = api.get_inv_item_indices(self.items_to_drop)
        self.drop(slots)
