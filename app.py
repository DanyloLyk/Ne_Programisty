from app import create_app

app = create_app()

if __name__ == "__main__":
    print("-" * 50)
    print("🚀 САЙТ ПРАЦЮЄ ТУТ: http://127.0.0.1")
    print("-" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)