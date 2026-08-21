---
# create lunr store for search page
---
{%- assign fields = site.data.config-search -%}
var store = [ 
{%- assign first_store_item = true -%}
{%- for item in site.data[site.metadata] -%}
{%- if item.objectid -%}
{%- assign include_search_item = false -%}
{%- if site.data.theme.search-child-objects == true -%}
{%- assign include_search_item = true -%}
{%- elsif item.parentid == nil or item.parentid == '' -%}
{%- assign include_search_item = true -%}
{%- endif -%}
{%- if include_search_item -%}
{%- unless first_store_item -%},{%- endunless -%}
{  
{% for f in fields %}{% if item[f.field] %}{{ f.field | jsonify }}: {{ item[f.field] | normalize_whitespace | replace: '""','"' | jsonify }},{% endif %}{% endfor %} 
"id": {% if item.parentid %}{{ item.parentid | append: '.html#' | append: item.objectid | jsonify }}{% else %}{{item.objectid | append: '.html' | jsonify }}{% endif %}

}
{%- assign first_store_item = false -%}
{%- endif -%}
{%- endif -%}
{%- endfor -%}
];
