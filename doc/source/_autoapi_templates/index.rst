API Reference
=============

This documentation lists all supported APIs used in Ansys Mechanical. It provides brief descriptions of the objects,
methods, and properties for all namespaces. Click the links to view the API documentation.

.. toctree::
   :titlesonly:
   :maxdepth: 10

   {% for page in pages %}
   {% if (page.top_level_object or page.name.split('.')) and page.display %}
   {{ page.include_path }}
   {% endif %}
   {% endfor %}