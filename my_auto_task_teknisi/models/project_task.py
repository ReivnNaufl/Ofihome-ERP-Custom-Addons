from odoo import models, api
import math

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @api.model
    def create(self, vals):
        task = super().create(vals)

        sale_line = task.sale_line_id
        if sale_line and sale_line.product_id.type == 'service':
            customer = sale_line.order_id.partner_id

            cust_lat = customer.x_latitude
            cust_lon = customer.x_longitude

            if not (cust_lat and cust_lon):
                return task  # Cannot proceed without customer coordinates

            teknisi_job = self.env['hr.job'].search([('name', 'ilike', 'Teknisi')], limit=1)
            if teknisi_job:
                teknisi_employees = self.env['hr.employee'].search([
                    ('job_id', '=', teknisi_job.id),
                    ('user_id', '!=', False),
                    ('work_contact_id', '!=', False)
                ])

                teknisi_list = []
                fallback_teknisi_list = []

                for emp in teknisi_employees:
                    user = emp.user_id
                    task_count = self.search_count([
                        ('user_ids', 'in', user.id),
                        ('stage_id.fold', '=', False)
                    ])

                    partner = emp.work_contact_id
                    tech_lat = partner.x_latitude
                    tech_lon = partner.x_longitude

                    if tech_lat and tech_lon:
                        distance = self._haversine(
                            cust_lat,
                            cust_lon,
                            tech_lat,
                            tech_lon
                        )
                        teknisi_list.append((emp, task_count, distance))
                    else:
                        fallback_teknisi_list.append((emp, task_count))

                if teknisi_list:
                    sorted_teknisi = sorted(teknisi_list, key=lambda x: (x[1], x[2]))
                    best_teknisi = sorted_teknisi[0][0]
                elif fallback_teknisi_list:
                    sorted_fallback = sorted(fallback_teknisi_list, key=lambda x: x[1])
                    best_teknisi = sorted_fallback[0][0]
                else:
                    return task  # No available technicians

                if best_teknisi.user_id:
                    task.user_ids = [(4, best_teknisi.user_id.id)]

        return task
