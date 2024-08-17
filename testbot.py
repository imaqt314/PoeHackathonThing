"""

Test bot for variety of functions.

This is the simplest possible bot and a great place to start if you want to build your own bot.

"""

from __future__ import annotations

from typing import AsyncIterable

import fastapi_poe as fp
from modal import App, Image, asgi_app, exit


class TestBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        async for msg in fp.stream_request(
            request, "Llama-3.1-8B-FW-128k", request.access_key
        ):
            # Add whatever logic you'd like here before yielding the result!
            yield msg

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"Llama-3.1-8B-FW-128k": 1})


# =============== MODAL CODE TO RUN THE BOT ================== #
REQUIREMENTS = ["fastapi-poe==0.0.47"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App(name="testbot-poe", image=image)


@app.cls(image=image)
class Model:
    # See https://creator.poe.com/docs/quick-start#integrating-with-poe to find these values.
    def __init__():
        self.access_key = "dXiinSEYZOuhBXNVtOrh9Ie0I1dAsUH5"
        self.bot_name = "BotCJQT833Y2S"

    @exit()
    def sync_settings(self):
        """Syncs bot settings on server shutdown."""
        if self.bot_name and self.access_key:
            try:
                fp.sync_bot_settings(self.bot_name, self.access_key)
            except Exception:
                print("\n*********** Warning ***********")
                print(
                    "Bot settings sync failed. For more information, see: https://creator.poe.com/docs/server-bots-functional-guides#updating-bot-settings"
                )
                print("\n*********** Warning ***********")

    @asgi_app()
    def fastapi_app(self):
        bot = TestBot()
        if not self.access_key:
            print(
                "Warning: Running without an access key. Please remember to set it before production."
            )
            app = fp.make_app(bot, allow_without_key=True)
        else:
            app = fp.make_app(bot, access_key=self.access_key)
        return app


@app.local_entrypoint()
def main():
    Model().run.remote()
