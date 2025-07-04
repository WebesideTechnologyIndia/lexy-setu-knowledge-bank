# management/commands/populate_links.py
# Run with: python manage.py populate_links

from django.core.management.base import BaseCommand
from links.models import Category, SubCategory, Link

class Command(BaseCommand):
    help = 'Populate database with sample link data'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with links...')
        
        # Create Categories
        quick_links, created = Category.objects.get_or_create(
            name='Quick Links',
            slug='quick-links',
            defaults={'order': 1}
        )
        
        important_links, created = Category.objects.get_or_create(
            name='Important Links',
            slug='important-links',
            defaults={'order': 2}
        )
        
        gst_links, created = Category.objects.get_or_create(
            name='GST/VAT Links',
            slug='gst-vat-links',
            defaults={'order': 3}
        )
        
        # Create SubCategories for Quick Links
        income_tax, created = SubCategory.objects.get_or_create(
            category=quick_links,
            name='Income Tax',
            slug='income-tax',
            defaults={'order': 1}
        )
        
        service_tax, created = SubCategory.objects.get_or_create(
            category=quick_links,
            name='Service Tax/ Excise',
            slug='service-tax-excise',
            defaults={'order': 2}
        )
        
        mca, created = SubCategory.objects.get_or_create(
            category=quick_links,
            name='Ministry of Corporate Affairs',
            slug='ministry-of-corporate-affairs',
            defaults={'order': 3}
        )
        
        esi, created = SubCategory.objects.get_or_create(
            category=quick_links,
            name="The Employees' State Insurance",
            slug='employees-state-insurance',
            defaults={'order': 4}
        )
        
        pf, created = SubCategory.objects.get_or_create(
            category=quick_links,
            name='Provident Fund',
            slug='provident-fund',
            defaults={'order': 5}
        )
        
        delhi_vat, created = SubCategory.objects.get_or_create(
            category=quick_links,
            name='Delhi VAT',
            slug='delhi-vat',
            defaults={'order': 6}
        )
        
        # Income Tax Links
        income_tax_links = [
            ('E-payment of Taxes', 'https://onlineservices.tin.egov-nsdl.com/etaxnew/tdsnontds.jsp'),
            ('Income Tax Assessee Login', 'https://www.incometax.gov.in/iec/foportal/'),
            ('Verify PAN (from Name & DOB)', 'https://www1.incometax.gov.in/e-filing/services/panverification.html'),
            ('Status of Tax Refund', 'https://tin.tin.nsdl.com/oltas/servlet/RefundStatus'),
            ('ITR-V Receipt Status', 'https://incometaxindiaefiling.gov.in/e-Filing/UserLogin/LoginHome.html'),
            ('Know Your AO', 'https://incometaxindiaefiling.gov.in/e-Filing/Services/KnowYourAoLink.html'),
            ('Online New PAN Application/ Correction of PAN', 'https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html'),
            ('TAN Login', 'https://incometaxindiaefiling.gov.in/e-Filing/UserLogin/LoginHome.html'),
            ('OLTAS Challan Status', 'https://tin.tin.nsdl.com/oltas/servlet/TaxPayerLogin'),
            ('Verify Form 16A', 'https://incometaxindiaefiling.gov.in/e-Filing/Services/Form16aLogin.html'),
            ('Verify Form 16', 'https://incometaxindiaefiling.gov.in/e-Filing/Services/Form16Login.html'),
            ('Know TAN', 'https://incometaxindiaefiling.gov.in/e-Filing/Services/KnowYourTanLink.html'),
        ]
        
        for i, (title, url) in enumerate(income_tax_links):
            Link.objects.get_or_create(
                subcategory=income_tax,
                title=title,
                defaults={'url': url, 'order': i+1}
            )
        
        # Service Tax Links
        service_tax_links = [
            ('E-payment of Service Tax/ Excise', 'https://www.aces.gov.in/excise/'),
            ('Know Challan Status', 'https://www.aces.gov.in/excise/'),
            ('Assessee Search (Code based)', 'https://www.aces.gov.in/excise/'),
            ('Assessee Login', 'https://www.aces.gov.in/excise/'),
        ]
        
        for i, (title, url) in enumerate(service_tax_links):
            Link.objects.get_or_create(
                subcategory=service_tax,
                title=title,
                defaults={'url': url, 'order': i+1}
            )
        
        # MCA Links
        mca_links = [
            ('Verify Co. Master Data', 'http://www.mca.gov.in/mcafoportal/companyLLPMasterData.do'),
            ('Find CIN', 'http://www.mca.gov.in/mcafoportal/findCIN.do'),
            ('Check Co./LLP Name', 'http://www.mca.gov.in/mcafoportal/checkCompanyName.do'),
            ('View Public Documents', 'http://www.mca.gov.in/mcafoportal/viewPublicDocuments.do'),
            ('Calculate Fee', 'http://www.mca.gov.in/mcafoportal/calculateFees.do'),
            ('Verify DIN-PAN Details of Directors', 'http://www.mca.gov.in/mcafoportal/verifyDINPAN.do'),
        ]
        
        for i, (title, url) in enumerate(mca_links):
            Link.objects.get_or_create(
                subcategory=mca,
                title=title,
                defaults={'url': url, 'order': i+1}
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with links!')
        )