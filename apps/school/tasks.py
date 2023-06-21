from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from django.conf import settings

from .models import Course


def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


@shared_task
def run_scrapper(user_id):
    driver = webdriver.Chrome(options=set_chrome_options())

    driver.get("https://orientacion.universia.net.co/cursos/tipos/cursos-administracion-y-negocios/7/1.html")

    print(driver.title)

    # Find all course article elements
    articles = driver.find_elements(By.XPATH, '//article[@class="list-item-node"]')

    # Initialize a list to store course data dictionaries
    courses = []

    # Iterate over the articles and extract relevant data
    for article in articles:
        # Extract title
        title_element = article.find_element(By.XPATH, './/h3[@class="list-entry-title"]/a')
        title = title_element.text

        # Extract description
        description_element = article.find_element(By.XPATH, './/div[@class="ColCursoContenido"]')
        description = description_element.text

        # Extract city
        city_element = article.find_element(By.XPATH, './/tr[td="Ciudad"]/td[2]')
        city = city_element.text

        # Extract university
        university_element = article.find_element(By.XPATH, './/tr[td=" Universidad"]/td[2]')
        university = university_element.text

        # Extract modality
        modality_element = article.find_element(By.XPATH, './/tr[td="Modalidad"]/td[2]')
        modality = modality_element.text

        # Extract type
        type_element = article.find_element(By.XPATH, './/tr[td="Tipo"]/td[2]')
        _type = type_element.text

        # Extract area
        area_element = article.find_element(By.XPATH, './/tr[td="Área"]/td[2]')
        area = area_element.text

        # Create a dictionary with the extracted data
        course_data = {
            'title': title,
            'description': description,
            'city': city,
            'university': university,
            'modality': modality,
            '_type': _type,
            'area': area
        }

        # Append the course data dictionary to the list
        courses.append(course_data)

    driver.quit()

    # Delete existing Course records
    Course.objects.all().delete()

    # Create Course records from the extracted data
    for data in courses:
        # Create a new Course instance with the extracted data
        course = Course(
            name=data['title'],
            description=data['description'],
            city=data['city'],
            university=data['university'],
            modality=data['modality'],
            type=data['_type'],
            area=data['area']
        )

        course.save()

    # Get the User object using the user_id
    user = User.objects.get(id=user_id)

    # Send an email to the user
    send_mail(
        'Asynchronous Task Completed',
        'The asynchronous task has been completed. Course retrieval has finished.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )
