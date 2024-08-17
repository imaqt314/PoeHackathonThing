from __future__ import annotations
from typing import AsyncIterable
from modal import App, Image, asgi_app, exit
import fastapi_poe as fp

class GPT35TurboBot(fp.PoeBot):
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
app = App(name="gpt35turbobot", image=image)

@app.cls()
class Model:
    def __init__(self):
        self.access_key = "dXiinSEYZOuhBXNVtOrh9Ie0I1dAsUH5"
        self.bot_name = "BotCJQT833Y2S"

    @exit()
    def sync_settings(self):
        """Syncs bot settings on server shutdown."""
        if self.bot_name and self.access_key:
            fp.sync_bot_settings(self.bot_name, self.access_key)
            
    @asgi_app()
    def fastapi_app(self):
        bot = GPT35TurboBot()
        app = fp.make_app(bot, access_key=self.access_key)
        return app

@app.local_entrypoint()
def main():
    Model().run.remote()