# Create this file: yourapp/management/commands/populate_categories.py

from django.core.management.base import BaseCommand
from bulletins.models import NotificationCategory  # Replace 'yourapp' with your actual app name

class Command(BaseCommand):
    help = 'Populate notification categories'

    def handle(self, *args, **options):
        categories = [
            # Main Categories
            ('rbi_sebi', 'RBI SEBI'),
            ('notification', 'Notification'),
            ('circular', 'Circular'),
            ('income_tax', 'Income Tax'),
            ('service_tax', 'Service Tax'),
            ('central_sales_tax', 'Central Sales Tax'),
            ('excise_matters', 'Excise Matters'),
            ('customs', 'Customs'),
            ('company_law', 'Company Law'),
            ('labour_laws', 'Labour Laws'),
            ('fema', 'FEMA'),
            ('llp_act_2008', 'The LLP Act 2008'),
            ('accounting_standard', 'Accounting Standard (INDAS)'),
            ('others', 'Others'),
            
            # GST Categories
            ('gst', 'GST'),
            ('igst', 'IGST'),
            ('utgst', 'UTGST'),
            ('compensation_cess', 'Compensation Cess'),
            ('ibc_regulation', 'IBC Regulation'),
            
            # VAT Categories
            ('vat', 'VAT'),
            ('delhi_vat', 'Delhi VAT'),
            ('maharashtra_vat', 'Maharashtra VAT'),
            ('gujarat_vat', 'Gujarat VAT'),
            ('telangana_vat', 'Telangana VAT'),
            ('tamil_nadu_vat', 'Tamil Nadu VAT'),
            ('karnataka_vat', 'Karnataka VAT'),
            ('west_bengal_vat', 'West Bengal VAT'),
            ('rajasthan_vat', 'Rajasthan VAT'),
            ('uttar_pradesh_vat', 'Uttar Pradesh VAT'),
            ('punjab_vat', 'Punjab VAT'),
        ]

        for name, display_name in categories:
            category, created = NotificationCategory.objects.get_or_create(
                name=name,
                defaults={'display_name': display_name}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created category: {display_name}')
                )
            else:
                self.stdout.write(f'Category already exists: {display_name}')

        self.stdout.write(
            self.style.SUCCESS('All categories have been processed!')
        )