def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'mp3', 'acc', 'ogg', 'wav', 'wma'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS