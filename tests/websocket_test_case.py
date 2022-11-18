import asyncio
import json
import logging
from multiprocessing import Pool

import dill
from websockets import connect

from tests.base_test_case import MVPTestCase
from tests.conftest import option


def _run_dill_encoded(payload):
    fun, args = dill.loads(payload)
    return fun(*args)


def _map_async(pool, fun, *args):
    payload = dill.dumps((fun, *args))
    return pool.map_async(_run_dill_encoded, (payload,))


class WebSocketTestCase(MVPTestCase):

    def setup_method(self):
        super().setup_method()
        self.uri = option.url.replace("http", "ws")

    def create_connection(self, functions: list, params: list = None):
        pool = Pool(len(functions))
        results = list()
        if params:
            for i, func in enumerate(functions):
                results.append(_map_async(pool, func, params[i]))
        else:
            for func in functions:
                results.append(_map_async(pool, func, []))
        return [result.get() for result in results]

    def eth_subscribe(self, params="newHeads"):
        async def get_pending(subscription_params):
            data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_subscribe",
                "params": [subscription_params]
            }
            result = list()
            async with connect(self.uri) as ws:
                await ws.send(json.dumps(data))
                response = json.loads((await ws.recv()))
                try:
                    subscription_id = response["result"]
                    logging.info(f"Subscription id: {subscription_id}")
                except KeyError:
                    raise Exception(f"Can not get subscription id, got response:\n{response}")
                for _ in range(20):
                    try:
                        message = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                        result.append(message)
                    except Exception as e:
                        logging.info(e)
            logging.info(f"Response:\n{result}")
            return subscription_id, result

        return asyncio.run(get_pending(subscription_params=params))
