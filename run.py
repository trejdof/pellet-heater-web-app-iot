from app import create_app

app = create_app()

# Print static folder path on startup
print(f"Static folder absolute path: {app.static_folder}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
