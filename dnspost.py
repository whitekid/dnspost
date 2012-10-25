import os
import ConfigParser

from twisted.internet import reactor
from twisted.names import dns
from twisted.names import client, server
from twisted.names import resolve

class DNSServerFactory(server.DNSServerFactory):
    def __init__(self, default_clients, hook_resolvers, verbosity):
        server.DNSServerFactory.__init__(self, None, None, default_clients, verbosity)

        # make custom clients
        name_hook = {
            '.net': '8.8.8.8',
        }

        # make resolvers
        self.hook_resolvers = {}
        for domain, host in name_hook.iteritems():
            self.hook_resolvers[domain] = resolve.ResolverChain([client.Resolver(servers=[(host, 53)])])

        self.hook_resolvers = hook_resolvers

    def handleQuery(self, message, protocol, address):
        if message.opCode == 0 and len(message.queries) == 1:
            query_host = str(message.queries[0].name)
            for hook in self.hook_resolvers.iterkeys():
                if query_host.endswith(hook):
                    saved_resolver = self.resolver
                    try:
                        self.resolver = self.hook_resolvers[hook]
                        return server.DNSServerFactory.handleQuery(self, message, protocol, address)
                    finally:
                        self.resolver = saved_resolver

        return server.DNSServerFactory.handleQuery(self, message, protocol, address)

CONFIG = {
    'hooks': {}
}

def parse_config():
    name = 'dnspost.conf'
    config_files = ['/etc/' + name, '/usr/local/etc/' + name, '%s/%s' % (os.path.expanduser('~'), name), './' + name]
    for name in config_files:
        if not os.path.exists(name): continue

        config = ConfigParser.ConfigParser({
            'listen_port': '53',
            'port': '53',
            'enabled': 'true',
        })

        config.read(name)
        for section in config.sections():
            if section == 'default':
                CONFIG['default.listen_port'] = config.getint(section, 'listen_port')
                CONFIG['default.server'] = config.get(section, 'server')
                CONFIG['default.port'] = config.getint(section, 'port')
            else:
                if not config.getboolean(section, 'enabled'): continue

                dns = {}
                dns['server'] = config.get(section, 'server')
                dns['port'] = config.getint(section, 'port')
                CONFIG['hooks'][section] = dns

def main():
    verbosity  = 1
    parse_config()

    # build resolver
    default_resolver = client.Resolver(servers=[(CONFIG['default.server'], CONFIG['default.port'])])

    hook_resolvers = {}
    for domain, host in CONFIG['hooks'].iteritems():
        hook_resolvers[domain] = \
            resolve.ResolverChain([client.Resolver(servers=[(host['server'], host['port'])])])

    factory = DNSServerFactory([default_resolver], hook_resolvers, verbosity)
    protocol = dns.DNSDatagramProtocol(factory)
    factory.noisy = protocol.noisy = verbosity

    reactor.listenUDP(CONFIG['default.listen_port'], protocol)
    reactor.listenTCP(CONFIG['default.listen_port'], factory)
    reactor.run()

main()

# vim: nu ai ts=4 sw=4 et
