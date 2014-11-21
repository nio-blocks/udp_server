"""

  UDP Server

"""
from socketserver import UDPServer, BaseRequestHandler, ThreadingMixIn
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties import BoolProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.string import StringProperty
from nio.modules.communication import PortManager
from nio.modules.threading import spawn


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


@Discoverable(DiscoverableType.block)
class UDPServer(Block):

    """ A block for receiving UDP data """

    host = StringProperty(title="Listener Host", default="127.0.0.1")
    port = IntProperty(title="Listener Port", default=5005)
    threaded = BoolProperty(title="User threads", default=False)
    packet_size = IntProperty(title="Packet size", default=8192)

    def __init__(self):
        super().__init__()
        self._server = None

    def _create_server(self):
        server_class = ThreadedUDPServer if self.threaded else SingleUDPServer
        return server_class((self.host, self.port),
                            UDPDataHandler,
                            self._handle_input)

    def configure(self, context):
        super().configure(context)
        # if no port is specified, get an open one from the PortManager
        if self.port < 0:
            self.port = PortManager.get_port()
        try:
            self._server = self._create_server()
            self._server.max_packet_size = self.packet_size
            self._logger.info("UDP Server listening on %s:%s" %
                              (self.host, self.port))
        except Exception as e:
            self._logger.error("Failed to create server - {0} : {1}".format(
                type(e).__name__, e))
            raise

    def start(self):
        super().start()
        if self._server:
            spawn(self._server.serve_forever)
        else:
            self._logger.warning("Server did not exist, so it was not started")

    def stop(self):
        if self._server:
            self._server.shutdown()
        self._logger.info("UDP Server stopped")
        super().stop()

    def _handle_input(self, raw_data):
        if raw_data is None:
            self._logger.warning("Receiving invalid data")
            return
        self.notify_signals([Signal({"data": raw_data})])