from server import Server

if __name__ == '__main__':
    server = Server()
 
    server.registerRoute('/', 'text/html', './components/index.html')
    server.registerRoute('/image', 'image/jpg', './components/image.jpg')

    port = 3000
    server.listen(port, lambda: print(f'Server listening on port: {port}'))