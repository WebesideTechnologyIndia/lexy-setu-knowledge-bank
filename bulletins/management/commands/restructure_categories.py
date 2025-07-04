# management/commands/restructure_categories.py
from django.core.management.base import BaseCommand
from bulletins.models import NotificationCategory

class Command(BaseCommand):
    help = 'Restructure VAT categories to hierarchical structure'
    
    def handle(self, *args, **options):
        # Pehle VAT main category get karo
        try:
            vat_main = NotificationCategory.objects.get(name='vat')
            self.stdout.write('VAT main category found')
        except NotificationCategory.DoesNotExist:
            # VAT main category banao
            vat_main = NotificationCategory.objects.create(
                name='vat',
                display_name='VAT'
            )
            self.stdout.write('VAT main category created')
        
        # VAT subcategories list
        vat_subcategories = [
            'delhi_vat',
            'maharashtra_vat',
            'gujarat_vat',
            'telangana_vat',
            'tamil_nadu_vat',
            'karnataka_vat',
            'west_bengal_vat',
            'rajasthan_vat',
            'uttar_pradesh_vat',
            'punjab_vat',
        ]
        
        # Subcategories ko VAT ke under move karo
        for sub_name in vat_subcategories:
            try:
                sub_category = NotificationCategory.objects.get(name=sub_name)
                sub_category.parent = vat_main
                sub_category.save()
                self.stdout.write(f'Updated {sub_category.display_name}')
            except NotificationCategory.DoesNotExist:
                self.stdout.write(f'Category {sub_name} not found')
        
        self.stdout.write(self.style.SUCCESS('Successfully restructured VAT categories!'))