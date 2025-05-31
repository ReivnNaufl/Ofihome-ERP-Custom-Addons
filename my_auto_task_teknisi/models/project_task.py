from odoo import models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        task = super().create(vals)

        # Pastikan task berasal dari Sales Order Line
        sale_line = task.sale_line_id
        if sale_line and sale_line.product_id and sale_line.product_id.type == 'service':
            # Cari job 'Teknisi'
            teknisi_job = self.env['hr.job'].search([('name', 'ilike', 'Teknisi')], limit=1)
            if teknisi_job:
                teknisi_employees = self.env['hr.employee'].search([
                    ('job_id', '=', teknisi_job.id),
                    ('user_id', '!=', False)
                ])

                if teknisi_employees:
                    # Hitung jumlah task yang dimiliki setiap teknisi
                    employee_task_counts = {}
                    for emp in teknisi_employees:
                        user = emp.user_id
                        count = self.search_count([
                            ('user_ids', 'in', user.id),
                            ('stage_id.fold', '=', False)  # hanya task yang belum selesai
                        ])
                        employee_task_counts[emp] = count

                    # Pilih employee dengan task paling sedikit
                    best_teknisi = min(employee_task_counts, key=employee_task_counts.get)
                    if best_teknisi.user_id:
                        task.user_ids = [(4, best_teknisi.user_id.id)]  # Assign user ke task

        return task
