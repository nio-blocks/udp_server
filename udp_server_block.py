from socketserver import UDPServer, BaseRequestHandler, ThreadingMixIn

from nio import GeneratorBlock
from nio.properties import \
    BoolProperty, IntProperty, StringProperty, VersionProperty
from nio.signal.base import Signal
from nio.util.threading.spawn import spawn


class SingleUDPServer(UDPServer):

    def __init__(self, server_address, handler_class, notifier):
        super().__init__(server_address, handler_class)
        self.notifier = notifier


class ThreadedUDPServer(ThreadingMixIn, SingleUDPServer):

    def __init__(self, server_address, handler_class, notifier):
        super().__init__(server_address, handler_class, notifier)


class UDPDataHandler(BaseRequestHandler):

    def handle(self):
        # Just notify raw data received
        self.server.notifier(self.request[0].strip())


class UDPServer(GeneratorBlock):

    version = VersionProperty("1.0.0")
    host = StringProperty(title="Listener Host", default='[[NIOHOST]]')
    port = IntProperty(title="Listener Port", allow_none=False)
    threaded = BoolProperty(title="User threads", default=False)
    packet_size = IntProperty(title="Packet size", default=8192)

    def __init__(self):
        super().__init__()
        self._server = None

    def _create_server(self):
        server_class = \
            ThreadedUDPServer if self.threaded() else SingleUDPServer
        return server_class((self.host(), self.port()),
                            UDPDataHandler,
                            self._handle_input)

    def configure(self, context):
        super().configure(context)

        try:
            self._server = self._create_server()
            self._server.max_packet_size = self.packet_size()
            self.logger.info("UDP Server listening on {}:{}"
                             .format(self.host(), self.port()))
        except Exception as e:
            self.logger.error("Failed to create server - {0} : {1}".format(
                type(e).__name__, e))
            raise

    def start(self):
        super().start()
        if self._server:
            spawn(self._server.serve_forever)
        else:
            self.logger.warning("Server did not exist, so it was not started")

    def stop(self):
        if self._server:
            self._server.shutdown()
        self.logger.info("UDP Server stopped")
        super().stop()

    def _handle_input(self, raw_data):
        if raw_data is None:
            self.logger.warning("Receiving invalid data")
            return
        self.notify_signals([Signal({"data": raw_data})])
