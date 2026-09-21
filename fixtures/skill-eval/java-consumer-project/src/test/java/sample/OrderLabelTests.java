package sample;

import sample.dal.OrderRow;
import sample.dal.mapper.OrderMapper;
import sample.face.OrderService;
import sample.service.impl.OrderServiceImpl;

public final class OrderLabelTests {

    public static void main(String[] args) {
        testEnabledLabelIsTrimmed();
        testMissingOrderReturnsEmpty();
        System.out.println("OrderLabelTests passed");
    }

    private static void testEnabledLabelIsTrimmed() {
        OrderMapper orderMapper = id -> new OrderRow("  example  ", true);
        OrderService orderService = new OrderServiceImpl(orderMapper);
        assertEquals("example", orderService.getOrderLabel(1L));
    }

    private static void testMissingOrderReturnsEmpty() {
        OrderMapper orderMapper = id -> null;
        OrderService orderService = new OrderServiceImpl(orderMapper);
        assertEquals("", orderService.getOrderLabel(2L));
    }

    private static void assertEquals(String expected, String actual) {
        if (!expected.equals(actual)) {
            throw new AssertionError("expected=" + expected + ", actual=" + actual);
        }
    }
}
