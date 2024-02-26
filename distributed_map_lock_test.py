import time
import threading

from functools import wraps

from hazelcast import HazelcastClient
from hazelcast.config import Config


CONFIG = Config()
CONFIG.cluster_name = "hazelcast-homework"


def time_measure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  
        name, result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{name} executed in  {time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}"  
              f" seconds. Execution result: {result}")
        return result
    return wrapper


class Incrementer:
    def __init__(self, hz_client, count) -> None:
        self.__count = count
        self.__map = hz_client.get_map("my-distributed-map").blocking()
        

    def unsafe_increment_map_value(self, key: str) -> None:
        self.__map.put_if_absent(key, 0)
        for _ in range(self.__count):
            self.__map.put(key, self.__map.get(key) + 1)


    def pesimis_block_increment_map_value(self, key: str) -> None:
        self.__map.put_if_absent(key, 0)
        for _ in range(self.__count):
            self.__map.lock(key)
            try:
                self.__map.put(key, self.__map.get(key) + 1)
            finally:
                self.__map.unlock(key)


    def increment_map_value_optim_block(self, key: str) -> None:
        self.__map.put_if_absent(key, 0)
        for _ in range(self.__count):
            while True:
                current_value = self.__map.get(key)
                new_value = current_value + 1
                if self.__map.replace_if_same(key, current_value, new_value):
                    break  


    @time_measure
    def performance_measure(self, func, key) -> int:
        threads = [threading.Thread(target=func, args=(key,)) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return func.__name__, self.__map.get(key)


def main():
    count = 10_000
    hz_client = HazelcastClient(CONFIG)
    incrementer = Incrementer(hz_client=hz_client, count=count)

    keys = ["undafe_key", "pissim_key", "optim_key"]
    functions = [incrementer.unsafe_increment_map_value, 
                incrementer.pesimis_block_increment_map_value, 
                incrementer.increment_map_value_optim_block]
    
    for i in range(len(keys)):
        incrementer.performance_measure(functions[i], keys[i])

    hz_client.shutdown()

if __name__ == "__main__":
    main()
