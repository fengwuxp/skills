package skillcheck;

import sample.dal.OrderRow;
import sample.dal.mapper.OrderMapper;
import sample.face.OrderService;
import sample.service.impl.OrderServiceImpl;
import sample.web.OrderController;

import java.util.HashMap;
import java.util.Map;

/** 使用真实 Controller 查询四种存储输入，验证调用者得到的订单名称。 */
public final class OrderEntryCheck {

    public static void main(String[] args) throws ReflectiveOperationException {
        Map<Long, OrderRow> rows = new HashMap<>();
        rows.put(1L, new OrderRow("  example  ", true));
        rows.put(2L, new OrderRow("inactive", false));
        rows.put(3L, new OrderRow(null, true));
        OrderController controller = createController(rows::get);

        assertLabel(controller, 1L, "启用订单名称去掉两端空白", "example");
        assertLabel(controller, 2L, "停用订单", "");
        assertLabel(controller, 3L, "订单名称为空", "");
        assertLabel(controller, 4L, "订单不存在", "");
        System.out.println("PASS OrderController.getOrderLabel (4 cases)");
    }

    /** 按样本实际公开的构造器装配；兼容旧入口，以便错误能在业务断言处复现。 */
    private static OrderController createController(OrderMapper mapper) throws ReflectiveOperationException {
        try {
            return OrderController.class.getConstructor(OrderService.class).newInstance(new OrderServiceImpl(mapper));
        } catch (NoSuchMethodException missingServiceConstructor) {
            return OrderController.class.getConstructor(OrderMapper.class).newInstance(mapper);
        }
    }

    private static void assertLabel(OrderController controller, long id, String scenario, String expected) {
        String actual = controller.getOrderLabel(id);
        if (!expected.equals(actual)) {
            throw new AssertionError("OrderController.getOrderLabel — " + scenario
                    + "，期望 [" + expected + "]，实际 [" + actual + "]");
        }
    }
}
