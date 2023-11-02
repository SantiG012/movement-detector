import pulsar

def pulsarProducer():
    client = pulsar.Client('pulsar://localhost:6650')
    consumer = client.subscribe('my-topic', 'my-sub')

    try:
        while True:
            msg = consumer.receive()
            try:
                # Procesa el mensaje aquí
                data = msg.data()
                print("Mensaje recibido:", data.decode('utf-8'))
            except Exception as e:
                print("Error al procesar el mensaje:", e)
            consumer.acknowledge(msg)  # Confirmar que se ha procesado el mensaje
    finally:
        consumer.close()
        client.close()

# Run the consumer
if __name__ == "__main__":
    pulsarProducer()