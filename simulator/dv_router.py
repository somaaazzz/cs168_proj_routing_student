"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import RoutePacket, \
                     Table, TableEntry, \
                     DVRouterBase, Ports, \
                     FOREVER, INFINITY

class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # Dead entries should time out after this interval
    GARBAGE_TTL = 10

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------
    
    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (self.SPLIT_HORIZON and self.POISON_REVERSE), \
                    "Split horizon and poison reverse can't both be on"
        
        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()
        
        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self


    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        self.table[host] = TableEntry(dst=host, port=port, latency=self.ports.get_latency(port) , expire_time=FOREVER)

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        # if table has entry of the destination, forward it to the next router
        entry = self.table.get(packet.dst)
        if (entry is not None) and (entry.latency < INFINITY):
            self.send(packet, port=entry.port, flood=False)



    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        # send RoutePacket advertisement to all the neighbors
        for entry in self.table.values():
            packet = RoutePacket(destination=entry.dst, latency=entry.latency)
            if self.SPLIT_HORIZON:
                for port in self.ports.get_all_ports():
                    if entry.port != port:
                        self.send(packet, port, flood=False)
            else:
                self.send(packet, flood=True)



    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        # called prtiodically
        for key in list(self.table):
            if self.table[key].expire_time <= api.current_time():
                self.table.pop(key)

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        # if cost of new advertisement <= old route, replace old entry with new advertised entry
        old_entry = self.table.get(route_dst)
        new_route_cost = route_latency + self.ports.get_latency(port)
        # if coming from the same port, take it
        # if old > new, take the new 
        if (old_entry is not None) and (port == old_entry.port):
            self.table[route_dst] = TableEntry(dst=route_dst, port=port, latency=new_route_cost , expire_time=api.current_time() + 15)
        elif (old_entry is None) or (old_entry.latency > new_route_cost):
            self.table[route_dst] = TableEntry(dst=route_dst, port=port, latency=new_route_cost , expire_time=api.current_time() + 15)

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        # TODO: fill in the rest!

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router does down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        # TODO: fill this in!

    # Feel free to add any helper methods!
