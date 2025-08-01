import pika, argparse, json, logging
from importlib import import_module
from baseapp.config.rabbitmq import RabbitMqConn

logger = logging.getLogger("rabbit")

def start_consuming(queue_name: str):
    """
    Memulai worker untuk mendengarkan pesan dari antrian secara terus-menerus.
    """
    try:
        # Gunakan context manager untuk koneksi yang andal
        with RabbitMqConn() as channel:
            # Deklarasi antrian yang andal, harus cocok dengan publisher
            channel.queue_declare(queue=queue_name, durable=True, auto_delete=False)
            
            # Ambil 1 pesan per worker pada satu waktu untuk distribusi beban yang adil
            channel.basic_qos(prefetch_count=1)

            # Definisikan fungsi callback di dalam scope ini agar bisa mengakses 'channel'
            def callback(ch, method, properties, body):
                logger.info("Menerima tugas baru dari antrian.")
                try:
                    # Proses pesan
                    messageObj = json.loads(body)
                    if "_execfile" in messageObj:
                        _execModule = import_module(messageObj["_execfile"])
                        _execFunction = getattr(_execModule, "_runcommand")
                        _execFunction(messageObj['data'])
                    
                    # Kirim konfirmasi HANYA SETELAH tugas selesai diproses
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info("Tugas berhasil diselesaikan.")

                except Exception as e:
                    logger.error(f"Terjadi error saat memproses tugas: {e}")
                    # Tolak pesan (nack) dan jangan masukkan kembali ke antrian (requeue=False)
                    # Ini akan mengirim pesan ke Dead Letter Exchange jika dikonfigurasi
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # Mulai proses consuming dengan manual acknowledgement
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False # Sangat penting untuk keandalan
            )

            logger.info(f"[*] Worker siap menerima pesan dari antrian '{queue_name}'. Tekan CTRL+C untuk keluar.")
            channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Worker dihentikan.")
    except Exception as e:
        logger.error(f"Koneksi ke RabbitMQ terputus atau gagal: {e}")


if __name__ == "__main__":
    # Buat parser untuk argumen command-line
    parser = argparse.ArgumentParser(description="RabbitMQ Consumer Worker")
    parser.add_argument(
        '--queue', 
        type=str, 
        required=True, 
        help="Nama antrian yang akan di-consume."
    )
    args = parser.parse_args()

    # Jalankan worker untuk mendengarkan antrian 'webhook_tasks'
    start_consuming(queue_name=args.queue)