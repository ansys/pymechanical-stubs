.. vale off

API reference
=============

This documentation lists all supported APIs used in Ansys Mechanical. It provides brief
descriptions of the objects, methods, and properties for all namespaces.

.. toctree::
   :titlesonly:
   :maxdepth: 3

   {% for page in pages %}
   {% if (page.top_level_object or page.name.split('.') | length == 4) and page.display %}
   {% set page_name = page.name.split('.')|list %}
   {% set version = page_name[-1] %}
   <span class="nf nf-md-package"></span>Mechanical 20{{ version[1:3] }} R{{ version[3] }}<{{ page.include_path }}>
   {% endif %}
   {% endfor %}

.. toctree::
   :hidden:

   ansys/mechanical/stubs/index

.. vale on