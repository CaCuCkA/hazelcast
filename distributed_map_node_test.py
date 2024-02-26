from hazelcast import HazelcastClient
from hazelcast.config import Config


ELEMENT_NUM = 1000

CONFIG = Config()
CONFIG.cluster_name = "hazelcast-homework"


def add_elements(map):
    map.put_all({key: f"value_{key}" for key in range(1_000)})


def count_elements(map):
    miss_number = 0
    for i in range(ELEMENT_NUM):
        miss_number += int(map.get(i) is None)
    assert miss_number == 0, f"The {miss_number} data was missed!"


def main():
    client = HazelcastClient(CONFIG)
    client
    my_map = client.get_map("my-distributed-map").blocking()

    add_elements(my_map) if my_map.size() == 0 else count_elements(my_map)
    client.shutdown()

if __name__ == "__main__":
    main()