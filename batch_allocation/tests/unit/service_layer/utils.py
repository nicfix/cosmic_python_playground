from batch_allocation.domain.model import Product
from batch_allocation.tests.unit.fixtures import MockedRepository
from batch_allocation.tests.unit.test_domain import create_batch


def init_product_repository(sku, purchased_quantity, batches_number) -> MockedRepository:
    batches = [create_batch(sku, purchased_quantity) for i in range(0, batches_number)]
    product = Product(sku, batches)
    return MockedRepository((product,))