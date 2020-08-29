## CONTRIB Instruction

### Setup

Create virtual env and run the following commands
```
pip install -r dev-requirements.txt
pip install -e .
```


### Test 

To run test you need to setup the following environment variables
```
export DJANGO_SETTINGS_MODULE=tests.settings
export SENDGRID_API_KEY=...
export DEFAULT_FROM_EMAIL=your-sendgrid@email.com
```

You can run plain text with django-admin.py `django-admin.py test` or with `tox`
