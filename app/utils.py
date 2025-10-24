import os
import requests

def download_image(url, folder="app/static/images"):
    filename = url.split("/")[-1]  # беремо назву файлу з URL
    path = os.path.join(folder, filename)

    if not os.path.exists(folder):
        os.makedirs(folder)

    # якщо файл ще не існує, завантажуємо
    if not os.path.exists(path):
        r = requests.get(url)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
        else:
            raise Exception(f"Не вдалося завантажити з {url}")

    # повертаємо шлях для HTML (відносно /static/)
    return f"images/{filename}"
