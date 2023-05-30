import inspect
from typing import Text, Callable, Awaitable

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse


class EnviroCar(InputChannel):
    def name(self) -> Text:
        """Name of your custom channel."""
        return "envirocar"

    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender")  # method to get sender_id
            message = request.json.get("message")  # method to fetch message
            input_channel = self.name()  # method to fetch input channel
            metadata = self.get_metadata(request)  # method to get metadata

            collector = CollectingOutputChannel()

            # include exception handling

            await on_new_message(
                UserMessage(
                    message,
                    collector,
                    sender_id,
                    input_channel=input_channel,
                    metadata=metadata,
                )
            )

            return response.json(collector.messages)

        return custom_webhook

    def get_metadata(self, request: Request):
        """Extracts the metadata from a user message.
            Args:
                request: A `Request` object
            Returns:
                Metadata extracted from the sent event payload.
            """
        return request.json.get("metadata", None)
