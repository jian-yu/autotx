def WriteToFile(dir, fileName, data):
    filePath = dir + '/' + fileName
    with open(filePath, 'w', encoding='utf-8') as file:
        if file.writable():
            file.write(data)
            return filePath, None
        return None, Exception('file is unable to write')