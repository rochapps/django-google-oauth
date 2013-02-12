==========
iContact
==========

A Django application allowing developers to synchronise instances of their models with iContact's Api. Using Django's signals mechanism and generic relations, no changes to the model being synchronised are required, and synchronisation occurs without user intervention over the models lifecycle.

Quick Start Guide
=====

Installation:
*************

In a typical scenario, the following steps are required to use django-icontact::

    1. Add icontact to the list of installed applications in your settings.py.
    2. Define a icontact.adapter.iContactAdapter for each model you want synchronised.
    3. Instantiate an instance of icontact.observer.iContactObserver.
    4. Call the CalendarObserver.observe(model, adapter) method to link models with iContact
    
Example
=======

The code in this example is sufficient to bind a model to iContact's API::

    from django.conf import settings

    from icontact.adapter import IContactAdapter, IContactData
    from icontact.observer import IContactObserver

    from models import Contact

    class ContactsAdapter(CalendarAdapter):
        """
        A icontact adapter for the Contact model.
        """
        
        def get_contact_data(self, instance):
            """
            Returns a iContactData object filled with data from the adaptee.
            """
            return iContactData(
                email=instance.email,
                etc,
            )
    observer = IContactObserver()
    observer.observe(Contact, ContactsAdapter())


www.rochapps.com
================
We built legal management software solutions for attorneys that want to move their practice to the cloud
