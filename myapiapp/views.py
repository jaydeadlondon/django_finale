from django.shortcuts import render
from django.http import HttpResponse
import os


def upload_file_view(request):
    if request.method == 'GET':
        return render(request, 'myapiapp/upload.html')

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return HttpResponse('Файл не выбран', status=400)

        max_file_size = 1 * 1024 * 1024

        if uploaded_file.size > max_file_size:
            return HttpResponse(
                f'Файл слишком большой. Максимальный размер: 1 МБ. '
                f'Размер вашего файла: {uploaded_file.size / 1024 / 1024:.2f} МБ',
                status=400
            )

        try:
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            return HttpResponse(
                f'Файл "{uploaded_file.name}" успешно загружен! '
                f'Размер: {uploaded_file.size / 1024:.2f} КБ'
            )

        except Exception as e:
            return HttpResponse(f'Ошибка при сохранении файла: {str(e)}', status=500)

    return HttpResponse('Метод не поддерживается', status=405)