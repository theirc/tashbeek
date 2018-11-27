from datetime import date, datetime
import numpy as np


def calculate_age(born):
    today = date.today()
    if born in ['---', '']:
        return ''
    born = datetime.strptime(born, '%Y-%m-%d')
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def concat(col1, col2, debug=False):
    prohibited = ['', '---', 'nan']
    if col1 not in prohibited:
        return col1
    elif col2 not in prohibited:
        return col2
    else:
        return ''

def age_concat(col1, col2):
    prohibited = ['', '---', 'nan']
    col1 = 0 if col1 in prohibited else float(col1)
    col2 = 0 if col2 in prohibited else float(col2)
    col1 = 0 if np.isnan(col1) else col1
    col2 = 0 if np.isnan(col2) else col2
    return col1 if col1 != 0 else col2

def lat(col):
    try:
        return float(col.split(' ')[0])
    except:
        return 0

def lng(col):
    try:
        return float(col.split(' ')[1])
    except:
        return 0

def update_profession(col):
    col = col.replace(['1'], 'management')
    col = col.replace(['2'], 'business')
    col = col.replace(['3'], 'computer')
    col = col.replace(['4'], 'engineering')
    col = col.replace(['5'], 'social_science')
    col = col.replace(['6'], 'social_service')
    col = col.replace(['7'], 'law')
    col = col.replace(['8'], 'teaching')
    col = col.replace(['9'], 'media')
    col = col.replace(['10'], 'healthcare_tech')
    col = col.replace(['11'], 'healthcare_support')
    col = col.replace(['12'], 'protective_science')
    col = col.replace(['13'], 'food')
    col = col.replace(['14'], 'janitor')
    col = col.replace(['15'], 'salon')
    col = col.replace(['16'], 'sales')
    col = col.replace(['17'], 'admin')
    col = col.replace(['18'], 'agriculture')
    col = col.replace(['19'], 'construction')
    col = col.replace(['20'], 'repair')
    col = col.replace(['21'], 'production')
    col = col.replace(['22'], 'driving')
    col = col.replace(['23'], 'military_police')
    col = col.replace(['24'], 'automotive')
    return col

get_lat = np.vectorize(lat)
get_lng = np.vectorize(lng)
np_age = np.vectorize(calculate_age)
np_concat = np.vectorize(concat)
np_age_concat = np.vectorize(age_concat)
