from django.template.loader import get_template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Category, Product


class TemplateLoadingTests(SimpleTestCase):
    def test_all_templates_can_be_loaded(self):
        template_names = (
            'main/base.html',
            'main/home_content.html',
            'main/catalog.html',
            'main/catalog_page.html',
            'main/filter_modal.html',
            'main/search_button.html',
            'main/search_input.html',
            'main/product_detail.html',
            'main/product_detail_page.html',
        )

        for template_name in template_names:
            with self.subTest(template=template_name):
                self.assertIsNotNone(get_template(template_name))


class PageRenderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Jackets', slug='jackets')
        cls.product = Product.objects.create(
            name='Test jacket',
            slug='test-jacket',
            category=cls.category,
            color='Black',
            price='100.00',
            description='Test description',
            main_image='products/main/test.jpg',
        )

    def test_catalog_full_page(self):
        response = self.client.get(reverse('main:catalog_all'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/catalog_page.html')
        self.assertContains(response, self.product.name)

    def test_catalog_htmx_fragment(self):
        response = self.client.get(
            reverse('main:catalog_all'),
            headers={'HX-Request': 'true'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/catalog.html')

    def test_search_input_htmx_fragment(self):
        response = self.client.get(
            reverse('main:catalog_all'),
            {'show_search': 'true'},
            headers={'HX-Request': 'true'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search_input.html')

    def test_catalog_search_and_filters(self):
        response = self.client.get(
            reverse('main:catalog_all'),
            {
                'q': 'jacket',
                'color': 'black',
                'min_price': '50',
                'max_price': '150',
            },
            headers={'HX-Request': 'true'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_detail_full_page(self):
        response = self.client.get(
            reverse('main:product_detail', kwargs={'slug': self.product.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product_detail_page.html')
        self.assertContains(response, self.product.name.upper())

    def test_product_detail_htmx_fragment(self):
        response = self.client.get(
            reverse('main:product_detail', kwargs={'slug': self.product.slug}),
            headers={'HX-Request': 'true'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product_detail.html')
