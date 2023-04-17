import time
import utilities.color as clr
from model.bot import BotStatus
from model.near_reality.nr_bot import NRBot
from utilities.api.status_socket import StatusSocket
import utilities.BackGroundScreenCap as bcp
import utilities.ScreenToClient  as stc
import utilities.RIOmouse as Mouse


class OSNRWoodcutting(NRBot):
    def __init__(self):
       
        bot_title = "Woodcutter"
        description = "This bot power-chops wood. Position your character near some trees, tag them, and press the play button."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False
        self.Client_Info = None
        self.win_name = None
        self.pid_number = None
        self.Input = "failed to set mouse input"
    
        

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])
        self.options_builder.add_process_selector("Client_Info")
        self.options_builder.add_checkbox_option("Input","Choose Input Method",["Remote","PAG"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            elif option == "Client_Info":
                self.Client_Info = options[option]
                client_info = str(self.Client_Info)
                win_name, pid_number = client_info.split(" : ")
                self.win_name = win_name
                self.pid_number = int(pid_number)
                self.win.window_title = self.win_name
                self.win.window_pid = self.pid_number
                stc.window_title = self.win_name
                Mouse.Mouse.clientpidSet = self.pid_number
                bcp.window_title = self.win_name
            elif option == "Input":
                self.Input = options[option]
                if self.Input == ['Remote']:
                    Mouse.Mouse.RemoteInputEnabledSet = True
                elif self.Input == ['PAG']:
                    Mouse.Mouse.RemoteInputEnabledSet = False
                else:
                    self.log_msg(f"Failed to set mouse")  
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.log_msg(f"{self.win_name}")
        self.log_msg(f"{self.pid_number}")
        self.log_msg(f"{self.Input}")
        self.options_set = True
    def main_loop(self):  # sourcery skip: low-code-quality
        # Setup API
        api = StatusSocket()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # If inventory is full
            if api.get_is_inv_full():
                self.drop_all(skip_slots=list(range(self.protect_slots)))
                logs += 28 - self.protect_slots
                self.log_msg(f"Logs cut: ~{logs}")
                time.sleep(1)
                continue


            # Find a tree
            tree = self.get_nearest_tag(clr.PINK)
            if tree is None:
                failed_searches += 1
                if failed_searches > 10:
                    self.__logout("No tagged trees found. Logging out.")
                time.sleep(1)
                continue

            # Click tree and wait to start cutting
            self.mouse.move_to(tree.random_point())
            self.mouse.click()
            time.sleep(5)

            # Wait so long as the player is cutting
            # -Could alternatively check the API for the player's idle status-
            timer = 0
            while not api.get_is_player_idle():
                self.update_progress((time.time() - start_time) / end_time)
                if timer % 6 == 0:
                    self.log_msg("Chopping tree...")
                time.sleep(2)
                timer += 2
            self.log_msg("Idle...")

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()
