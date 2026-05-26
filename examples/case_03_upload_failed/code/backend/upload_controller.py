MAX_SIZE = 5 * 1024 * 1024

def upload(file):
    if file.size > MAX_SIZE:
        return {"message": "upload failed"}, 413
    return save_file(file)
