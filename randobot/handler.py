import asyncio
from datetime import datetime, timedelta
from racetime_bot import RaceHandler, monitor_cmd, can_monitor

class RandoHandler(RaceHandler):
    stop_at = ["cancelled", "finished"]
    CURRENT_STANDARD_RACE_GOAL = "Standard Race - Defeat Ganondorf"
    CURRENT_SPOILER_LOG_GOAL = "Spoiler Log"

    def __init__(self, generator, **kwargs):
        super().__init__(**kwargs)

        self.generator = generator
        self.loop = asyncio.get_event_loop()
        self.loop_ended = False

    async def begin(self):
        if not self.state.get("initialized"):
            self.state["initialized"] = True
            self.state["finished_entrants"] = set()
            self.state["race_delay"] = timedelta(0, 15)

        self.loop.create_task(self.handle_scheduled_tasks())

    async def race_data(self, data):
        self.data = data.get('race')
        if self.data.goal.custom == false:
            if self.data.goal.name == CURRENT_STANDARD_RACE_GOAL:
                self.state["standard_race"] = True
                self.state["spoiler_log"] = False
                self.state["race_delay"] = timedelta(0, 15, 0, 0, 15)
            elif self.data.goal.name == CURRENT_SPOILER_LOG_GOAL:
                self.state["standard_race"] = False
                self.state["spoiler_log"] = True
                self.state["race_delay"] = timedelta(0, 15, 0, 0, 50)
            else:
                self.state["standard_race"] = False
                self.state["spoiler_log"] = False

    def close_handler(self):
        self.loop_ended = True

    async def handle_scheduled_tasks(self):
        while not self.loop_ended:
            try:
                if self.state.get("seed_rolled"):
                    seconds_remaining = self.seconds_remaining(False)
                    race_delay = self.seconds_remaining(True)

                    if not self.state.get("40_warning_sent") and seconds_remaining < 2400 and race_delay > 2400: # 40 minutes
                        await self.send_message("You have 40 minutes until the race starts!")
                        self.state["40_warning_sent"] = True

                    if not self.state.get("30_warning_sent") and seconds_remaining < 1800 and race_delay > 1800: # 30 minutes
                        await self.send_message("You have 30 minutes until the race starts!")
                        self.state["30_warning_sent"] = True

                    if not self.state.get("20_warning_sent") and seconds_remaining < 1200 and race_delay > 1200: # 20 minutes
                        await self.send_message("You have 20 minutes until the race starts!")
                        self.state["20_warning_sent"] = True

                    if not self.state.get("permalink_available") and seconds_remaining < 900 and race_delay > 900: # 15 minutes
                        await self.send_message("You have 15 minutes until the race starts!")
                        permalink = self.state.get("permalink")
                        await self.send_message(f"Permalink: {permalink}")
                        self.state["permalink_available"] = True

                    if not self.state.get("10_warning_sent") and seconds_remaining < 600 and race_delay > 600: # 10 minutes
                        await self.send_message("You have 10 minutes until the race starts!")
                        await self.send_message("Please start your stream if you haven't done so already!")
                        self.state["10_warning_sent"] = True

                    if not self.state.get("5_warning_sent") and seconds_remaining < 300: # 5 minutes
                        await self.send_message("You have 5 minutes until the race starts!")
                        self.state["5_warning_sent"] = True

                    if not self.state.get("file_name_available") and seconds_remaining < 60: # 1 minute
                        await self.send_message("You have 1 minute until the race starts!")
                        file_name = self.state.get("file_name")
                        await self.send_message(f"File Name: {file_name}")
                        self.state["file_name_available"] = True

                    if not self.state.get("race_started") and seconds_remaining < 15:
                        await self.force_start()
                        self.state["race_started"] = True
            finally:
                await asyncio.sleep(0.5)

    async def error(self, data):
        self.logger.info(data.get('errors'))

    async def race_data(self, data):
        self.data = data.get("race")

        if self.state.get("seed_rolled"):
            finished_entrants = set(
                map(
                    lambda entrant: entrant.get("user").get("name"),
                    filter(
                        lambda entrant: entrant.get("status").get("value") == "done",
                        self.data.get("entrants")
                    )
                )
            )

            new_finishers = list(finished_entrants - self.state["finished_entrants"])

            for finisher in new_finishers:
                await self.send_message(
                    f"{finisher}, before you end your stream, please remember to advance to the second text box after defeating Ganondorf."
                )

            self.state["finished_entrants"] = finished_entrants

    async def ex_summonbot(self, args, message):
        race_delay = (self.state.get["race_delay"] - timedelta.(0,15)).total_minutes()
        if self.state.get("standard_race"):
            await self.send_message(f"Please use command !startrace to get a permalink, race is set to start {race_delay} minutes after that.")
        elif self.state.get("spoiler_log")
            await self.send_message(f"Please use command !startrace to get a link to the spoiler log, race is set to start {race_delay} minutes after that.")
        else
            await self.send_message("You've summoned me to a custom room! I don't know how to handle this yet. Sorry!")

    async def ex_removebot(self, args, message):
        self.state["remove_bot"] = True
        await self.send_message("This will remove the bot and it will forget all currently set settings, use !confirm to do this, otherwise use !cancel")

    async def ex_confirm(self, args, message):
        if self.state.get("remove_bot"):
            self.should_stop()

    async def ex_cancel(self, args, message):
        if self.state.get("remove_bot"):
            await self.send_message("Command Cancelled")
            self.state["remove_bot"] = False

    async def ex_tingletuner(self, args, message):
        if self.state.get("tingle_tuner_banned"):
            await self.send_message("The Tingle Tuner is banned in this race.")
        elif self.state.get("seed_rolled"):
            await self.send_message("The Tingle Tuner is allowed in this race.")
        else:
            await self.send_message(
                "Use !bantingletuner if you'd like the Tingle Tuner to be banned in this race. The "
                "ban will go into effect if at least one runner asks for the Tingle Tuner to be banned."
            )

    async def ex_bantingletuner(self, args, message):
        if self.state.get("tingle_tuner_banned"):
            await self.send_message("The Tingle Tuner is already banned in this race.")
        elif self.state.get("seed_rolled") and not can_monitor(message):
            await self.send_message("The race has already started! The Tingle Tuner is allowed in this race.")
        else:
            self.state["tingle_tuner_banned"] = True
            await self.send_message("The Tingle Tuner is now banned in this race.")

    @monitor_cmd
    async def ex_unbantingletuner(self, args, message):
        if not self.state.get("tingle_tuner_banned"):
            await self.send_message("The Tingle Tuner is already allowed in this race.")
        else:
            self.state["tingle_tuner_banned"] = False
            await self.send_message("The Tingle Tuner is now allowed in this race.")

    async def ex_spoilerlogurl(self, args, message):
        if self.state.get("seed_rolled") and (can_monitor(message) or self.state.get("spoiler_log_available")):
            spoiler_log_url = self.state.get("spoiler_log_url")
            await self.send_message(f"Spoiler Log: {spoiler_log_url}")
        else:

    async def ex_permalink(self, args, message):
        if self.state.get("seed_rolled") and (can_monitor(message) or self.state.get("permalink_available")):
            permalink = self.state.get("permalink")
            await self.send_message(f"Permalink: {permalink}")
        else:
            await self.send_message("Permalink is not available yet!")

    async def ex_filename(self, args, message):
        if self.state.get("seed_rolled") and (can_monitor(message) or self.state.get("file_name_available")):
            file_name = self.state.get("file_name")
            await self.send_message(f"File Name: {file_name}")
        else:
            await self.send_message("File Name is not available yet!")

    async def ex_time(self, args, message):
        if not self.state.get("seed_rolled"):
            await self.send_message("Seed has not been generated yet!")
        elif self.state.get("race_started"):
            await self.send_message("Race has already started!")
        else:
            duration = datetime.utcfromtimestamp(self.seconds_remaining())
            time_remaining = duration.strftime("%M:%S")
            await self.send_message(f"You have {time_remaining} until the race starts!")

    def seconds_remaining(self, args):
        if(args == True):
            return (self.state.get("race_delay") - timedelta(0,15)).total_seconds()
        if not self.state.get("time_paused"):
            return (self.state.get("race_start_time") - datetime.now()).total_seconds()
        else:
            return 9999

    async def ex_startrace(self, args, message):
        if self.state.get("spoiler_log"):
            startspoilerlograce(self, args, message)
        elif self.state.get("standard_race"):
            startstandardrace(self, message)
        elif
            await self.send_message("This is for future development!")

    @monitor_cmd
    async def startspoilerlograce(self, args, message):
        if not self.state.get("spoiler_log"):
            await self.send_message("This is not a spoiler log race!")
            return
        await self.roll_and_send(args, message)
            await self.send_message("Spoiler Log is not available yet!")

    async def startstandardrace(self, message):
        if not self.state.get("seed_rolled") and self.state.get("standard_race"):
            permalink = self.state.get("permalink")
            self.state["seed_rolled"] = True
            await self.send_message(f"Permalink: {permalink}")
            await self.send_message("The bot is defaulted to start in {} minutes, if you wish to change that, please use !pause. You'll have to force start later, or use !unpause")

    async def roll_and_send(self, args, message):
        if self.state.get("seed_rolled"):
            await self.send_message(
                "Seed already generated!"
            )
            return

        self.loop.create_task(self.roll())

    async def roll(self):
        self.state["seed_rolled"] = True

        await self.send_message("Generating seed...")

        generated_seed = self.generator.generate_seed()
        spoiler_log_url = generated_seed.get("spoiler_log_url")
        permalink = generated_seed.get("permalink")
        file_name = generated_seed.get("file_name")

        self.logger.info(spoiler_log_url)
        self.logger.info(permalink)
        self.logger.info(file_name)

        self.state["spoiler_log_url"] = spoiler_log_url
        self.state["permalink"] = permalink
        self.state["file_name"] = file_name
        self.state["race_start_time"] = datetime.now() + timedelta(0, 15, 0, 0, 50)

        await self.send_message("Seed generated! Preparation stage starts in 15 seconds...")

        await asyncio.sleep(10)
        await self.send_message("5...")
        await asyncio.sleep(1)
        await self.send_message("4...")
        await asyncio.sleep(1)
        await self.send_message("3...")
        await asyncio.sleep(1)
        await self.send_message("2...")
        await asyncio.sleep(1)
        await self.send_message("1...")
        await asyncio.sleep(1)

        await self.send_message("You have 50 minutes to prepare your route!")
        await self.send_message(f"Spoiler Log: {spoiler_log_url}")
        self.state["spoiler_log_available"] = True
