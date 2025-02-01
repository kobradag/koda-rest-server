# encoding: utf-8
import asyncio

from kobra.KodadClient import KodadClient
# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto
from kobra.KodadThread import KodadCommunicationError


class KodadMultiClient(object):
    def __init__(self, hosts: list[str]):
        self.kobras = [KodadClient(*h.split(":")) for h in hosts]

    def __get_kobra(self):
        for k in self.kobras:
            if k.is_utxo_indexed and k.is_synced:
                return k

    async def initialize_all(self):
        tasks = [asyncio.create_task(k.ping()) for k in self.kobras]

        for t in tasks:
            await t

    async def request(self, command, params=None, timeout=60, retry=3):
        try:
            return await self.__get_kobra().request(command, params, timeout=timeout, retry=1)
        except KodadCommunicationError:
            await self.initialize_all()
            return await self.__get_kobra().request(command, params, timeout=timeout, retry=retry)

    async def notify(self, command, params, callback):
        return await self.__get_kobra().notify(command, params, callback)
