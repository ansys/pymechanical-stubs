API Reference
=============

This documentation lists all supported APIs used in Ansys Mechanical. It provides brief descriptions of the objects,
methods, and properties for all namespaces.

.. toctree::
   :titlesonly:
   :maxdepth: 3

   {% for page in pages %}
   {% if (page.top_level_object or page.name.split('.') | length == 3) and page.display %}
   <span class="nf nf-md-package"></span> {{ page.name }}<{{ page.include_path }}>
   {% endif %}
   {% endfor %}