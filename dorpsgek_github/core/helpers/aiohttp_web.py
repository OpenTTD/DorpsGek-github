import asyncio

from aiohttp import helpers
from aiohttp.log import access_logger
from aiohttp.web_runner import (
    AppRunner,
    GracefulExit,
    SockSite,
    TCPSite,
    UnixSite,
)
from collections import Iterable


def prepare_app(app, *, host=None, port=None, path=None, sock=None,
                shutdown_timeout=60.0, ssl_context=None,
                backlog=128, access_log_class=helpers.AccessLogger,
                access_log_format=helpers.AccessLogger.LOG_FORMAT,
                access_log=access_logger, handle_signals=True,
                reuse_address=None, reuse_port=None):
    """
    Slightly modified version of aiohttp.web.run_app, where the server is not
    really started, but the coroutine is returned.
    This allows to caller to run multiple apps at once.
    """
    loop = asyncio.get_event_loop()

    if asyncio.iscoroutine(app):
        app = loop.run_until_complete(app)

    runner = AppRunner(app, handle_signals=handle_signals,
                       access_log_class=access_log_class,
                       access_log_format=access_log_format,
                       access_log=access_log)

    loop.run_until_complete(runner.setup())

    sites = []

    if host is not None:
        if isinstance(host, (str, bytes, bytearray, memoryview)):
            sites.append(TCPSite(runner, host, port,
                                 shutdown_timeout=shutdown_timeout,
                                 ssl_context=ssl_context,
                                 backlog=backlog,
                                 reuse_address=reuse_address,
                                 reuse_port=reuse_port))
        else:
            for h in host:
                sites.append(TCPSite(runner, h, port,
                                     shutdown_timeout=shutdown_timeout,
                                     ssl_context=ssl_context,
                                     backlog=backlog,
                                     reuse_address=reuse_address,
                                     reuse_port=reuse_port))
    elif path is None and sock is None or port is not None:
        sites.append(TCPSite(runner, port=port,
                             shutdown_timeout=shutdown_timeout,
                             ssl_context=ssl_context, backlog=backlog,
                             reuse_address=reuse_address,
                             reuse_port=reuse_port))

    if path is not None:
        if isinstance(path, (str, bytes, bytearray, memoryview)):
            sites.append(UnixSite(runner, path,
                                  shutdown_timeout=shutdown_timeout,
                                  ssl_context=ssl_context,
                                  backlog=backlog))
        else:
            for p in path:
                sites.append(UnixSite(runner, p,
                                      shutdown_timeout=shutdown_timeout,
                                      ssl_context=ssl_context,
                                      backlog=backlog))

    if sock is not None:
        if not isinstance(sock, Iterable):
            sites.append(SockSite(runner, sock,
                                  shutdown_timeout=shutdown_timeout,
                                  ssl_context=ssl_context,
                                  backlog=backlog))
        else:
            for s in sock:
                sites.append(SockSite(runner, s,
                                      shutdown_timeout=shutdown_timeout,
                                      ssl_context=ssl_context,
                                      backlog=backlog))

    runner.prepared_sites = sites
    return runner


def run_apps(runners, print=print):
    """
    Run all apps at once.

    This is part of aiohttp.web.run_app, in combination with prepare_app above.
    """

    loop = asyncio.get_event_loop()

    try:
        for runner in runners:
            for site in runner.prepared_sites:
                loop.run_until_complete(site.start())
        try:
            if print:  # pragma: no branch
                for runner in runners:
                    names = sorted(str(s.name) for s in runner.sites)
                    print("======== Running on {} ========".format(", ".join(names)))
                print("(Press CTRL+C to quit)")
            loop.run_forever()
        except (GracefulExit, KeyboardInterrupt):  # pragma: no cover
            pass
    finally:
        for runner in runners:
            loop.run_until_complete(runner.cleanup())
    if hasattr(loop, "shutdown_asyncgens"):
        loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
