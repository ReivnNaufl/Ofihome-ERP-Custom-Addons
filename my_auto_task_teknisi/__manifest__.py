{
    'name': 'Auto Assign Teknisi to Task',
    'version': '1.0',
    'depends': ['project', 'sale_management', 'hr'],
    'author': 'ChatGPT - OpenAI',
    'category': 'Services',
    'summary': 'Automatically assigns Teknisi employee with lowest workload to new tasks',
    'description': """
        When a sales order creates a project task from a service-type product,
        the system automatically assigns an employee with the 'Teknisi' job
        who has the least number of assigned tasks.
    """,
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
