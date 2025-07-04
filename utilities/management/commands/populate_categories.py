# utilities/management/commands/populate_categories.py

from django.core.management.base import BaseCommand
from utilities.models import Category

class Command(BaseCommand):
    help = 'Populate the database with initial categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting category population...'))
        
        categories_data = [
            # Tax and Legal Categories
            {'name': 'rates_of_tds', 'display_name': 'Rates of TDS'},
            {'name': 'tds_rates_nri', 'display_name': 'TDS Rates of N.R.I us 195'},
            {'name': 'rates_of_income_tax', 'display_name': 'Rates of Income Tax'},
            {'name': 'depreciation_rates_companies_act', 'display_name': 'Depreciation Rates Companies Act'},
            {'name': 'depreciation_rates_income_tax_act', 'display_name': 'Depreciation Rates Income Tax Act'},
            {'name': 'roc_filing_fees_cos_act_2013', 'display_name': 'ROC Filing Fees (Cos Act. 2013)'},
            {'name': 'roc_fee_structure_cos_act_2013', 'display_name': 'ROC Fee Structure (Cos Act. 2013)'},
            {'name': 'cost_inflation_index', 'display_name': 'Cost Inflation Index'},
            {'name': 'ifsc_codes', 'display_name': 'IFSC Codes'},
            {'name': 'micr_codes', 'display_name': 'MICR Codes'},
            {'name': 'rates_of_nsc_interest', 'display_name': 'Rates of NSC Interest'},
            {'name': 'gold_and_silver_rates', 'display_name': 'Gold and Silver Rates'},
            {'name': 'rates_of_stamp_duty', 'display_name': 'Rates of Stamp Duty'},
            {'name': 'llp_fees', 'display_name': 'LLP Fees'},
            {'name': 'national_industries_classification', 'display_name': 'National Industries Classification'},
            {'name': 'hsn_rate_list', 'display_name': 'HSN Rate List'},
            {'name': 'deduction_80tta_vs_80ttb', 'display_name': 'Deduction u/s 80TTA Vs 80TTB'},
        ]
        
        created_count = 0
        existing_count = 0
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'display_name': cat_data['display_name'],
                    'is_active': True,
                    'description': f"Information and utilities related to {cat_data['display_name']}"
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created category: {category.display_name}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Category already exists: {category.display_name}')
                )
                existing_count += 1
        
        # Create subcategories
        subcategories_data = [
            {
                'parent_name': 'rates_of_tds',
                'subcategories': [
                    {'name': 'tds_on_salary', 'display_name': 'TDS on Salary'},
                    {'name': 'tds_on_professional_fees', 'display_name': 'TDS on Professional Fees'},
                    {'name': 'tds_on_commission', 'display_name': 'TDS on Commission'},
                ]
            },
            {
                'parent_name': 'rates_of_income_tax',
                'subcategories': [
                    {'name': 'individual_tax_rates', 'display_name': 'Individual Tax Rates'},
                    {'name': 'corporate_tax_rates', 'display_name': 'Corporate Tax Rates'},
                    {'name': 'huf_tax_rates', 'display_name': 'HUF Tax Rates'},
                ]
            },
        ]
        
        self.stdout.write('\n📁 Creating subcategories...')
        
        for parent_data in subcategories_data:
            try:
                parent_category = Category.objects.get(name=parent_data['parent_name'])
                
                for subcat_data in parent_data['subcategories']:
                    subcategory, created = Category.objects.get_or_create(
                        name=subcat_data['name'],
                        defaults={
                            'display_name': subcat_data['display_name'],
                            'parent': parent_category,
                            'is_active': True,
                            'description': f"Subcategory of {parent_category.display_name}"
                        }
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Created subcategory: {subcategory.display_name} (under {parent_category.display_name})')
                        )
                        created_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ℹ️  Subcategory already exists: {subcategory.display_name}')
                        )
                        existing_count += 1
                        
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Parent category "{parent_data["parent_name"]}" not found')
                )
        
        # Summary
        total_categories = Category.objects.count()
        main_categories = Category.objects.filter(parent=None).count()
        subcategories = Category.objects.filter(parent__isnull=False).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Categories setup complete!')
        )
        self.stdout.write(f'📊 Total categories: {total_categories}')
        self.stdout.write(f'📋 Main categories: {main_categories}')
        self.stdout.write(f'📂 Subcategories: {subcategories}')
        self.stdout.write(f'✨ Created: {created_count}, Already existed: {existing_count}')