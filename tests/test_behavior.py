"""Behavior and boundary tests for the order desk safety net (Assignment 2, Task 2)."""

from pathlib import Path
import tempfile
import unittest

from supplydesk.service import OrderService


class OrderBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "state.json"
        self.service = OrderService(self.path)

    # ---------- Normal behavior ----------
    def test_regular_pickup_two_notebooks(self):
        q = self.service.quote("regular", [{"product_id": "notebook", "quantity": 2}])
        self.assertEqual(
            (q["subtotal_cents"], q["discount_cents"], q["delivery_cents"], q["total_cents"]),
            (1000, 0, 0, 1000),
        )

    def test_student_delivery_two_hoodies(self):
        q = self.service.quote("student", [{"product_id": "hoodie", "quantity": 2}], "delivery")
        self.assertEqual(
            (q["discount_cents"], q["delivery_cents"], q["total_cents"]),
            (800, 600, 7800),
        )

    def test_quote_and_order_pricing_agree(self):
        items = [{"product_id": "mug", "quantity": 2}]
        q = self.service.quote("student", items, "delivery")
        o = self.service.place_order("student", items, "delivery")
        for key in ("subtotal_cents", "discount_cents", "delivery_cents", "total_cents"):
            self.assertEqual(q[key], o[key], f"mismatch on {key}")

    # ---------- Boundary behavior ----------
    def test_delivery_free_at_threshold(self):
        # 3 hoodies = 12000 subtotal; net (no discount) = 12000 >= 10000 -> free
        q = self.service.quote("regular", [{"product_id": "hoodie", "quantity": 3}], "delivery")
        self.assertEqual(q["delivery_cents"], 0)
        self.assertEqual(q["total_cents"], 12000)

    def test_student_discount_exactly_at_threshold(self):
        # Spec says "at least 5000" -> 2 bags = 5000. Code uses "> 5000" -> likely 0.
        # Do NOT change expected value; document as a defect.
        q = self.service.quote("student", [{"product_id": "bag", "quantity": 2}])
        self.assertEqual(q["subtotal_cents"], 5000)
        self.assertEqual(q["discount_cents"], 500)  # Expected per spec; may fail -> document

    def test_quantity_lower_bound_one(self):
        q = self.service.quote("regular", [{"product_id": "mug", "quantity": 1}])
        self.assertEqual(q["subtotal_cents"], 1500)

    # ---------- Invalid / exceptional ----------
    def test_invalid_customer(self):
        with self.assertRaises(ValueError):
            self.service.quote("vip", [{"product_id": "notebook", "quantity": 1}])

    def test_invalid_fulfillment(self):
        with self.assertRaises(ValueError):
            self.service.quote("regular", [{"product_id": "notebook", "quantity": 1}], "teleport")

    def test_empty_items(self):
        with self.assertRaises(ValueError):
            self.service.quote("regular", [])

    def test_boolean_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.service.quote("regular", [{"product_id": "notebook", "quantity": True}])

    def test_unknown_product(self):
        with self.assertRaises(ValueError):
            self.service.quote("regular", [{"product_id": "rocket", "quantity": 1}])

    def test_quantity_over_stock(self):
        with self.assertRaises(ValueError):
            self.service.place_order("regular", [{"product_id": "hoodie", "quantity": 6}])

    def test_unknown_order(self):
        with self.assertRaises(ValueError):
            self.service.get_order("ORD-9999")

    def test_invalid_request_does_not_change_state(self):
        before_orders = self.service.list_orders()
        before_catalog = self.service.catalog()
        with self.assertRaises(ValueError):
            self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}], "teleport")
        self.assertEqual(self.service.list_orders(), before_orders)
        self.assertEqual(self.service.catalog(), before_catalog)

    # ---------- Behavior important to preserve ----------
    def test_duplicate_lines_checked_against_combined_stock(self):
        with self.assertRaises(ValueError):
            self.service.place_order(
                "regular",
                [
                    {"product_id": "hoodie", "quantity": 3},
                    {"product_id": "hoodie", "quantity": 3},
                ],
            )

    def test_order_ids_monotonic_across_cancel(self):
        o1 = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}])
        self.service.cancel_order(o1["order_id"])
        o2 = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}])
        self.assertEqual(o1["order_id"], "ORD-0001")
        self.assertEqual(o2["order_id"], "ORD-0002")

    def test_cancelled_orders_kept_in_history(self):
        o = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}])
        self.service.cancel_order(o["order_id"])
        ids = [x["order_id"] for x in self.service.list_orders()]
        self.assertIn(o["order_id"], ids)

    def test_cancel_twice_idempotent(self):
        o = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}])
        self.service.cancel_order(o["order_id"])
        stock_after_first = self.service.catalog()
        again = self.service.cancel_order(o["order_id"])
        self.assertEqual(again["status"], "cancelled")
        self.assertEqual(self.service.catalog(), stock_after_first)

    def test_saved_order_reopened_matches(self):
        o = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}])
        reopened = OrderService(self.path).get_order(o["order_id"])
        self.assertEqual(reopened, o)


if __name__ == "__main__":
    unittest.main()