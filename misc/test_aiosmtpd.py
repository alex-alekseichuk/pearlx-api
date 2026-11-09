import asyncio
from aiosmtpd.controller import Controller


class SmtpHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        message = envelope.content.decode("utf8", errors="replace")
        print(message)
        return "250 Message accepted for delivery"


controller = Controller(SmtpHandler())
controller.start()
input(f"Controller started {controller.hostname}:{controller.port}")
controller.stop()
