
#!/bin/bash
until python manage.py migrate; do
  sleep 2
  echo "Retry!";
done

echo "Django is ready.";
python manage.py runserver 0.0.0.0:8000
