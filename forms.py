import sys
from slugify import slugify


def check_list_form(request_form):

    errors = {}

    if request_form['list_name'] == '':
        # flash('Please fill in the list name before clicking the button.')
        errors['longname'] = 'The list name must not be empty.'

    if len(request_form['list_name']) > 100:
        # flash('Your list name is too long!')
        errors['longname'] = 'Your list name is too long!'

    if len(request_form['list_description']) > 500:
        # flash('Your description is too long!')
        errors['description'] = 'Your description is too long!'


    returned_list = {}

    if 'shortname' not in request_form:
        returned_list['shortname'] = slugify(request_form['list_name'], max_length=42, word_boundary=True, save_order=True)
    else:
        returned_list['shortname'] = slugify(request_form['shortname'], max_length=42, word_boundary=True, save_order=True)

    returned_list['longname'] = request_form['list_name']
    returned_list['description'] = request_form['list_description']
    
    if returned_list['shortname'] in ['create','add','_feed']:
        errors['longname'] = '🤔 Ha-ha. Please don’t use forbidden names.'

    return(returned_list, errors)