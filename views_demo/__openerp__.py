# -*- coding: utf-8 -*-
{
    'name': "Demo of views",
    'summary': "Views",
    'depends': ['base'],
    'data': [
        # ordering matters. Security files should be on the top
        # security groups
        # model security access
        # ..Other data files
        #'security/ir.model.access.csv',
        "views/add_a_menu_item_and_window_action.xml",
        #"views/have_an_action_open_a_specific_view.xml",
        "views/list_views.xml",
        "views/search_views.xml",
    ],
    'description': "Showcase some of the demos."
}