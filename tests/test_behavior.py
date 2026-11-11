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
        q = self.service.quote("regular", [{"product_id": "hoodie", "quantity": 3}], "delivery")
        self.assertEqual(q["delivery_cents"], 0)
        self.assertEqual(q["total_cents"], 12000)

    def test_student_discount_exactly_at_threshold(self):
        q = self.service.quote("student", [{"product_id": "bag", "quantity": 2}])
        self.assertEqual(q["subtotal_cents"], 5000)
        self.assertEqual(q["discount_cents"], 500)

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


class ExpressDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "state.json"
        self.service = OrderService(self.path)

    def test_express_regular_two_notebooks(self):
        q = self.service.quote("regular", [{"product_id": "notebook", "quantity": 2}], "express")
        self.assertEqual((q["delivery_cents"], q["total_cents"]), (1200, 2200))

    def test_express_student_two_hoodies(self):
        q = self.service.quote("student", [{"product_id": "hoodie", "quantity": 2}], "express")
        self.assertEqual((q["discount_cents"], q["delivery_cents"], q["total_cents"]), (800, 1200, 8400))

    def test_express_never_waived_above_standard_threshold(self):
        q = self.service.quote("regular", [{"product_id": "hoodie", "quantity": 3}], "express")
        self.assertEqual((q["delivery_cents"], q["total_cents"]), (1200, 13200))

    def test_express_order_matches_quote_and_survives_reload(self):
        items = [{"product_id": "hoodie", "quantity": 2}]
        q = self.service.quote("student", items, "express")
        o = self.service.place_order("student", items, "express")
        for key in ("fulfillment", "items", "discount_cents", "delivery_cents", "total_cents"):
            self.assertEqual(q[key], o[key], f"mismatch on {key}")
        reopened = OrderService(self.path).get_order(o["order_id"])
        self.assertEqual(reopened, o)

    def test_express_cancel_restores_stock_and_keeps_record(self):
        before = self.service.catalog()
        o = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}], "express")
        c = self.service.cancel_order(o["order_id"])
        self.assertEqual(c["status"], "cancelled")
        self.assertEqual(c["fulfillment"], "express")
        self.assertEqual(c["delivery_cents"], 1200)
        self.assertEqual(self.service.catalog(), before)


if __name__ == "__main__":
    unittest.main()