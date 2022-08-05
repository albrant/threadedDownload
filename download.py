import requests
import os
import bs4
import threading


def download_xkcd(start_comic: int, end_comic: int) -> None:
    for url_number in range(start_comic, end_comic+1):
        url = f'https://xkcd.com/{url_number}'
        print(f'Открытие адреса: {url}')
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        comic_elem = soup.select('#comic img')
        if comic_elem == []:
            print(f'Не удалось найти изображение по адресу \n {url}')
        else:
            protocol = 'https:'
            comic_url = protocol + comic_elem[0].get('src')
            # Загрузка изображения
            print(f'Загрузка {comic_url}')
            res = requests.get(comic_url)
            res.raise_for_status()
            # сохранение в файл в папку ./xkcd
            with open(
                os.path.join(
                    'xkcd',
                    os.path.basename(comic_url)
                    ), 'wb') as image_file:
                for chunk in res.iter_content(100_000):
                    image_file.write(chunk)


def benchmark(func):
    import time

    def wrapper(*args, **kwargs):
        start_benchmark = time.time()
        func(*args, **kwargs)
        end_benchmark = time.time()
        benchmark_time = round(end_benchmark - start_benchmark, 2)
        print(f'[*] Время выполнения составило {benchmark_time} секунд')
    return wrapper


@benchmark
def multi_threading(images_count: int, images_per_thread: int) -> None:
    # Создаём и запускаем потоки
    # на каждый поток по несколько закачек
    download_threads = []
    for i in range(0, images_count, images_per_thread):
        start = i if i > 1 else 1
        end = i + images_per_thread - 1
        download_thread = threading.Thread(
            target=download_xkcd,
            args=(start, end)
        )
        download_thread.daemon = True
        download_threads.append(download_thread)
        download_thread.start()

        # Ожидание завершения всех потоков
        for download_thread in download_threads:
            download_thread.join()
        print('Готово!')


@benchmark
def start_one_thread(images_count: int) -> None:
    download_xkcd(1, images_count)


if __name__ == '__main__':
    IMAGES_COUNT = 50
    # Создаём папку для сохранения всех файлов
    os.makedirs('xkcd', exist_ok=True)

    multi_threading(IMAGES_COUNT, 15)
    # start_one_thread(IMAGES_COUNT)
