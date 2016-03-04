============
Installation
============

Retrieve and install CloudKitty dashboard:

::

    git clone git://git.openstack.org/openstack/cloudkitty-dashboard
    cd cloudkitty-dashboard
    python setup.py install


Find where the python packages are installed:

::

    PY_PACKAGES_PATH=`pip --version | cut -d' ' -f4`


Then add the additional settings file to the horizon settings or installation.
Depending on your setup, you might need to add it to ``/usr/share`` or directly
in the horizon python package:

::

    # If horizon is installed by packages:
    ln -s $PY_PACKAGES_PATH/cloudkittydashboard/enabled/_[0-9]*.py \
    /usr/share/openstack-dashboard/openstack_dashboard/enabled/

    # Directly from sources:
    ln -s $PY_PACKAGES_PATH/cloudkittydashboard/enabled/_[0-9]*.py \
    $PY_PACKAGES_PATH/openstack_dashboard/enabled/


Restart the web server hosting Horizon.

For more detailed information about CloudKitty installation check out the
`installation section`_ of the documentation.


.. _installation section: https://cloudkitty.readthedocs.org/en/latest/installation.html
