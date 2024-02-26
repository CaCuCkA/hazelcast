import hazelcast
import threading


def produce(queue):
    for i in range(1, 101):
        if not queue.offer(f"value-{i}", 1).result():
            print("Queue is full")
            return


def consume(queue, consumer_id):
    while queue.size():
        item = queue.poll(1).result()
        if item is None:
            print("Queue is empty")
            return
        print(f"Consumer {consumer_id} consumed {item}")


def main():
    client = hazelcast.HazelcastClient(cluster_name="hazelcast-homework")
    queue = client.get_queue("queue")

    threads = [
        threading.Thread(target=produce, args=(queue,)),
        threading.Thread(target=consume, args=(queue, 1)),
        threading.Thread(target=consume, args=(queue, 2)),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    client.shutdown()


if __name__ == "__main__":
    main()
