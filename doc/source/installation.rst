============
Installation
============

Retrieve and install CloudKitty dashboard:

::

    git clone https://opendev.org/openstack/cloudkitty-dashboard
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


Configuration
=============

To configure CloudKitty dashboard, add variables to your Horizon settings
file.
For more details about how to add variables to Horizon settings checkout the
`Horizon Settings Reference documentation`_.


.. _Horizon Settings Reference documentation: https://docs.openstack.org/horizon/latest/configuration/settings.html

Rate Pre/Postfix
----------------

You can configure pre/postfix to rate vaules shown at the dashboard.

Here's example of setting rate currency to US Dollar.

.. code-block:: python

   # You can choose to have prefix or postfix or both.
   # Prefix and postfix are not mutally exclusive.
   OPENSTACK_CLOUDKITTY_RATE_PREFIX = '$'
   OPENSTACK_CLOUDKITTY_RATE_POSTFIX = 'USD'

Some symbols (Such as Non-ASCII) might require to use unicode value directly.

.. code-block:: python

   # British Pound
   OPENSTACK_CLOUDKITTY_RATE_PREFIX = u'\xA3'
   OPENSTACK_CLOUDKITTY_RATE_POSTFIX = 'GBP'
